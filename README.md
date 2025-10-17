# AI Car Agent - Tư vấn mua xe thông minh

Một ứng dụng AI chatbot tư vấn mua xe với giao diện chat hiện đại, tích hợp Google Maps API và email service.

## 🚀 Tính năng

- **AI Chatbot**: Tư vấn xe dựa trên ngân sách và yêu cầu người dùng
- **So sánh xe**: Đưa ra 3 mẫu xe phù hợp và so sánh chi tiết
- **Tìm showroom**: Sử dụng Google Maps API để tìm showroom gần nhất
- **Gửi báo giá**: Tích hợp SendGrid để gửi email báo giá đẹp mắt
- **Đăng ký lái thử**: Quản lý lịch test drive
- **Giao diện hiện đại**: React với styled-components
- **Deploy dễ dàng**: Docker + CI/CD với GitHub Actions

## 🏗️ Kiến trúc

```
├── backend/           # Flask API server
│   └── app.py        # Main application
├── frontend/          # React frontend
│   ├── src/
│   └── package.json
├── tests/            # Unit tests
├── docker-compose.yml
├── Dockerfile
└── .github/workflows/ # CI/CD pipeline
```

## 🛠️ Cài đặt

### Yêu cầu hệ thống

- Python 3.9+
- Node.js 18+
- PostgreSQL 13+
- Docker & Docker Compose (tùy chọn)

### 1. Clone repository

```bash
git clone <repository-url>
cd car-agent
```

### 2. Cài đặt Backend

```bash
# Tạo virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# hoặc
venv\Scripts\activate     # Windows

# Cài đặt dependencies
pip install -r requirements.txt
```

### 3. Cài đặt Frontend

```bash
cd frontend
npm install
```

### 4. Cấu hình Environment Variables

Tạo file `.env` từ `env.example`:

```bash
cp env.example .env
```

Cập nhật các biến môi trường:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/car_agent_db

# API Keys
OPENAI_API_KEY=your-openai-api-key
GOOGLE_MAPS_API_KEY=your-google-maps-api-key
SENDGRID_API_KEY=your-sendgrid-api-key

# Flask
SECRET_KEY=your-secret-key
```

### 5. Khởi tạo Database

```bash
# Tạo database PostgreSQL
createdb car_agent_db

# Chạy migration (nếu có)
flask db upgrade
```

## 🚀 Chạy ứng dụng

### Development Mode

```bash
# Terminal 1: Backend
cd backend
python app.py

# Terminal 2: Frontend
cd frontend
npm start
```

Truy cập: http://localhost:3000

### Docker Mode

```bash
# Chạy tất cả services
docker-compose up -d

# Xem logs
docker-compose logs -f
```

## 📱 Sử dụng

1. **Tư vấn xe**: Nhập yêu cầu như "Tôi muốn mua xe dưới 1 tỷ"
2. **So sánh xe**: AI sẽ đưa ra 3 mẫu xe và so sánh
3. **Chọn xe**: Chọn xe bạn quan tâm
4. **Nhập email**: Để nhận báo giá chi tiết
5. **Tìm showroom**: AI tìm showroom gần bạn
6. **Đăng ký lái thử**: Đặt lịch test drive

## 🔧 API Endpoints

### Chat
- `POST /api/chat` - Gửi tin nhắn cho AI agent

### Cars
- `GET /api/cars` - Lấy danh sách xe

### Showrooms
- `GET /api/showrooms` - Lấy danh sách showroom
- `POST /api/nearby-showrooms` - Tìm showroom gần nhất

### Email & Test Drive
- `POST /api/send-quote` - Gửi báo giá qua email
- `POST /api/schedule-test-drive` - Đăng ký lái thử

### Health
- `GET /api/health` - Kiểm tra trạng thái API

## 🚀 Deploy

### 1. Deploy Backend (Railway/Render)

#### Railway
```bash
# Cài đặt Railway CLI
npm install -g @railway/cli

# Login và deploy
railway login
railway init
railway up
```

#### Render
1. Kết nối GitHub repository
2. Chọn "Web Service"
3. Cấu hình:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
   - Environment Variables: Thêm tất cả biến từ `.env`

### 2. Deploy Frontend (Vercel/Netlify)

#### Vercel
```bash
# Cài đặt Vercel CLI
npm install -g vercel

# Deploy
cd frontend
vercel --prod
```

#### Netlify
1. Kết nối GitHub repository
2. Build settings:
   - Build command: `npm run build`
   - Publish directory: `build`
   - Environment variables: `REACT_APP_API_URL`

### 3. Database (PostgreSQL)

#### Railway Database
```bash
railway add postgresql
```

#### Render Database
1. Tạo PostgreSQL service
2. Copy connection string vào `DATABASE_URL`

## 🔐 Bảo mật

### Environment Variables
- Không commit file `.env`
- Sử dụng secrets trong CI/CD
- Rotate API keys định kỳ

### API Security
- Rate limiting
- CORS configuration
- Input validation
- SQL injection prevention

### Production Checklist
- [ ] HTTPS enabled
- [ ] Database credentials secure
- [ ] API keys in environment variables
- [ ] Error handling không expose sensitive info
- [ ] Logging và monitoring

## 🧪 Testing

```bash
# Backend tests
pytest tests/

# Frontend tests
cd frontend
npm test

# Coverage
pytest --cov=backend tests/
```

## 📊 Monitoring

### Health Checks
- API health endpoint: `/api/health`
- Database connectivity
- External API status

### Logging
- Application logs
- Error tracking
- Performance metrics

## 🔄 CI/CD

GitHub Actions pipeline:
1. **Test**: Chạy unit tests
2. **Build**: Build Docker images
3. **Deploy**: Deploy to production

### Secrets cần thiết:
- `OPENAI_API_KEY`
- `GOOGLE_MAPS_API_KEY`
- `SENDGRID_API_KEY`
- `VERCEL_TOKEN`
- `RAILWAY_TOKEN`

## 🚀 Mở rộng

### Tính năng có thể thêm:
- [ ] Tích hợp OpenAI GPT cho AI agent thông minh hơn
- [ ] Real-time chat với WebSocket
- [ ] Push notifications
- [ ] Mobile app (React Native)
- [ ] Admin dashboard
- [ ] Analytics và reporting
- [ ] Multi-language support
- [ ] Voice chat integration

### Performance Optimization:
- [ ] Redis caching
- [ ] CDN cho static assets
- [ ] Database indexing
- [ ] API response compression
- [ ] Image optimization

## 🤝 Contributing

1. Fork repository
2. Tạo feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push branch: `git push origin feature/amazing-feature`
5. Tạo Pull Request

## 📄 License

MIT License - xem file [LICENSE](LICENSE) để biết thêm chi tiết.

## 📞 Support

- Email: support@caragent.com
- GitHub Issues: [Tạo issue](https://github.com/your-repo/issues)
- Documentation: [Wiki](https://github.com/your-repo/wiki)

---

**Made with ❤️ by AI Car Agent Team**
