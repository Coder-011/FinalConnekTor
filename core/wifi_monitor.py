# core/wifi_monitor.py
import threading
import time
import requests
from kivy.clock import Clock

POLL_INTERVAL  = 8    # seconds between probes
COOLDOWN       = 30   # seconds between auto-login attempts
PORTAL_HOST    = '10.100.1.1'
PROBE_URL      = 'http://captive.apple.com'   # plain HTTP — portals intercept this


class WiFiMonitor:
    """
    Background probe thread. Polls every POLL_INTERVAL seconds.
    When it detects the campus captive portal (redirect to 10.100.1.1),
    it fires login_callback on the main thread via Clock.schedule_once.

    Reads get_enabled() on every cycle — toggle changes take effect immediately
    without restarting the thread.

    Only one thread runs at a time. Calling start() when already running
    is a no-op.
    """

    def __init__(self, login_callback, get_enabled):
        self._running         = False
        self._thread          = None
        self._login_callback  = login_callback   # called on main thread
        self._get_enabled     = get_enabled      # () -> bool
        self._last_attempt    = 0

    def start(self):
        if self._thread and self._thread.is_alive():
            return
        self._running = True
        self._thread  = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False

    def _run(self):
        while self._running:
            time.sleep(POLL_INTERVAL)
            if not self._running:
                break
            if not self._get_enabled():
                continue
            if time.time() - self._last_attempt < COOLDOWN:
                continue
            try:
                self._probe()
            except Exception:
                pass   # never let the monitor thread crash

    def _probe(self):
        try:
            r = requests.get(
                PROBE_URL,
                timeout=5,
                allow_redirects=True,
                verify=False,
            )
            if PORTAL_HOST in r.url or PORTAL_HOST in r.text:
                self._last_attempt = time.time()
                Clock.schedule_once(lambda dt: self._login_callback(), 0)
        except (requests.exceptions.ConnectionError,
                requests.exceptions.Timeout):
            pass
