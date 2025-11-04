# Chariot Security Platform

<div align='center'>

![Chariot Logo](https://via.placeholder.com/150x150?text=Chariot)

**AI-Powered Web3 Security Platform**

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-in%20development-yellow.svg)]()

</div>

---

## 📋 Table of Contents

- [Overview](#overview)
- [Project Status](#project-status)
- [Architecture](#architecture)
- [Technology Stack](#technology-stack)
- [Getting Started](#getting-started)
- [Team Responsibilities](#team-responsibilities)
- [Development Guide](#development-guide)
- [API Documentation](#api-documentation)
- [Deployment](#deployment)
- [Contributing](#contributing)

---

## 🎯 Overview

Chariot is a comprehensive security platform designed for Web3 and fintech applications. It provides real-time threat detection, fraud prevention, behavioral analysis, and AI-powered security insights.

### Key Features

- 🛡️ **Real-time Transaction Analysis** - ML-powered fraud detection
- 🤖 **AI Threat Intelligence** - Behavioral anomaly detection
- 🚨 **Intelligent Alerting** - Multi-channel notifications with smart correlation
- 📊 **Automated Reporting** - AI-generated security reports and insights
- 🔐 **Multi-chain Support** - Ethereum, Polygon, BSC, Solana
- 💳 **Flexible Payments** - USDT on-chain + Paystack (Naira)
- 👥 **Community System** - Referral-based affiliate program

---

## 📊 Project Status

### ✅ Completed Components

#### Backend Services (6/6)
- ✅ **Auth Service** (Port 8001)
  - User registration & authentication
  - JWT-based session management
  - Community/referral system
  - Device fingerprinting

- ✅ **Fraud Detection Service** (Port 8002)
  - Real-time transaction analysis
  - Smart contract bytecode inspection
  - Malicious contract database
  - Transaction simulation

- ✅ **ML Serving Service** (Port 8003)
  - Fraud prediction models
  - Anomaly detection
  - Risk scoring engine
  - Behavioral analysis

- ✅ **Alert Engine** (Port 8004)
  - Security event management
  - Multi-channel notifications (Email, SMS, Push, Webhook)
  - Real-time alerting
  - Alert correlation

- ✅ **Payment Service** (Port 8005)
  - USDT payment verification (Ethereum, Polygon, BSC)
  - Paystack integration (Naira)
  - Subscription management
  - Community commission system

- ✅ **Reporting Service** (Port 8006)
  - AI-powered report generation (OpenAI integration)
  - Compliance reporting
  - Trend analysis
  - Custom recommendations

#### Shared Infrastructure
- ✅ Database utilities (PostgreSQL + SQLAlchemy)
- ✅ Redis client (Caching, sessions, queues)
- ✅ Authentication middleware (JWT)
- ✅ Rate limiting
- ✅ Error handling
- ✅ Encryption service
- ✅ Logging system

#### Project Structure
- ✅ Complete folder structure
- ✅ Service isolation
- ✅ Shared utilities
- ✅ Configuration management

### 🚧 In Progress / Pending

#### Frontend (0% Complete)
- ⏳ **React + TypeScript Setup**
  - Basic project structure created
  - Dependencies configured
  - Needs implementation

- ⏳ **Core Pages**
  - [ ] Login/Register
  - [ ] Dashboard (with real-time stats)
  - [ ] Transaction Analysis
  - [ ] Security Events
  - [ ] Alerts Management
  - [ ] Reports & Analytics
  - [ ] Subscription/Payments
  - [ ] Community Dashboard

- ⏳ **Components**
  - [ ] Security widgets
  - [ ] Charts & visualizations
  - [ ] Alert notifications
  - [ ] Forms & inputs

#### ML Models (Training Required)
- ⏳ **Fraud Detection Model**
  - Structure created
  - Needs training data
  - Needs model training

- ⏳ **Anomaly Detection Model**
  - Structure created
  - Needs baseline data
  - Needs model training

- ⏳ **Risk Scoring Model**
  - Structure created
  - Needs feature engineering
  - Needs model training

- ⏳ **Behavioral Analysis Model**
  - Structure created
  - Needs user behavior data
  - Needs model training

#### Infrastructure
- ⏳ **Docker Containers**
  - [ ] Dockerfile for each service
  - [ ] Docker Compose orchestration
  - [ ] Environment configuration

- ⏳ **Database**
  - [ ] PostgreSQL setup
  - [ ] Initial migrations
  - [ ] Seed data

- ⏳ **Deployment**
  - [ ] CI/CD pipeline
  - [ ] Kubernetes manifests
  - [ ] Production environment

#### Testing
- [ ] Unit tests
- [ ] Integration tests
- [ ] End-to-end tests
- [ ] Load testing

#### Documentation
- [ ] API documentation (Swagger/OpenAPI)
- [ ] Architecture diagrams
- [ ] Deployment guide
- [ ] User guide

---

## 🏗️ Architecture

\\\
┌─────────────────────────────────────────────────────────┐
│                    Frontend Layer                        │
│              React + TypeScript + Tailwind               │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│                  API Gateway (Future)                    │
│            Load Balancing + Rate Limiting                │
└────────────────────┬────────────────────────────────────┘
                     │
      ┌──────────────┼──────────────┐
      │              │              │
┌─────▼─────┐  ┌────▼────┐  ┌──────▼──────┐
│   Auth    │  │  Fraud  │  │ML Serving   │
│  Service  │  │Detection│  │   Service   │
│  :8001    │  │ :8002   │  │   :8003     │
└───────────┘  └─────────┘  └─────────────┘
      │              │              │
┌─────▼─────┐  ┌────▼────┐  ┌──────▼──────┐
│  Alert    │  │ Payment │  │ Reporting   │
│  Engine   │  │ Service │  │  Service    │
│  :8004    │  │ :8005   │  │   :8006     │
└───────────┘  └─────────┘  └─────────────┘
      │              │              │
      └──────────────┼──────────────┘
                     │
      ┌──────────────┼──────────────┐
      │              │              │
┌─────▼─────┐  ┌────▼────┐  ┌──────▼──────┐
│PostgreSQL │  │  Redis  │  │ Blockchain  │
│ Database  │  │ Cache   │  │   Nodes     │
└───────────┘  └─────────┘  └─────────────┘
\\\

---

## 🛠️ Technology Stack

### Backend
- **Python 3.11+** - Core language
- **FastAPI** - Web framework
- **SQLAlchemy** - ORM
- **PostgreSQL** - Primary database
- **Redis** - Caching & sessions
- **Web3.py** - Blockchain interaction
- **OpenAI API** - AI report generation
- **JWT** - Authentication

### Frontend
- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **Socket.IO** - Real-time updates
- **Axios** - HTTP client
- **React Router** - Navigation
- **Recharts** - Data visualization

### ML/AI
- **scikit-learn** - Classical ML
- **NumPy** - Numerical computing
- **OpenAI GPT** - Report generation
- **TensorFlow/PyTorch** (Future) - Deep learning

### DevOps
- **Docker** - Containerization
- **Kubernetes** - Orchestration
- **GitHub Actions** - CI/CD
- **Nginx** - Reverse proxy

### Blockchain
- **Web3.js/Web3.py** - Ethereum interaction
- **Alchemy/Infura** - RPC providers
- **Ethers.js** - Frontend blockchain

---

## 🚀 Getting Started

### Prerequisites

\\\ash
# Required
- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- Redis 7+

# Optional
- Docker & Docker Compose
\\\

### Installation

#### 1. Clone Repository

\\\ash
git clone https://github.com/YOUR_USERNAME/ChariotSecurity.git
cd ChariotSecurity
\\\

#### 2. Backend Setup

\\\ash
cd backend

# Install dependencies for each service
cd services/auth-service
pip install -r requirements.txt

cd ../fraud-detection
pip install -r requirements.txt

# ... repeat for other services

# Create .env file
cp .env.example .env
# Edit .env with your configurations
\\\

#### 3. Database Setup

\\\ash
# Create PostgreSQL database
createdb chariot_security

# Run migrations
python database/migrations/001_initial.sql
\\\

#### 4. Frontend Setup

\\\ash
cd frontend

# Install dependencies
npm install

# Create .env file
cp .env.example .env

# Start development server
npm run dev
\\\

### Running Services

#### Option 1: Manual Start

\\\ash
# Terminal 1 - Auth Service
cd backend/services/auth-service
python main.py

# Terminal 2 - Fraud Detection
cd backend/services/fraud-detection
python main.py

# Terminal 3 - ML Serving
cd backend/services/ml-serving
python main.py

# Terminal 4 - Alert Engine
cd backend/services/alert-engine
python main.py

# Terminal 5 - Payment Service
cd backend/services/payment-service
python main.py

# Terminal 6 - Reporting Service
cd backend/services/reporting-service
python main.py

# Terminal 7 - Frontend
cd frontend
npm run dev
\\\

#### Option 2: Docker (Recommended - Coming Soon)

\\\ash
docker-compose up
\\\

### Access Points

- **Frontend:** http://localhost:3000
- **Auth Service:** http://localhost:8001
- **Fraud Detection:** http://localhost:8002
- **ML Serving:** http://localhost:8003
- **Alert Engine:** http://localhost:8004
- **Payment Service:** http://localhost:8005
- **Reporting Service:** http://localhost:8006

---

## 👥 Team Responsibilities

### Backend Lead (HandsomeKing) - AI/ML Focus
**Services:**
- ✅ ML Serving Service
- ✅ Fraud Detection Service
- ✅ Alert Engine
- ✅ Reporting Service

**ML Models:**
- ⏳ Train fraud detection model
- ⏳ Train anomaly detection model
- ⏳ Train risk scoring model
- ⏳ Train behavioral analysis model

**Tasks:**
- [ ] Collect training data
- [ ] Feature engineering
- [ ] Model training & optimization
- [ ] Model deployment & monitoring
- [ ] Alert correlation algorithms
- [ ] Report generation optimization

### Backend Developer 2 (TBD)
**Services:**
- ✅ Auth Service
- ✅ Payment Service

**Tasks:**
- [ ] Test authentication flows
- [ ] Integrate Paystack
- [ ] Test USDT verification
- [ ] Commission calculation verification
- [ ] Community management features

### Frontend Developer (TBD)
**Responsibilities:**
- ⏳ Implement all frontend pages
- ⏳ Build reusable components
- ⏳ Integrate with backend APIs
- ⏳ Real-time WebSocket integration
- ⏳ Responsive design
- ⏳ State management

**Priority Pages:**
1. Login/Register
2. Dashboard
3. Transaction Analysis
4. Alerts
5. Subscription/Payment

### DevOps Engineer (TBD)
**Responsibilities:**
- [ ] Docker containerization
- [ ] Kubernetes setup
- [ ] CI/CD pipeline
- [ ] Monitoring & logging
- [ ] Database backups
- [ ] Production deployment

---

## 📚 Development Guide

### Backend Development

#### Adding a New Service

\\\ash
cd backend/services
mkdir new-service
cd new-service

# Create files
touch main.py models.py routes.py service.py config.py requirements.txt
\\\

#### API Endpoint Pattern

\\\python
from fastapi import APIRouter, Depends
from shared.middleware.auth import get_current_user

router = APIRouter(prefix='/your-service', tags=['Your Service'])

@router.get('/endpoint')
async def your_endpoint(current_user: dict = Depends(get_current_user)):
    return {'success': True, 'data': {}}
\\\

#### Database Models

\\\python
from sqlalchemy import Column, String, DateTime
from shared.utils.database import Base

class YourModel(Base):
    __tablename__ = 'your_table'
    
    id = Column(UUID(as_uuid=True), primary_key=True)
    name = Column(String(255), nullable=False)
\\\

### Frontend Development

#### Creating Components

\\\	ypescript
// src/components/YourComponent.tsx
import React from 'react'

interface YourComponentProps {
  title: string
}

const YourComponent: React.FC<YourComponentProps> = ({ title }) => {
  return (
    <div className="p-4 bg-white rounded-lg shadow">
      <h2>{title}</h2>
    </div>
  )
}

export default YourComponent
\\\

#### API Integration

\\\	ypescript
// src/services/yourService.ts
import api from './api'

export const yourService = {
  getData: async () => {
    const response = await api.get('/your-endpoint')
    return response.data
  }
}
\\\

### Code Style

- **Python:** Follow PEP 8
- **TypeScript:** Use ESLint config
- **Commits:** Conventional commits (feat:, fix:, docs:)
- **Branches:** feature/*, bugfix/*, hotfix/*

---

## 📖 API Documentation

### Authentication

**POST /auth/register**
\\\json
{
  "email": "user@example.com",
  "password": "secure_password",
  "wallet_address": "0x...",
  "referral_code": "CHR-XXXX"
}
\\\

**POST /auth/login**
\\\json
{
  "email": "user@example.com",
  "password": "secure_password",
  "device_fingerprint": {...}
}
\\\

### Fraud Detection

**POST /fraud/analyze**
\\\json
{
  "to_address": "0x...",
  "data": "0x...",
  "value": "1000000000000000000",
  "chain_id": 1
}
\\\

**Response:**
\\\json
{
  "success": true,
  "data": {
    "risk_score": 0.85,
    "risk_level": "High",
    "threats": [...],
    "recommendation": "⚠️ PROCEED WITH EXTREME CAUTION"
  }
}
\\\

### Full API Docs

- Swagger UI: http://localhost:8001/docs (per service)
- ReDoc: http://localhost:8001/redoc

---

## 🚢 Deployment

### Environment Variables

\\\ash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/chariot_security

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# JWT
JWT_SECRET_KEY=your-secret-key
SECRET_KEY=your-app-secret

# Blockchain
ETHEREUM_RPC_URL=https://eth-mainnet.alchemyapi.io/v2/YOUR_KEY
POLYGON_RPC_URL=https://polygon-mainnet.alchemyapi.io/v2/YOUR_KEY
BSC_RPC_URL=https://bsc-dataseed.binance.org/

# Payment
PAYSTACK_SECRET_KEY=sk_test_xxxxx
PAYSTACK_PUBLIC_KEY=pk_test_xxxxx

# AI
OPENAI_API_KEY=sk-xxxxx
\\\

### Production Deployment (Coming Soon)

\\\ash
# Build Docker images
docker-compose -f docker-compose.prod.yml build

# Deploy to Kubernetes
kubectl apply -f infrastructure/kubernetes/

# Monitor
kubectl get pods
\\\

---

## 🤝 Contributing

### Getting Started

1. Fork the repository
2. Create a feature branch (\git checkout -b feature/amazing-feature\)
3. Commit your changes (\git commit -m 'feat: add amazing feature'\)
4. Push to branch (\git push origin feature/amazing-feature\)
5. Open a Pull Request

### Pull Request Guidelines

- Clear description of changes
- Link related issues
- Update documentation
- Add tests if applicable
- Ensure all tests pass

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 📞 Contact & Support

- **Project Lead:** HandsomeKing
- **Email:** support@chariotsecurity.io
- **Discord:** [Join our server](#)
- **Documentation:** [docs.chariotsecurity.io](#)

---

## 🗺️ Roadmap

### Phase 1: MVP (Current)
- [x] Backend services architecture
- [x] Core ML models structure
- [ ] Frontend implementation
- [ ] ML model training

### Phase 2: Enhancement (Q2 2024)
- [ ] Mobile app (React Native)
- [ ] Browser extension
- [ ] Advanced ML models
- [ ] Social protection features

### Phase 3: Scale (Q3 2024)
- [ ] Multi-language support
- [ ] Enterprise features
- [ ] White-label options
- [ ] Advanced analytics

---

## ⭐ Acknowledgments

- OpenAI for GPT integration
- Web3.py community
- FastAPI framework
- React ecosystem

---

<div align='center'>

**Built with ❤️ by the Chariot Team**

[Website](#) • [Documentation](#) • [Twitter](#) • [Discord](#)

</div>
#   C h a r i o t S e c u r i t y  
 