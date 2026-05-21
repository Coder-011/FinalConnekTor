[app]
title = ConnekTor
package.name = connektor
package.domain = org.citpc
source.dir = .
source.include_exts = py,kv,json,ttf,otf,png,jpg
version = 4.0.0

requirements = python3,kivy,kivymd,requests,certifi,charset-normalizer,urllib3,idna

# Removed hard pins to allow Buildozer to resolve dependencies automatically
orientation = portrait
fullscreen = 0
android.minapi = 21
android.targetapi = 33
# android.ndk = 25b
# android.sdk_build_tools = 33.0.2
android.accept_sdk_license = True
android.archs = arm64-v8a, armeabi-v7a

android.permissions = INTERNET, ACCESS_WIFI_STATE, CHANGE_WIFI_STATE, ACCESS_NETWORK_STATE, CHANGE_NETWORK_STATE

android.allow_backup = False
android.logcat_filters = *:S python:D

# Presplash color matches app background — avoids white flash on launch
presplash.color = #0D0E1A
icon.filename = %(source.dir)s/assets/icon.png

[buildozer]
log_level = 2
warn_on_root = 1
