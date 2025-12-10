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
