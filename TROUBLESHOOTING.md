# Troubleshooting Guide

## 🔧 Common Issues and Solutions

### Internal Server Error - SOLVED ✅

**Problem**: The server was showing internal server errors due to missing dependencies and configuration issues.

**Root Causes**:
1. Missing Python dependencies (FastAPI, Uvicorn, etc.)
2. Missing configuration files
3. Database connection issues
4. Import errors in the application

**Solution Steps**:

1. **Install Dependencies**:
   ```bash
   ./install_dependencies.sh
   ```

2. **Use Minimal Server** (if full app has issues):
   ```bash
   cd backend
   python3 -m uvicorn app.minimal_main:app --host 0.0.0.0 --port 8001
   ```

3. **Check Server Status**:
   ```bash
   curl http://localhost:8001/
   curl http://localhost:8001/health
   ```

### Port Already in Use

**Problem**: `[Errno 98] error while attempting to bind on address ('0.0.0.0', 8000): [errno 98] address already in use`

**Solutions**:
1. **Use Different Port**:
   ```bash
   python3 -m uvicorn app.minimal_main:app --host 0.0.0.0 --port 8001
   ```

2. **Kill Existing Process**:
   ```bash
   pkill -f uvicorn
   # or
   ps aux | grep uvicorn
   kill <process_id>
   ```

### Missing Dependencies

**Problem**: `No module named 'fastapi'` or similar import errors.

**Solution**:
```bash
# Install basic dependencies
pip3 install --user fastapi uvicorn pydantic sqlalchemy

# Or use the provided script
./install_dependencies.sh
```

### Database Issues

**Problem**: Database connection errors or missing tables.

**Solutions**:
1. **Use SQLite** (default in .env):
   ```
   DATABASE_URL=sqlite:///./dubbing_platform.db
   ```

2. **Initialize Database**:
   ```python
   from app.core.database import engine, Base
   Base.metadata.create_all(bind=engine)
   ```

### Configuration Issues

**Problem**: Missing environment variables or configuration errors.

**Solution**: Use the provided `.env` file with default values:
```bash
# Copy the .env file to backend directory if needed
cp .env backend/.env
```

## 🚀 Quick Start (Working Solution)

### Option 1: Minimal Server (Recommended for Testing)

```bash
# 1. Install dependencies
./install_dependencies.sh

# 2. Start minimal server
cd backend
python3 -m uvicorn app.minimal_main:app --host 0.0.0.0 --port 8001

# 3. Test in browser or curl
curl http://localhost:8001/
```

### Option 2: Full Application

```bash
# 1. Install dependencies
./install_dependencies.sh

# 2. Set up environment
cp .env backend/.env

# 3. Start full application
cd backend
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

### Option 3: Using Startup Script

```bash
# 1. Install dependencies
./install_dependencies.sh

# 2. Use startup script
python3 start_server.py --backend-only --port 8001
```

## 🧪 Testing the Server

### Basic Health Checks

```bash
# Root endpoint
curl http://localhost:8001/
# Expected: {"message":"Multilingual AI Video Dubbing Platform","version":"1.0.0","status":"active"}

# Health endpoint
curl http://localhost:8001/health
# Expected: {"status":"healthy"}

# API health (if available)
curl http://localhost:8001/api/v1/health
# Expected: {"status":"healthy","api_version":"v1"}
```

### API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc

## 🐛 Debugging Steps

### 1. Check Python Environment

```bash
python3 --version
pip3 --version
pip3 list | grep fastapi
```

### 2. Test Imports

```bash
python3 -c "import fastapi; print('FastAPI OK')"
python3 -c "import uvicorn; print('Uvicorn OK')"
python3 -c "import pydantic; print('Pydantic OK')"
```

### 3. Check Application Structure

```bash
ls -la backend/app/
python3 -c "from backend.app.main import app; print('App import OK')"
```

### 4. Run Diagnostic Script

```bash
python3 test_server.py
```

## 📁 File Structure Check

Ensure you have these key files:

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── minimal_main.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   └── database.py
│   └── api/
│       └── v1/
│           └── __init__.py
├── requirements.txt
└── .env
```

## 🔍 Log Analysis

### Enable Debug Mode

Add to `.env`:
```
DEBUG=true
LOG_LEVEL=DEBUG
```

### Check Logs

```bash
# Start with verbose logging
python3 -m uvicorn app.minimal_main:app --host 0.0.0.0 --port 8001 --log-level debug

# Or check application logs
tail -f logs/app.log  # if logging to file
```

## 🌐 Network Issues

### Firewall

```bash
# Check if port is accessible
curl -v http://localhost:8001/

# If using remote server, check firewall
sudo ufw status
sudo ufw allow 8001
```

### Host Binding

```bash
# Bind to all interfaces
--host 0.0.0.0

# Bind to localhost only
--host 127.0.0.1

# Bind to specific IP
--host 192.168.1.100
```

## 🔧 Performance Issues

### Memory Usage

```bash
# Check memory usage
free -h
ps aux | grep python

# Reduce memory usage
export PYTHONOPTIMIZE=1
```

### CPU Usage

```bash
# Check CPU usage
top | grep python
htop  # if available
```

## 📞 Getting Help

If you're still experiencing issues:

1. **Check the logs** for specific error messages
2. **Run the diagnostic script**: `python3 test_server.py`
3. **Try the minimal server** first: `app.minimal_main:app`
4. **Check dependencies** are properly installed
5. **Verify file permissions** and paths

### Common Error Messages

| Error | Solution |
|-------|----------|
| `No module named 'fastapi'` | Run `./install_dependencies.sh` |
| `Address already in use` | Use different port: `--port 8001` |
| `Permission denied` | Check file permissions: `chmod +x script.py` |
| `Database error` | Use SQLite: `DATABASE_URL=sqlite:///./db.sqlite` |
| `Import error` | Check `__init__.py` files exist |

## ✅ Success Indicators

You'll know the server is working when:

1. **Server starts without errors**
2. **Health endpoint responds**: `curl http://localhost:8001/health`
3. **Root endpoint responds**: `curl http://localhost:8001/`
4. **API docs accessible**: http://localhost:8001/docs
5. **No error messages in logs**

## 🎉 Next Steps

Once the server is running:

1. **Test API endpoints** using the Swagger UI
2. **Set up the frontend** (if needed)
3. **Configure AI services** (for full functionality)
4. **Set up database** (for production use)
5. **Configure monitoring** and logging