# AI Trading System

A comprehensive AI-powered trading platform with real-time analysis, pattern recognition, and automated deployment.

## 🚀 Features

- **Real-time Stock Analysis**: Live data streaming from US and Taiwan markets
- **AI-Powered Insights**: OpenAI integration for intelligent trading recommendations  
- **Technical Indicators**: Advanced pattern recognition and signal generation
- **Interactive Charts**: TradingView integration with custom indicators
- **User Authentication**: Google OAuth and JWT-based security
- **Automated Backtesting**: Strategy performance analysis
- **Multi-Market Support**: US stocks and Taiwan Stock Exchange

## 🏗️ Architecture

### Frontend
- **Framework**: Next.js 14 with TypeScript
- **Styling**: Tailwind CSS
- **Charts**: TradingView Charting Library
- **Authentication**: Google OAuth
- **Deployment**: Google Cloud Run

### Backend  
- **Framework**: FastAPI with Python
- **Database**: PostgreSQL on Cloud SQL
- **AI Integration**: OpenAI GPT-4
- **Data Sources**: Multiple financial APIs
- **Deployment**: Google Cloud Run

### Infrastructure
- **Container Registry**: Google Artifact Registry
- **CI/CD**: Google Cloud Build with GitHub integration
- **Monitoring**: Google Cloud Logging
- **Security**: Secret Manager for API keys

## 🔧 Development

### Prerequisites
- Docker
- Node.js 18+
- Python 3.8+
- Google Cloud SDK

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/OVEROVEN/ai-trading-system.git
   cd ai-trading-system
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and configuration
   ```

3. **Run with Docker Compose**
   ```bash
   docker-compose up --build
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000

## 🚀 Deployment

### Automatic Deployment
Pushes to the `main` branch automatically trigger:
- Frontend deployment to Cloud Run
- Backend deployment to Cloud Run  
- Database migrations (if needed)

### Manual Deployment
```bash
# Deploy frontend
gcloud run deploy auto-trade-frontend --source ./frontend --region asia-northeast1

# Deploy backend  
gcloud run deploy auto-trade-backend --source . --region asia-northeast1
```

## 📊 API Endpoints

- `GET /api/stocks/{symbol}` - Get stock data
- `POST /api/analysis/technical` - Technical analysis
- `POST /api/analysis/ai` - AI-powered analysis
- `GET /api/charts/{symbol}` - Chart data
- `POST /api/backtest` - Strategy backtesting

## 🔐 Security

- API keys stored in Google Secret Manager
- OAuth 2.0 authentication
- HTTPS-only communication
- CORS properly configured
- Rate limiting implemented

## 📈 Performance

- **Frontend**: Optimized with Next.js static generation
- **Backend**: Async FastAPI with connection pooling  
- **Database**: Indexed queries and caching
- **CDN**: Static assets served via Google Cloud CDN

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- TradingView for charting library
- OpenAI for AI capabilities
- Google Cloud for infrastructure
- The open-source community

---

**Live Application**: [AI Trading Dashboard](https://auto-trade-frontend-610357573971.asia-northeast1.run.app)

🤖 Generated with [Claude Code](https://claude.ai/code)