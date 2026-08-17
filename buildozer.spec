[app]

# Thông tin ứng dụng
title = BMO Adventure Time
package.name = bmo_adventure_time
package.domain = org.bmoapp

source.dir = .
source.main = main.py
source.include_exts = py,png,jpg,kv,atlas,ttf,wav,ogg,mp3
source.include_patterns = bmo/**/*.py,bmo/**

version = 1.0.0
requirements = python3,pygame,pyttsx3,espeak

# Orientation: portrait cho điện thoại
orientation = portrait
fullscreen = 1

# Android API
android.api = 33
android.minapi = 26
android.ndk = 25b
android.ndk_api = 26
android.accept_sdk_license = True

# Permissions cần thiết
android.permissions = INTERNET,ACCESS_NETWORK_STATE,VIBRATE,RECORD_AUDIO,MODIFY_AUDIO_SETTINGS,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# Màu nền splash screen khi load
android.presplash_color = #8DD5C9

# Icon và splash screen
# android.icon.filename = %(source.dir)s/assets/icon.png
# android.presplash.filename = %(source.dir)s/assets/splash.png

# Cài đặt build
android.arch = arm64-v8a
android.release_artifact = apk

[buildozer]
log_level = 2
warn_on_root = 1
