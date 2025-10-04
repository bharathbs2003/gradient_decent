# Multilingual AI Video Dubbing Platform

A comprehensive AI-powered platform for creating high-fidelity multilingual dubbed videos with synchronized, realistic facial animations.

## 🎯 Vision
Enable seamless, high-fidelity, multilingual dubbing of video content by automatically synchronizing translated speech with realistic, speaker-consistent facial animations—eliminating the "uncanny valley" effect and enhancing global accessibility of digital media.

## 🚀 Features

### Core Capabilities
- **Automated Dubbing Pipeline**: Reduce manual dubbing effort by ≥80%
- **50+ Language Support**: Cover top spoken languages by internet users
- **High-Quality Lip Sync**: Achieve LSE-C ≥ 0.85 accuracy
- **Real-time Preview**: <5 sec latency for short clips
- **Ethical AI**: Embedded provenance and consent management

### Technical Features
- **Input Processing**: Support for MP4, MOV, AVI with automatic speaker detection
- **Multilingual Translation**: ASR + LLM translation with human review interface
- **Voice Synthesis**: Voice cloning with emotion-aware TTS
- **Facial Re-animation**: 3D face reconstruction with neural rendering
- **Ethical Safeguards**: Digital watermarking and consent tracking

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend UI   │    │   Backend API   │    │  AI Services    │
│   (React)       │◄──►│   (FastAPI)     │◄──►│  (Microservices)│
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   Database      │
                       │   (PostgreSQL)  │
                       └─────────────────┘
```

## 🛠️ Tech Stack

- **Backend**: FastAPI, PostgreSQL, Redis, Celery
- **Frontend**: React, TypeScript, Tailwind CSS, Vite
- **AI/ML**: PyTorch, Transformers, OpenCV, MediaPipe
- **Infrastructure**: Docker, AWS/GCP, Kubernetes
- **Monitoring**: Prometheus, Grafana

## 📋 Quick Start

### Option 1: Simple Setup (Recommended for Testing)

1. **Install dependencies**
   ```bash
   ./install_dependencies.sh
   ```

2. **Start the server**
   ```bash
   cd backend
   python3 -m uvicorn app.minimal_main:app --host 0.0.0.0 --port 8001
   ```

3. **Access the platform**
   - API: http://localhost:8001
   - API Docs: http://localhost:8001/docs
   - Health Check: http://localhost:8001/health

### Option 2: Full Docker Setup

1. **Start with Docker Compose**
   ```bash
   docker-compose up -d
   ```

2. **Access the platform**
   - Frontend: http://localhost:3000
   - API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Option 3: Development Setup

1. **Use the startup script**
   ```bash
   python3 start_server.py --backend-only --port 8001
   ```

## 🔧 Troubleshooting

If you encounter issues, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for detailed solutions.

**Common Issues**:
- **Internal Server Error**: Run `./install_dependencies.sh`
- **Port in use**: Use `--port 8001` instead of 8000
- **Missing modules**: Install dependencies with pip3

## 📊 Performance Metrics

| Metric | Target | Tool |
|--------|--------|------|
| Lip-sync accuracy | LSE-C ≥ 0.85 | SyncNet |
| Visual fidelity | FID ≤ 15 | Fréchet Inception Distance |
| Emotion preservation | AU correlation ≥ 0.75 | OpenFace AUs |
| Translation quality | BLEU ≥ 35 | SacreBLEU |
| Processing time | <1 min per 1-min clip | - |

## 🗺️ Roadmap

- **Q1 2025**: MVP - English → 5 languages, 720p
- **Q3 2025**: Scale - 50 languages, 1080p
- **Q1 2026**: Enterprise - 4K support, real-time API

## 🔒 Ethics & Compliance

- Explicit consent framework
- Digital watermarking (C2PA compliant)
- Actor rights compliance
- Bias mitigation audits

## 📄 License

MIT License - see LICENSE file for details.

## 🤝 Contributing

Please read CONTRIBUTING.md for contribution guidelines.