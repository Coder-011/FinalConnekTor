# core/login.py
import time
import threading
import requests
import urllib3
from kivy.clock import Clock

# Suppress InsecureRequestWarning — portal uses self-signed cert
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ── PORTAL CONSTANTS (extracted verbatim from APK bytecode) ────────────────
LOGIN_URL   = 'https://10.100.1.1:8090/login.xml'
REFERER     = 'https://10.100.1.1:8090/'
MODE        = '191'
PRODUCTTYPE = 'your_producttype'   # literal string from binary — do not change
USER_AGENT  = (
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
    'AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/58.0.3029.110 Safari/537.3'
)
SUCCESS_STRING = 'You are signed in as'  # portal response on success

def perform_login(username: str, password: str, result_callback):
    """
    Fires a POST to the captive portal login endpoint.
    Runs in a daemon thread — never call this directly on the main thread.

    result_callback(status: str, message: str) — called via Clock.schedule_once
    status is one of: 'connected', 'failed', 'error'
    message is a human-readable string for the UI status badge.
    """
    def _worker():
        # Fresh timestamp on EVERY call — prevents replay rejection
        timestamp = int(time.time() * 1000)

        payload = {
            'mode':        MODE,
            'username':    username,
            'password':    password,
            'a':           timestamp,
            'producttype': PRODUCTTYPE,
        }

        # Manual URL-encoding — exactly as the original APK does it.
        # Do NOT replace with data=payload in requests.post.
        payload_encoded = '&'.join([
            f'{k}={requests.utils.quote(str(v))}'
            for k, v in payload.items()
        ])

        headers = {
            'User-Agent':   USER_AGENT,
            'Content-Type': 'application/x-www-form-urlencoded',
            'Referer':      REFERER,
        }

        # Retry loop — up to 2 attempts on Timeout
        for attempt in range(2):
            try:
                response = requests.post(
                    LOGIN_URL,
                    data=payload_encoded,
                    headers=headers,
                    verify=False,    # portal has self-signed cert
                    timeout=10,
                )

                if SUCCESS_STRING in response.text:
                    Clock.schedule_once(
                        lambda dt: result_callback('connected', 'Connected'), 0
                    )
                else:
                    Clock.schedule_once(
                        lambda dt: result_callback('failed', 'Login Failed'), 0
                    )
                return

            except requests.exceptions.Timeout:
                if attempt == 0:
                    # Refresh timestamp and retry once
                    time.sleep(2)
                    timestamp = int(time.time() * 1000)
                    payload['a'] = timestamp
                    payload_encoded = '&'.join([
                        f'{k}={requests.utils.quote(str(v))}'
                        for k, v in payload.items()
                    ])
                    continue
                Clock.schedule_once(
                    lambda dt: result_callback('failed', 'Timed Out'), 0
                )
                return

            except requests.exceptions.ConnectionError:
                Clock.schedule_once(
                    lambda dt: result_callback('error', 'No Network'), 0
                )
                return

            except requests.exceptions.RequestException as e:
                msg = str(e)[:40]
                Clock.schedule_once(
                    lambda dt: result_callback('error', f'Error: {msg}'), 0
                )
                return

    t = threading.Thread(target=_worker, daemon=True)
    t.start()
