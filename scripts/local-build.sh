#!/bin/bash
# ===================================================================
# 🎮 AutoGen DekuDeals - Local Build Automation
# Professional build pipeline for local development
# ===================================================================

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
VERSION="${1:-dev-$(date +'%Y%m%d')-$(git rev-parse --short HEAD 2>/dev/null || echo 'local')}"
BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ')
VCS_REF=$(git rev-parse --short HEAD 2>/dev/null || echo 'unknown')

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "${PURPLE}[STEP]${NC} $1"
}

# Banner
echo -e "${CYAN}"
cat << 'EOF'
================================================================
🎮 AutoGen DekuDeals - Local Build Pipeline
================================================================
EOF
echo -e "${NC}"

# Change to project directory
cd "$PROJECT_DIR"

log_info "Starting local build pipeline..."
log_info "Version: $VERSION"
log_info "Build Date: $BUILD_DATE"
log_info "VCS Ref: $VCS_REF"
echo ""

# ===================================================================
# STEP 1: Environment Validation
# ===================================================================
log_step "🔍 Environment Validation"

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    log_error "Docker is not installed or not in PATH"
    exit 1
fi

# Check if Docker daemon is running
if ! docker info &> /dev/null; then
    log_error "Docker daemon is not running"
    exit 1
fi

# Check Python version
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1)
    log_info "Python: $PYTHON_VERSION"
else
    log_warning "Python3 not found in PATH"
fi

log_success "Environment validation completed"
echo ""

# ===================================================================
# STEP 2: Code Quality Checks
# ===================================================================
log_step "🔍 Code Quality Checks"

# Check for basic Python syntax errors
if command -v python3 &> /dev/null; then
    log_info "Checking Python syntax..."
    
    if python3 -m py_compile enhanced_cli.py; then
        log_success "enhanced_cli.py syntax OK"
    else
        log_error "enhanced_cli.py syntax error"
        exit 1
    fi
    
    if python3 -m py_compile agent_tools.py; then
        log_success "agent_tools.py syntax OK"
    else
        log_error "agent_tools.py syntax error"
        exit 1
    fi
    
    if python3 -m py_compile autogen_agents.py; then
        log_success "autogen_agents.py syntax OK"
    else
        log_error "autogen_agents.py syntax error"
        exit 1
    fi
else
    log_warning "Skipping Python syntax checks (Python3 not available)"
fi

log_success "Code quality checks completed"
echo ""

# ===================================================================
# STEP 3: Security Scan
# ===================================================================
log_step "🔒 Security Scan"

log_info "Scanning for potential secrets..."

# Check for potential API keys in code
if grep -r "sk-[a-zA-Z0-9]" --include="*.py" . 2>/dev/null; then
    log_error "Potential API keys found in code!"
    echo "Please remove any hardcoded API keys from your source code."
    exit 1
fi

# Check for hardcoded api_key assignments
HARDCODED_KEYS=$(grep -r "api_key.*=" --include="*.py" . 2>/dev/null | grep -v "OPENAI_API_KEY" || true)
if [[ -n "$HARDCODED_KEYS" ]]; then
    log_warning "Potential hardcoded API keys found:"
    echo "$HARDCODED_KEYS"
fi

log_success "Security scan completed"
echo ""

# ===================================================================
# STEP 4: Build Docker Image
# ===================================================================
log_step "🐳 Building Docker Image"

log_info "Building Docker image with version $VERSION..."

# Build the Docker image
if docker build \
    --build-arg BUILD_DATE="$BUILD_DATE" \
    --build-arg VERSION="$VERSION" \
    --build-arg VCS_REF="$VCS_REF" \
    --tag "autogen-dekudeals:$VERSION" \
    --tag "autogen-dekudeals:latest" \
    --tag "autogen-dekudeals:dev" \
    . ; then
    log_success "Docker build completed successfully"
else
    log_error "Docker build failed"
    exit 1
fi

echo ""

# ===================================================================
# STEP 5: Test Docker Image
# ===================================================================
log_step "🧪 Testing Docker Image"

log_info "Testing basic Docker image functionality..."

# Test info command
if docker run --rm "autogen-dekudeals:$VERSION" info > /dev/null 2>&1; then
    log_success "Docker info command test passed"
else
    log_error "Docker info command test failed"
    exit 1
fi

# Test health command
if docker run --rm "autogen-dekudeals:$VERSION" health > /dev/null 2>&1; then
    log_success "Docker health command test passed"
else
    log_error "Docker health command test failed"
    exit 1
fi

log_success "Docker image tests completed"
echo ""

# ===================================================================
# STEP 6: Generate Build Report
# ===================================================================
log_step "📋 Generating Build Report"

BUILD_REPORT="build-report-$(date +'%Y%m%d-%H%M%S').txt"

cat > "$BUILD_REPORT" << EOF
AutoGen DekuDeals - Local Build Report
======================================

Build Information:
- Version: $VERSION
- Build Date: $BUILD_DATE
- VCS Ref: $VCS_REF
- Builder: $(whoami)@$(hostname)
- Build Script: $0

Environment:
- OS: $(uname -s) $(uname -r)
- Docker: $(docker --version)
- Python: ${PYTHON_VERSION:-Not available}

Docker Images Created:
- autogen-dekudeals:$VERSION
- autogen-dekudeals:latest
- autogen-dekudeals:dev

Image Size:
$(docker images autogen-dekudeals:$VERSION --format "table {{.Repository}}:{{.Tag}}\t{{.Size}}" | tail -n 1)

Quick Start Commands:
docker run -it --env-file .env autogen-dekudeals:$VERSION cli
docker run --rm autogen-dekudeals:$VERSION info
docker run --rm autogen-dekudeals:$VERSION health

Build Status: SUCCESS
Build Completed: $(date)
EOF

log_info "Build report saved to: $BUILD_REPORT"
echo ""

# ===================================================================
# Summary
# ===================================================================
echo -e "${GREEN}"
cat << 'EOF'
================================================================
🎉 LOCAL BUILD COMPLETED SUCCESSFULLY!
================================================================
EOF
echo -e "${NC}"

echo -e "${CYAN}Docker Images Created:${NC}"
docker images autogen-dekudeals --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"

echo ""
echo -e "${CYAN}Quick Test Commands:${NC}"
echo -e "${YELLOW}docker run --rm autogen-dekudeals:$VERSION info${NC}"
echo -e "${YELLOW}docker run --rm autogen-dekudeals:$VERSION health${NC}"
echo -e "${YELLOW}docker run -it --env-file .env autogen-dekudeals:$VERSION cli${NC}"

echo ""
echo -e "${GREEN}✅ Build pipeline completed successfully!${NC}"
echo -e "${BLUE}📋 Build report: $BUILD_REPORT${NC}" 