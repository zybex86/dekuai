#!/bin/bash
# ===================================================================
# 🎮 AutoGen DekuDeals - Local Deployment Script
# Professional deployment automation for local environment
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
DEFAULT_VERSION="latest"
DEFAULT_MODE="cli"

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

show_usage() {
    cat << EOF
${CYAN}🎮 AutoGen DekuDeals - Local Deployment Script${NC}

${YELLOW}Usage:${NC}
  $0 [OPTIONS] [COMMAND]

${YELLOW}Options:${NC}
  -v, --version VERSION    Docker image version (default: $DEFAULT_VERSION)
  -m, --mode MODE         Deployment mode (default: $DEFAULT_MODE)
  -e, --env-file FILE     Environment file (default: .env)
  -p, --port PORT         Port mapping (default: 8000:8000)
  -d, --detached          Run in detached mode
  -h, --help              Show this help message

${YELLOW}Deployment Modes:${NC}
  cli                     Interactive CLI mode
  api                     API server mode (future)
  demo                    Demo mode
  health                  Health check
  info                    System information
  quick GAME              Quick game analysis
  batch GAMES...          Batch analysis

${YELLOW}Examples:${NC}
  $0                                    # Interactive CLI (default)
  $0 -m demo                           # Demo mode
  $0 -m quick "Hollow Knight"          # Quick analysis
  $0 -v dev-20250618 -m cli            # Specific version
  $0 -d -m api                         # Detached API mode
  $0 --env-file custom.env -m cli      # Custom environment

${YELLOW}Pre-deployment Commands:${NC}
  $0 build                             # Build before deployment
  $0 test                              # Test deployment
  $0 status                            # Show deployment status
  $0 cleanup                           # Cleanup containers
EOF
}

build_image() {
    log_step "🔨 Building Docker Image"
    if [[ -f "$SCRIPT_DIR/local-build.sh" ]]; then
        log_info "Running local build script..."
        bash "$SCRIPT_DIR/local-build.sh"
        log_success "Build completed"
    else
        log_error "Build script not found: $SCRIPT_DIR/local-build.sh"
        exit 1
    fi
}

test_deployment() {
    log_step "🧪 Testing Deployment"
    
    # Check if image exists
    if ! docker images "autogen-dekudeals:$VERSION" --format "{{.Repository}}" | grep -q "autogen-dekudeals"; then
        log_error "Docker image autogen-dekudeals:$VERSION not found"
        log_info "Run '$0 build' first to build the image"
        exit 1
    fi
    
    # Test basic functionality
    log_info "Testing image functionality..."
    
    if docker run --rm "autogen-dekudeals:$VERSION" info > /dev/null 2>&1; then
        log_success "Info command test passed"
    else
        log_error "Info command test failed"
        exit 1
    fi
    
    if docker run --rm "autogen-dekudeals:$VERSION" health > /dev/null 2>&1; then
        log_success "Health command test passed"
    else
        log_error "Health command test failed"
        exit 1
    fi
    
    log_success "Deployment tests passed"
}

show_status() {
    log_step "📊 Deployment Status"
    
    echo -e "${CYAN}Available Images:${NC}"
    docker images autogen-dekudeals --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}" 2>/dev/null || {
        echo "No AutoGen DekuDeals images found"
    }
    
    echo ""
    echo -e "${CYAN}Running Containers:${NC}"
    docker ps --filter "ancestor=autogen-dekudeals" --format "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null || {
        echo "No running AutoGen DekuDeals containers"
    }
    
    echo ""
    echo -e "${CYAN}All Containers (including stopped):${NC}"
    docker ps -a --filter "ancestor=autogen-dekudeals" --format "table {{.Names}}\t{{.Image}}\t{{.Status}}" 2>/dev/null || {
        echo "No AutoGen DekuDeals containers found"
    }
}

cleanup_containers() {
    log_step "🧹 Cleaning Up Containers"
    
    # Stop running containers
    RUNNING_CONTAINERS=$(docker ps --filter "ancestor=autogen-dekudeals" -q)
    if [[ -n "$RUNNING_CONTAINERS" ]]; then
        log_info "Stopping running containers..."
        echo "$RUNNING_CONTAINERS" | xargs docker stop
        log_success "Stopped running containers"
    fi
    
    # Remove stopped containers
    STOPPED_CONTAINERS=$(docker ps -a --filter "ancestor=autogen-dekudeals" -q)
    if [[ -n "$STOPPED_CONTAINERS" ]]; then
        log_info "Removing stopped containers..."
        echo "$STOPPED_CONTAINERS" | xargs docker rm
        log_success "Removed stopped containers"
    fi
    
    if [[ -z "$RUNNING_CONTAINERS" && -z "$STOPPED_CONTAINERS" ]]; then
        log_info "No AutoGen DekuDeals containers to clean up"
    fi
}

validate_environment() {
    log_step "🔍 Environment Validation"
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed or not in PATH"
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        log_error "Docker daemon is not running"
        exit 1
    fi
    
    # Check image existence
    if ! docker images "autogen-dekudeals:$VERSION" --format "{{.Repository}}" | grep -q "autogen-dekudeals"; then
        log_error "Docker image autogen-dekudeals:$VERSION not found"
        log_info "Available images:"
        docker images autogen-dekudeals --format "  - {{.Repository}}:{{.Tag}}" 2>/dev/null || echo "  None found"
        log_info "Run '$0 build' to build the image"
        exit 1
    fi
    
    # Check environment file
    if [[ -f "$ENV_FILE" ]]; then
        log_success "Environment file found: $ENV_FILE"
        
        # Check for OpenAI API key
        if grep -q "OPENAI_API_KEY=" "$ENV_FILE" && ! grep -q "OPENAI_API_KEY=sk-your-" "$ENV_FILE"; then
            log_success "OpenAI API key detected in environment file"
        else
            log_warning "OpenAI API key not found or not configured in $ENV_FILE"
            log_info "Some features may not work without a valid API key"
        fi
    else
        log_warning "Environment file not found: $ENV_FILE"
        log_info "Creating minimal environment file..."
        cat > "$ENV_FILE" << EOF
# AutoGen DekuDeals Environment Configuration
OPENAI_API_KEY=your-openai-api-key-here
APP_ENV=development
VERSION=$VERSION
EOF
        log_info "Please edit $ENV_FILE and add your OpenAI API key"
    fi
    
    log_success "Environment validation completed"
}

deploy_container() {
    log_step "🚀 Deploying Container"
    
    # Build Docker run command
    DOCKER_CMD="docker run"
    
    # Add detached flag if requested
    if [[ "$DETACHED" == "true" ]]; then
        DOCKER_CMD="$DOCKER_CMD -d"
        CONTAINER_NAME="autogen-dekudeals-$(date +'%Y%m%d-%H%M%S')"
        DOCKER_CMD="$DOCKER_CMD --name $CONTAINER_NAME"
    else
        DOCKER_CMD="$DOCKER_CMD --rm -it"
    fi
    
    # Add environment file
    DOCKER_CMD="$DOCKER_CMD --env-file $ENV_FILE"
    
    # Add volume mounts for persistent data
    DOCKER_CMD="$DOCKER_CMD -v $PROJECT_DIR/cache:/app/cache"
    DOCKER_CMD="$DOCKER_CMD -v $PROJECT_DIR/logs:/app/logs"
    
    # Add port mapping if API mode
    if [[ "$MODE" == "api" ]]; then
        DOCKER_CMD="$DOCKER_CMD -p $PORT"
    fi
    
    # Add image and command
    DOCKER_CMD="$DOCKER_CMD autogen-dekudeals:$VERSION $MODE"
    
    # Add additional arguments
    if [[ -n "$EXTRA_ARGS" ]]; then
        DOCKER_CMD="$DOCKER_CMD $EXTRA_ARGS"
    fi
    
    log_info "Deployment command: $DOCKER_CMD"
    
    if [[ "$DETACHED" == "true" ]]; then
        log_info "Starting container in detached mode..."
        eval "$DOCKER_CMD"
        log_success "Container started: $CONTAINER_NAME"
        log_info "Monitor with: docker logs -f $CONTAINER_NAME"
        log_info "Stop with: docker stop $CONTAINER_NAME"
    else
        log_info "Starting interactive container..."
        log_info "Press Ctrl+C to stop the container"
        echo ""
        eval "$DOCKER_CMD"
    fi
}

# Parse command line arguments
VERSION="$DEFAULT_VERSION"
MODE="$DEFAULT_MODE"
ENV_FILE=".env"
PORT="8000:8000"
DETACHED="false"
EXTRA_ARGS=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -v|--version)
            VERSION="$2"
            shift 2
            ;;
        -m|--mode)
            MODE="$2"
            shift 2
            ;;
        -e|--env-file)
            ENV_FILE="$2"
            shift 2
            ;;
        -p|--port)
            PORT="$2"
            shift 2
            ;;
        -d|--detached)
            DETACHED="true"
            shift
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        build)
            build_image
            exit 0
            ;;
        test)
            test_deployment
            exit 0
            ;;
        status)
            show_status
            exit 0
            ;;
        cleanup)
            cleanup_containers
            exit 0
            ;;
        quick)
            MODE="quick"
            shift
            EXTRA_ARGS="$*"
            break
            ;;
        batch)
            MODE="batch"
            shift
            EXTRA_ARGS="$*"
            break
            ;;
        *)
            MODE="$1"
            shift
            EXTRA_ARGS="$*"
            break
            ;;
    esac
done

# Change to project directory
cd "$PROJECT_DIR"

# Banner
echo -e "${CYAN}"
cat << 'EOF'
================================================================
🚀 AutoGen DekuDeals - Local Deployment
================================================================
EOF
echo -e "${NC}"

log_info "Version: $VERSION"
log_info "Mode: $MODE"
log_info "Environment File: $ENV_FILE"
if [[ "$MODE" == "api" ]]; then
    log_info "Port Mapping: $PORT"
fi
if [[ "$DETACHED" == "true" ]]; then
    log_info "Detached Mode: Enabled"
fi
echo ""

# Execute deployment pipeline
validate_environment
deploy_container

echo ""
log_success "Deployment completed!" 