[app]

# عنوان برنامه
title = جورچین تجهیزات پدافند

# نام فایل اصلی (الزامی)
source.dir = main.py
source.include_exts = py,png,jpg,jpeg,gif,atlas,ttf,mp3,wav

# نام بسته (package)
package.name = جورچین تجهیزات پدافند
package.domain = ir.mohsen.puzzle

# نسخه
version = 1.0

# مشخصات توسعه‌دهنده
author = Mohsen Zare
author.email = mohsen2014za@gmail.com
author.website =

# فایل اصلی
source.main = main.py

# گرافیک (آیکون و لانچر — اختیاری)
# icon.filename = icon.png
# presplash.filename = presplash.png

# گزینه‌های اضافه (log, fullscreen و ...)
fullscreen = 1
android.logcat_filters = *:S python:D

[buildozer]

# دایرکتوری خروجی
log_level = 2
warn_on_root = 1

[build]

# فشرده‌سازی
build_mode = debug

[app]

# اجازه دسترسی به صدا و ذخیره‌سازی (در صورت نیاز)
# android.permissions = WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE

# کتابخانه‌های مورد نیاز
requirements = python3,kivy==2.2.1, pillow, android

# تنظیمات پلتفرم
android.api = 31
android.minapi = 21
android.ndk = 25b
android.gradle_dependencies = 'com.google.android.gms:play-services-location:21.0.1'

# نام نمایشی در لانچر
android.name = Puzzle IQ

# بسته کامل (package ID)
android.package = ir.mohsen.puzzle.puzzleiq

# نسخه‌های مورد نیاز
android.sdk = 26
p4a.branch = develop