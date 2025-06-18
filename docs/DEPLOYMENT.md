# 🚀 AutoGen DekuDeals - Deployment Guide

Complete deployment documentation for **AutoGen DekuDeals CI/CD Pipeline**.

## 📋 Overview

This guide covers both **local development** and **GitHub-based production** deployment strategies for the AutoGen DekuDeals system.

### 🎯 Available Deployment Options

1. **🏠 Local Development** - Immediate deployment on your machine
2. **🔄 Local CI/CD** - Professional build/deploy pipeline (works now)
3. **☁️ GitHub-based** - Production-ready CI/CD with GitHub Actions (when ready)

## 🏠 Local Development Deployment

### **Quick Start (5 minutes)**

```bash
# 1. Ensure Docker is running
docker --version

# 2. Build the image
./scripts/local-build.sh

# 3. Deploy interactively
./scripts/local-deploy.sh

# 4. Or deploy specific mode
./scripts/local-deploy.sh -m quick "Hollow Knight"
```

### **Available Local Commands**

#### **Build Commands**
```bash
# Professional build pipeline
./scripts/local-build.sh [version]

# Build with specific version
./scripts/local-build.sh v6.3.0

# Build latest
./scripts/local-build.sh
```

#### **Deployment Commands**
```bash
# Interactive CLI (default)
./scripts/local-deploy.sh

# Demo mode
./scripts/local-deploy.sh -m demo

# Quick game analysis
./scripts/local-deploy.sh -m quick "Game Name"

# Batch analysis
./scripts/local-deploy.sh -m batch "Game1" "Game2" "Game3"

# Health check
./scripts/local-deploy.sh -m health

# Detached API mode (future)
./scripts/local-deploy.sh -d -m api
```

#### **Management Commands**
```bash
# Show deployment status
./scripts/local-deploy.sh status

# Test deployment
./scripts/local-deploy.sh test

# Cleanup containers
./scripts/local-deploy.sh cleanup

# Build before deploy
./scripts/local-deploy.sh build
```

#### **Advanced Options**
```bash
# Specific version
./scripts/local-deploy.sh -v dev-20250618 -m cli

# Custom environment file
./scripts/local-deploy.sh -e custom.env -m cli

# Custom port mapping
./scripts/local-deploy.sh -p 9000:8000 -m api

# Help
./scripts/local-deploy.sh --help
```

## 🔄 Local CI/CD Pipeline

### **Complete Local Workflow**

```bash
# 1. Code Development
# Make your changes to the codebase

# 2. Professional Build
./scripts/local-build.sh
# ✅ Environment validation
# ✅ Code quality checks  
# ✅ Security scanning
# ✅ Docker build
# ✅ Testing
# ✅ Build report generation

# 3. Professional Deployment
./scripts/local-deploy.sh -m cli
# ✅ Environment validation
# ✅ Image verification
# ✅ Configuration checks
# ✅ Container deployment

# 4. Management
./scripts/local-deploy.sh status    # Check status
./scripts/local-deploy.sh cleanup   # Clean up
```

### **Build Pipeline Features**

- **🔍 Environment Validation** - Docker, Python, dependencies
- **🔒 Security Scanning** - API key leak detection
- **🧪 Code Quality** - Syntax checking and validation
- **🐳 Docker Build** - Multi-stage production builds
- **✅ Testing** - Health checks and functionality tests
- **📋 Reporting** - Detailed build reports with metrics

### **Deployment Pipeline Features**

- **🎯 Multiple Modes** - CLI, API, demo, quick, batch
- **⚙️ Configuration Management** - Environment files, port mapping
- **📊 Status Monitoring** - Container and image management
- **🧹 Cleanup Tools** - Container lifecycle management
- **🔧 Version Control** - Multiple image versions

## ☁️ GitHub-based CI/CD (When Ready)

### **Prerequisites for GitHub Deployment**

1. **Create GitHub Repository**
2. **Configure Secrets**
3. **Set up Environments**
4. **Push Code**

### **GitHub Actions Workflows Available**

#### **1. Main CI Pipeline (`.github/workflows/ci.yml`)**
**Triggers:** Every push to main/master, pull requests
**Features:**
- ✅ **Build & Test** - Python syntax, Docker build, functionality tests
- ✅ **Security Scan** - Trivy vulnerability scanning, secrets detection
- ✅ **Artifacts** - Docker image artifacts with 7-day retention
- ✅ **Reporting** - Build summaries and status reports

```yaml
# Automatic on push
git push origin main

# Manual trigger
# GitHub Actions → CI/CD Pipeline → Run workflow
```

#### **2. Production Deployment (`.github/workflows/prod-deploy.yml`)**
**Triggers:** Git tags (v*), manual dispatch
**Features:**
- ✅ **Production Build** - Multi-stage Docker builds
- ✅ **Manual Approval** - Production environment protection
- ✅ **GitHub Release** - Automated release creation with assets
- ✅ **Documentation** - Release notes and deployment instructions

```bash
# Create production release
git tag v6.3.0
git push origin v6.3.0

# GitHub will:
# 1. Build production image
# 2. Wait for manual approval
# 3. Create GitHub Release
# 4. Attach Docker image + docs
```

### **GitHub Repository Setup Guide**

#### **Step 1: Create Repository**
```bash
# Option A: GitHub CLI
gh repo create autogen-dekudeals --public

# Option B: GitHub Web Interface
# Go to github.com → New Repository → autogen-dekudeals
```

#### **Step 2: Configure Secrets**
Go to: `Repository → Settings → Secrets and variables → Actions`

**Required Secrets:**
- `OPENAI_API_KEY` - Your OpenAI API key for testing

**Optional Secrets:**
- `DOCKER_REGISTRY_TOKEN` - For private registries
- `DEPLOY_KEY` - For deployment automation

#### **Step 3: Set up Environments**
Go to: `Repository → Settings → Environments`

**Create Environment:** `production`
- ✅ **Required reviewers** - Add yourself
- ✅ **Wait timer** - 0 minutes
- ✅ **Deployment protection rules** - Enable

#### **Step 4: Push Code**
```bash
# Initialize git (if not already done)
git init
git branch -M main

# Add remote
git remote add origin https://github.com/yourusername/autogen-dekudeals.git

# Initial push
git add .
git commit -m "🚀 Initial CI/CD setup with GitHub Actions"
git push -u origin main
```

### **GitHub Workflows Usage**

#### **Development Workflow**
```bash
# 1. Make changes
git add .
git commit -m "✨ Add new feature"
git push origin main

# 2. GitHub automatically:
# ✅ Runs CI pipeline
# ✅ Builds Docker image
# ✅ Runs security scans
# ✅ Creates artifacts

# 3. Check results:
# GitHub → Actions → Latest workflow run
```

#### **Production Release Workflow**
```bash
# 1. Create release tag
git tag v6.3.0
git push origin v6.3.0

# 2. GitHub automatically:
# ✅ Builds production image
# ✅ Waits for approval

# 3. Manual approval:
# GitHub → Actions → Production Deployment → Review

# 4. After approval:
# ✅ Creates GitHub Release
# ✅ Attaches Docker image
# ✅ Generates release notes
```

## 📊 Deployment Comparison

| Feature | Local Development | Local CI/CD | GitHub CI/CD |
|---------|------------------|-------------|--------------|
| **Setup Time** | 2 minutes | 5 minutes | 15 minutes |
| **Build Pipeline** | Manual | Automated | Automated |
| **Security Scanning** | Basic | Advanced | Enterprise |
| **Deployment** | Immediate | Professional | Production |
| **Version Control** | Local tags | Local versions | Git tags |
| **Collaboration** | Single user | Team ready | Full team |
| **Release Management** | Manual | Semi-auto | Fully automated |
| **Cost** | Free | Free | Free (GitHub) |

## 🎯 Recommendations

### **For Individual Development**
```bash
# Quick development cycle
./scripts/local-build.sh && ./scripts/local-deploy.sh -m cli
```

### **For Team Development**
1. **Start with Local CI/CD** - Professional workflow
2. **Move to GitHub** - When ready for collaboration
3. **Use Production Pipeline** - For releases

### **For Production Use**
1. **GitHub repository** - Version control and collaboration
2. **GitHub Actions** - Automated CI/CD pipeline
3. **Manual approval** - Production deployment safety
4. **GitHub Releases** - Professional release management

## 🔧 Troubleshooting

### **Common Issues**

#### **Docker Permission Denied**
```bash
# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Or use sudo
sudo ./scripts/local-build.sh
sudo ./scripts/local-deploy.sh
```

#### **Image Not Found**
```bash
# Check available images
docker images autogen-dekudeals

# Build if missing
./scripts/local-build.sh

# Check build logs
./scripts/local-deploy.sh test
```

#### **Environment Issues**
```bash
# Check environment file
cat .env

# Validate environment
./scripts/local-deploy.sh test

# Create minimal environment
cp env.example .env
# Edit .env with your OpenAI API key
```

#### **GitHub Actions Failing**
```bash
# Check workflow syntax
# .github/workflows/ files should be valid YAML

# Check secrets
# Repository → Settings → Secrets → OPENAI_API_KEY

# Check permissions
# Repository → Settings → Actions → General → Workflow permissions
```

## 📚 Additional Resources

- **[DOCKER-README.md](../DOCKER-README.md)** - Complete Docker guide
- **[USER_GUIDE.md](../USER_GUIDE.md)** - User manual
- **[QUICK_SETUP.md](../QUICK_SETUP.md)** - 5-minute setup
- **[GITHUB-SETUP.md](./GITHUB-SETUP.md)** - GitHub repository setup

## 🎉 Success Metrics

**Local CI/CD Pipeline:**
- ✅ **Professional build automation** with quality checks
- ✅ **Security scanning** with secrets detection
- ✅ **Multi-mode deployment** with environment validation
- ✅ **Container management** with lifecycle automation

**GitHub CI/CD Pipeline:**
- ✅ **Enterprise workflow** with automated testing
- ✅ **Production protection** with manual approval gates
- ✅ **Release automation** with GitHub Releases
- ✅ **Collaboration ready** with team-friendly processes

**Ready for production deployment in any environment!** 🚀 