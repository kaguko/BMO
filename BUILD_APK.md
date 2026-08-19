# 📱 Hướng dẫn Build APK Android cho BMO

## Tổng quan

BMO sử dụng **pygame** + **python-for-android** + **Buildozer** để build APK Android.  
Toàn bộ quá trình build chạy **miễn phí** trên **GitHub Actions** (cloud Ubuntu VM).

---

## Cách 1: Build APK tự động qua GitHub Actions *(Khuyên dùng)*

### Bước 1: Tạo GitHub Repository

1. Đăng nhập [github.com](https://github.com) → **New Repository**
2. Tên repo: `bmo-adventure-time` (hoặc tùy ý)
3. Chọn **Public** (miễn phí GitHub Actions)

### Bước 2: Push code lên GitHub

Mở Terminal trong thư mục `E:\BMO` và chạy:

```powershell
git init
git add .
git commit -m "🤖 BMO Adventure Time - Initial release"
git branch -M main
git remote add origin https://github.com/TÊN_USER/bmo-adventure-time.git
git push -u origin main
```

> Thay `TÊN_USER` bằng username GitHub của bạn.

### Bước 3: Kích hoạt build

- Mỗi lần push code → **GitHub Actions tự động chạy build** (~20-40 phút)
- Hoặc vào tab **Actions** → chọn **"🤖 Build BMO Android APK"** → **Run workflow**

### Bước 4: Tải APK về

1. Vào **Actions** → Click vào build mới nhất đã thành công ✅
2. Cuộn xuống phần **Artifacts**
3. Tải file **`BMO-Adventure-Time-APK.zip`**
4. Giải nén → có file `.apk`

---

## Cách 2: Build trên máy local (WSL2/Ubuntu)

Yêu cầu: Đã cài **WSL2** với Ubuntu 22.04

```bash
# Cài đặt dependencies
sudo apt-get update && sudo apt-get install -y \
    python3-pip openjdk-17-jdk build-essential \
    libffi-dev libssl-dev zlib1g-dev autoconf libtool \
    espeak libespeak-dev

# Cài buildozer
pip3 install buildozer==1.5.0 cython==0.29.37

# Build APK debug
cd /mnt/e/BMO
buildozer android debug

# APK xuất ra:
ls bin/*.apk
```

---

## Cài đặt APK lên điện thoại

### Cách A: Cài trực tiếp (ADB)

```powershell
# Bật Developer Mode + USB Debugging trên điện thoại
adb install bin\bmo-adventure-time-1.0.0-debug.apk
```

### Cách B: Copy file APK

1. Copy file `.apk` vào điện thoại qua USB hoặc Google Drive
2. Trên điện thoại: Bật **"Cài từ nguồn không xác định"**
3. Mở file `.apk` → Cài đặt

---

## Điều khiển trên Mobile (Cảm ứng)

| Hành động | Điều khiển |
|-----------|------------|
| **Menu chính** | Nút `☰` dưới màn hình |
| **Chat với BMO** | Nút `💬` dưới màn hình |
| **Game 1 - Runner** | Nút `1` dưới màn hình |
| **Game 2 - Bug Invaders** | Nút `2` dưới màn hình |
| **Game 3 - Simon** | Nút `3` dưới màn hình |
| **Game 4 - Rainicorn** | Nút `4` dưới màn hình |
| **Vuốt trán BMO** | Thả ra cảm xúc vui vẻ |
| **Chạy - Nhảy** | Chạm bên trái màn hình |
| **Runner - BMO CHOP!** | Chạm bên phải màn hình |
| **Bug Invaders - Bắn** | Kéo/giữ để điều khiển tàu |
| **Flappy - Bay** | Tap để vỗ cánh |
| **Simon** | Tap vào 4 nút màu |

---

## Thông số APK

| Thuộc tính | Giá trị |
|------------|---------|
| Android API | 33 (Android 13+) |
| Min Android | 26 (Android 8.0+) |
| Kiến trúc | arm64-v8a |
| Màn hình | Fullscreen Portrait |
| Độ phân giải | 480 × 854 |
| TTS | espeak (offline) |
| Size dự kiến | ~30-50 MB |

---

## Lưu ý

> **pyttsx3 SAPI5** (Windows TTS) không hoạt động trên Android.  
> BMO tự động chuyển sang **espeak** (cài sẵn trong APK) khi chạy trên Android.  
> Giọng espeak khác giọng Zira trên Windows nhưng vẫn pitch-shifted giống BMO.
