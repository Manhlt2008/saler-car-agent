# 🚀 Hướng dẫn Deploy AI Car Agent

## 📋 Tổng quan

Hướng dẫn chi tiết để deploy ứng dụng AI Car Agent lên các platform khác nhau.

## 🏗️ Kiến trúc Deploy

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Database      │
│   (Vercel)      │◄──►│   (Railway)     │◄──►│   (PostgreSQL)  │
│   React App     │    │   Flask API     │    │   Railway DB    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🔧 Chuẩn bị

### 1. API Keys cần thiết

#### OpenAI API
```bash
# Đăng ký tại: https://platform.openai.com/
OPENAI_API_KEY=sk-...
```

#### Google Maps API
```bash
# Đăng ký tại: https://console.cloud.google.com/
# Bật APIs: Places API, Maps JavaScript API
GOOGLE_MAPS_API_KEY=AIza...
```

#### SendGrid API
```bash
# Đăng ký tại: https://sendgrid.com/
SENDGRID_API_KEY=SG...
```

### 2. GitHub Secrets

Thêm vào GitHub repository settings:

```
OPENAI_API_KEY=sk-...
GOOGLE_MAPS_API_KEY=AIza...
SENDGRID_API_KEY=SG...
VERCEL_TOKEN=vercel_...
RAILWAY_TOKEN=railway_...
```

## 🚀 Deploy Backend (Railway)

### Bước 1: Chuẩn bị Railway

```bash
# Cài đặt Railway CLI
npm install -g @railway/cli

# Login
railway login
```

### Bước 2: Tạo Project

```bash
# Tạo project mới
railway init

# Thêm PostgreSQL database
railway add postgresql
```

### Bước 3: Cấu hình Environment Variables

```bash
# Thêm các biến môi trường
railway variables set DATABASE_URL=$DATABASE_URL
railway variables set SECRET_KEY=your-secret-key-here
railway variables set OPENAI_API_KEY=$OPENAI_API_KEY
railway variables set GOOGLE_MAPS_API_KEY=$GOOGLE_MAPS_API_KEY
railway variables set SENDGRID_API_KEY=$SENDGRID_API_KEY
railway variables set SENDGRID_FROM_EMAIL=noreply@yourdomain.com
```

### Bước 4: Deploy

```bash
# Deploy backend
railway up
```

### Bước 5: Lấy Backend URL

```bash
# Lấy URL của backend
railway domain
# Ví dụ: https://car-agent-backend-production.up.railway.app
```

## 🌐 Deploy Frontend (Vercel)

### Bước 1: Chuẩn bị Vercel

```bash
# Cài đặt Vercel CLI
npm install -g vercel

# Login
vercel login
```

### Bước 2: Cấu hình Frontend

Tạo file `frontend/.env.production`:

```env
REACT_APP_API_URL=https://car-agent-backend-production.up.railway.app
```

### Bước 3: Deploy

```bash
cd frontend
vercel --prod
```

### Bước 4: Cấu hình Environment Variables trong Vercel

1. Vào Vercel Dashboard
2. Chọn project
3. Settings → Environment Variables
4. Thêm:
   ```
   REACT_APP_API_URL = https://your-backend-url.railway.app
   ```

## 🐳 Deploy với Docker

### Bước 1: Build Images

```bash
# Build backend image
docker build -t car-agent-backend .

# Build frontend image
docker build -t car-agent-frontend ./frontend
```

### Bước 2: Deploy với Docker Compose

```bash
# Chạy production
docker-compose -f docker-compose.prod.yml up -d
```

### Bước 3: Cấu hình Production

Tạo `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  db:
    image: postgres:13
    environment:
      POSTGRES_DB: car_agent_db
      POSTGRES_USER: car_agent_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  backend:
    image: car-agent-backend
    environment:
      DATABASE_URL: postgresql://car_agent_user:${DB_PASSWORD}@db:5432/car_agent_db
      SECRET_KEY: ${SECRET_KEY}
      OPENAI_API_KEY: ${OPENAI_API_KEY}
      GOOGLE_MAPS_API_KEY: ${GOOGLE_MAPS_API_KEY}
      SENDGRID_API_KEY: ${SENDGRID_API_KEY}
    ports:
      - "5000:5000"
    depends_on:
      - db
    restart: unless-stopped

  frontend:
    image: car-agent-frontend
    ports:
      - "3000:3000"
    environment:
      REACT_APP_API_URL: http://localhost:5000
    depends_on:
      - backend
    restart: unless-stopped

volumes:
  postgres_data:
```

## 🔄 CI/CD với GitHub Actions

### Bước 1: Cấu hình Secrets

Thêm vào GitHub repository:

```
OPENAI_API_KEY
GOOGLE_MAPS_API_KEY
SENDGRID_API_KEY
VERCEL_TOKEN
RAILWAY_TOKEN
VERCEL_ORG_ID
VERCEL_PROJECT_ID
```

### Bước 2: Workflow tự động

File `.github/workflows/ci-cd.yml` đã được tạo sẵn:

- **Test**: Chạy unit tests
- **Build**: Build Docker images
- **Deploy Frontend**: Deploy lên Vercel
- **Deploy Backend**: Deploy lên Railway

### Bước 3: Trigger Deploy

```bash
# Push lên main branch sẽ trigger deploy
git push origin main
```

## 🗄️ Database Setup

### Bước 1: Khởi tạo Database

```bash
# Kết nối đến Railway database
railway connect postgresql

# Hoặc sử dụng connection string
psql $DATABASE_URL
```

### Bước 2: Tạo Tables

```sql
-- Database sẽ tự động tạo tables khi chạy app
-- Hoặc chạy migration
flask db upgrade
```

### Bước 3: Seed Data

```python
# Chạy script seed data
python backend/seed_data.py
```

## 🔍 Monitoring & Logs

### Railway Logs

```bash
# Xem logs backend
railway logs

# Xem logs database
railway logs --service postgresql
```

### Vercel Logs

```bash
# Xem logs frontend
vercel logs
```

### Health Checks

```bash
# Kiểm tra backend
curl https://your-backend-url.railway.app/api/health

# Kiểm tra frontend
curl https://your-frontend-url.vercel.app
```

## 🚨 Troubleshooting

### Lỗi thường gặp

#### 1. Database Connection Error
```bash
# Kiểm tra DATABASE_URL
railway variables

# Test connection
railway connect postgresql
```

#### 2. API Key Invalid
```bash
# Kiểm tra API keys
railway variables | grep API_KEY

# Test API
curl -H "Authorization: Bearer $API_KEY" https://api.openai.com/v1/models
```

#### 3. CORS Error
```python
# Kiểm tra CORS config trong backend/app.py
CORS(app, origins=["https://your-frontend-url.vercel.app"])
```

#### 4. Build Error
```bash
# Kiểm tra logs
railway logs --service backend

# Rebuild
railway redeploy
```

### Debug Commands

```bash
# Kiểm tra environment variables
railway variables

# Kiểm tra services
railway status

# Restart service
railway redeploy

# Xem logs real-time
railway logs --follow
```

## 📊 Performance Optimization

### Backend
- Sử dụng Redis cho caching
- Database connection pooling
- API response compression
- Rate limiting

### Frontend
- Code splitting
- Image optimization
- CDN cho static assets
- Service worker caching

### Database
- Indexing
- Query optimization
- Connection pooling
- Read replicas

## 🔐 Security Checklist

### Production Security
- [ ] HTTPS enabled
- [ ] Environment variables secure
- [ ] API keys rotated
- [ ] Database credentials secure
- [ ] CORS properly configured
- [ ] Rate limiting enabled
- [ ] Input validation
- [ ] SQL injection prevention
- [ ] XSS protection
- [ ] CSRF protection

### Monitoring
- [ ] Error tracking (Sentry)
- [ ] Performance monitoring
- [ ] Uptime monitoring
- [ ] Security scanning
- [ ] Log aggregation

## 📈 Scaling

### Horizontal Scaling
- Load balancer
- Multiple backend instances
- Database read replicas
- CDN for static assets

### Vertical Scaling
- Increase server resources
- Database optimization
- Caching strategies
- Code optimization

## 🆘 Support

### Khi gặp vấn đề:
1. Kiểm tra logs
2. Xem GitHub Issues
3. Liên hệ support team
4. Tạo issue mới

### Useful Commands:
```bash
# Railway
railway status
railway logs
railway variables
railway redeploy

# Vercel
vercel logs
vercel env ls
vercel redeploy

# Docker
docker-compose logs -f
docker-compose ps
docker-compose restart
```

---

**🎉 Chúc mừng! Bạn đã deploy thành công AI Car Agent!**


