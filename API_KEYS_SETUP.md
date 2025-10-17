# 🔑 Hướng dẫn cấu hình API Keys

## 📋 Tổng quan

Để sử dụng đầy đủ tính năng của AI Car Agent, bạn cần cấu hình các API keys sau:

## 🔧 Cách cấu hình

### 1. OpenAI API Key (Tùy chọn - cho AI thông minh hơn)

**Mục đích**: Cải thiện khả năng hiểu và phản hồi của AI agent

**Cách lấy**:
1. Truy cập: https://platform.openai.com/
2. Đăng ký/Đăng nhập tài khoản
3. Vào API Keys → Create new secret key
4. Copy key và thay thế trong file `.env`:
   ```
   OPENAI_API_KEY=sk-your-actual-key-here
   ```

**Chi phí**: Có phí theo usage (khoảng $0.002/1K tokens)

### 2. Google Maps API Key (Tùy chọn - cho tìm showroom)

**Mục đích**: Tìm showroom gần nhất dựa trên vị trí người dùng

**Cách lấy**:
1. Truy cập: https://console.cloud.google.com/
2. Tạo project mới hoặc chọn project có sẵn
3. Enable APIs:
   - Places API
   - Maps JavaScript API
   - Geocoding API
4. Tạo API Key: APIs & Services → Credentials → Create Credentials
5. Copy key và thay thế trong file `.env`:
   ```
   GOOGLE_MAPS_API_KEY=AIza-your-actual-key-here
   ```

**Chi phí**: Miễn phí $200/tháng, sau đó có phí

### 3. SendGrid API Key (Tùy chọn - cho gửi email)

**Mục đích**: Gửi email báo giá xe cho khách hàng

**Cách lấy**:
1. Truy cập: https://sendgrid.com/
2. Đăng ký tài khoản miễn phí
3. Vào Settings → API Keys → Create API Key
4. Chọn "Restricted Access" và chỉ enable "Mail Send"
5. Copy key và thay thế trong file `.env`:
   ```
   SENDGRID_API_KEY=SG.your-actual-key-here
   ```

**Chi phí**: Miễn phí 100 emails/ngày

## 🚀 Chạy không cần API Keys

Nếu chưa có API keys, ứng dụng vẫn chạy được với các tính năng cơ bản:

- ✅ Giao diện chat đẹp mắt
- ✅ Tư vấn xe cơ bản (dựa trên database)
- ✅ So sánh xe
- ❌ Tìm showroom gần nhất (cần Google Maps)
- ❌ Gửi email báo giá (cần SendGrid)
- ❌ AI thông minh (cần OpenAI)

## 📝 Cập nhật API Keys

1. **Mở file `.env`** trong thư mục gốc
2. **Thay thế** các placeholder:
   ```
   # Thay đổi từ:
   OPENAI_API_KEY=your-openai-api-key-here
   
   # Thành:
   OPENAI_API_KEY=sk-actual-key-here
   ```
3. **Restart** ứng dụng để áp dụng thay đổi

## 🔒 Bảo mật

- ⚠️ **KHÔNG** commit file `.env` lên Git
- ⚠️ **KHÔNG** chia sẻ API keys
- ⚠️ **KHÔNG** hardcode keys trong source code
- ✅ Sử dụng environment variables
- ✅ Rotate keys định kỳ

## 🆘 Troubleshooting

### Lỗi "Invalid API key"
- Kiểm tra key có đúng format không
- Kiểm tra key có được enable đúng APIs không
- Kiểm tra billing account có được setup không

### Lỗi "Quota exceeded"
- Kiểm tra usage limits
- Upgrade plan nếu cần
- Implement rate limiting

### Lỗi "Permission denied"
- Kiểm tra API permissions
- Kiểm tra domain restrictions
- Kiểm tra IP restrictions

## 📞 Support

Nếu gặp vấn đề:
1. Kiểm tra logs trong console
2. Xem documentation của từng service
3. Tạo issue trên GitHub
4. Liên hệ support team

---

**💡 Tip**: Bắt đầu với SendGrid (miễn phí) để test email, sau đó thêm Google Maps và cuối cùng là OpenAI.


