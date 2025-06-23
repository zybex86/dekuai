# 🐳 AutoGen DekuDeals - Docker Deployment Guide

Production-ready containerization for **AutoGen DekuDeals Game Analysis System**.

## 📋 Overview

This guide covers **Phase 6.3: Production Deployment** with enterprise-level Docker infrastructure:

- **Multi-stage Dockerfile** with optimized production builds
- **Development & Production** Docker Compose configurations  
- **Enterprise security** with non-root users, read-only filesystems
- **Smart entrypoint** with multiple operation modes
- **Production Makefile** with 20+ management commands

## 🚀 Quick Start

### 1. **One-Command Setup**
```bash
make setup
# Creates directories, copies env template, sets permissions
```

### 2. **Configure Environment**
```bash
# Edit .env file with your OpenAI API key
nano .env
# Required: OPENAI_API_KEY=sk-your-api-key-here
```

### 3. **Choose Your Environment**

#### **Development (Recommended for Testing)**
```bash
make dev          # Full development environment
make dev-cli      # Interactive CLI in container
make dev-quick    # Quick game analysis
```

#### **Production (Enterprise Deployment)**
```bash
make prod-deploy  # Full production deployment
make prod-update  # Update existing deployment
make prod-stop    # Stop production environment
```

## 🏗️ Architecture

### **Multi-Stage Dockerfile**
```dockerfile
# Stage 1: Builder (dependencies + build artifacts)
FROM python:3.13.3-slim AS builder
# Install dependencies, copy code, prepare app

# Stage 2: Production (optimized runtime)  
FROM python:3.13.3-slim AS production
# Copy from builder, security hardening, minimal runtime
```

**Benefits:**
- **Smaller images**: Production image without build tools
- **Security**: Non-root user, dropped capabilities, read-only filesystem
- **Performance**: Optimized Python environment

### **Smart Entrypoint**
```bash
./entrypoint.sh api        # API server mode (future)
./entrypoint.sh cli        # Interactive CLI
./entrypoint.sh demo       # Demo mode
./entrypoint.sh quick "Celeste"  # Quick analysis
./entrypoint.sh batch "INSIDE" "Hollow Knight"  # Batch processing
./entrypoint.sh test       # Run test suite
./entrypoint.sh health     # Health check
```

## 📁 Files Created

### **Core Docker Files**
- `Dockerfile` - Multi-stage production build (113 lines)
- `docker-compose.yml` - Development environment (134 lines)  
- `docker-compose.prod.yml` - Production environment (229 lines)
- `entrypoint.sh` - Smart startup script (256 lines)
- `env.example` - Environment template (127 lines)
- `Makefile` - Management commands (243 lines)
- `.dockerignore` - Build optimization

### **Directory Structure**
```
autogen-tut/
├── 🐳 Docker Infrastructure
│   ├── Dockerfile                 # Multi-stage build
│   ├── docker-compose.yml         # Development config
│   ├── docker-compose.prod.yml    # Production config
│   ├── entrypoint.sh             # Startup script
│   ├── .dockerignore             # Build optimization
│   └── Makefile                  # Management commands
├── ⚙️ Configuration
│   ├── env.example               # Environment template
│   └── .env                      # Your config (created by setup)
├── 📂 Data Directories
│   ├── cache/                    # Application cache
│   ├── logs/                     # Application logs
│   ├── data/                     # Application data
│   └── production/               # Production volumes
│       ├── cache/
│       ├── logs/
│       └── data/
└── 🎮 Application Code
    ├── enhanced_cli.py           # Main CLI interface
    ├── agent_tools.py            # AutoGen tools
    ├── utils/                    # Core utilities
    └── ...                       # Rest of application
```

## 🛠️ Makefile Commands

### **Development Commands**
```bash
make build          # Build Docker image for development
make dev            # Start development environment
make dev-cli        # Interactive CLI in container
make dev-quick      # Quick game analysis
make test           # Run test suite
make test-comprehensive  # Comprehensive testing
```

### **Production Commands**
```bash
make build-prod     # Build optimized production image
make prod-deploy    # Deploy to production
make prod-update    # Update production deployment
make prod-stop      # Stop production environment
```

### **Management Commands**
```bash
make logs           # Show container logs
make status         # Show container status
make shell          # Access container shell
make health         # Check container health
make info           # Show system information
make clean          # Clean up containers/images
make version        # Show version information
```

### **Setup & Configuration**
```bash
make setup          # Initial setup (directories, .env)
make check-env      # Validate environment
make help           # Show all commands
```

## 🔒 Security Features (Production)

### **Container Security**
- **Non-root user**: UID/GID 1000 for security
- **Read-only filesystem**: Prevents container modifications
- **Dropped capabilities**: Minimal Linux capabilities (only CHOWN, SETGID, SETUID)
- **No new privileges**: Prevents privilege escalation
- **Temporary filesystems**: Writable areas in memory only

### **Image Security**
- **Multi-stage build**: No build tools in production image
- **Minimal base**: python:3.13.3-slim (security patches)
- **Dependency scanning**: Requirements.txt only (no dev dependencies)
- **Resource limits**: Memory and CPU constraints

### **Network Security**
- **Custom networks**: Isolated container communication
- **Port mapping**: Configurable API port exposure
- **Secrets management**: External secrets for API keys

## 📊 Environment Configuration

### **Required Variables**
```bash
# .env file (copy from env.example)
OPENAI_API_KEY=sk-your-openai-api-key-here  # REQUIRED
APP_ENV=development|production
VERSION=6.3.0
```

### **Optional Variables**
```bash
# Performance
WORKERS=2                    # Number of worker processes
CACHE_TTL=3600              # Cache TTL in seconds
MAX_BATCH_SIZE=10           # Maximum batch size

# API (future)
API_PORT=8000               # API port
API_HOST=0.0.0.0           # API host

# Production Volumes
CACHE_VOLUME_PATH=/opt/autogen-dekudeals/cache
LOGS_VOLUME_PATH=/opt/autogen-dekudeals/logs
DATA_VOLUME_PATH=/opt/autogen-dekudeals/data

# Features
ENABLE_BATCH_PROCESSING=true
ENABLE_ADVANCED_CACHING=true
ENABLE_QUALITY_METRICS=true
```

## 🎯 Usage Examples

### **Development Workflow**
```bash
# 1. Setup environment
make setup
nano .env  # Add OPENAI_API_KEY

# 2. Start development
make dev-cli

# 3. Test batch processing
make test-comprehensive

# 4. View logs
make logs

# 5. Cleanup
make clean
```

### **Production Deployment**
```bash
# 1. Setup production environment
make setup
nano .env  # Configure for production

# 2. Deploy to production
make prod-deploy

# 3. Monitor deployment
make status-prod
make logs-prod

# 4. Update deployment
make prod-update

# 5. Health check
make health
```

### **Quick Testing**
```bash
# Build and test quickly
make build && make dev-quick
# Enter game name when prompted

# Or direct command
docker run --rm -it --env-file .env \
  -v $(pwd)/cache:/app/cache \
  autogen-dekudeals:latest quick "Hollow Knight"
```

## 🔧 Troubleshooting

### **Docker Permission Issues**
```bash
# Add user to docker group (requires logout/login)
sudo usermod -aG docker $USER

# Or use sudo for all docker commands
sudo make build
sudo make dev
```

### **Environment Issues**
```bash
# Check environment
make check-env

# Validate Docker setup
make info

# Check container health
make health
```

### **Build Issues**
```bash
# Clean and rebuild
make clean
make build

# Check Dockerfile syntax
head -20 Dockerfile

# Check available space
df -h
```

### **Runtime Issues**
```bash
# Check container logs
make logs

# Access container shell for debugging
make shell

# Check container status
make status
```

## 📈 Performance Optimization

### **Development vs Production**
| Feature | Development | Production |
|---------|-------------|------------|
| **Memory Limit** | 1GB | 2GB |
| **CPU Limit** | 1.0 | 2.0 |
| **Workers** | 1 | 2 |
| **Security** | Basic | Enterprise |
| **Logging** | Verbose | Structured |
| **Health Checks** | 30s | 15s |

### **Cache Configuration**
```bash
# Development: Local volumes
./cache:/app/cache

# Production: Named volumes with backup
autogen_cache_prod:/app/cache
```

### **Resource Monitoring**
```bash
# Container resource usage
docker stats autogen-dekudeals-prod

# Container health
docker inspect autogen-dekudeals-prod | grep Health

# Logs analysis
make logs-prod | grep ERROR
```

## 🚀 Next Steps

After successful Docker deployment:

1. **Phase 6.4: Monitoring & Analytics**
   - Grafana/Prometheus integration
   - Real-time dashboards
   - Performance metrics

2. **Phase 6.5: Advanced Features**
   - API endpoints with FastAPI
   - Web interface
   - CI/CD pipeline integration

3. **Production Scaling**
   - Kubernetes deployment
   - Load balancing
   - Database integration

## 📝 Notes

- **Docker permissions**: User must be in `docker` group or use `sudo`
- **Environment setup**: Copy `env.example` to `.env` and configure
- **Resource requirements**: Minimum 2GB RAM, 10GB disk space
- **Network requirements**: Internet access for DekuDeals.com scraping

---

## 🎉 Success Metrics

**Phase 6.3 Step 1 Complete:**
- ✅ **Multi-stage Dockerfile** (113 lines) with security hardening
- ✅ **Development environment** (134 lines) with hot reload support  
- ✅ **Production environment** (229 lines) with enterprise security
- ✅ **Smart entrypoint** (256 lines) with 8 operation modes
- ✅ **Management Makefile** (243 lines) with 20+ commands
- ✅ **Environment configuration** with comprehensive templates
- ✅ **Security hardening** with non-root users and capability dropping

**Total infrastructure: 1,102 lines of production-ready Docker code!**

Ready for **Phase 6.3 Step 2: CI/CD Pipeline** 🚀 