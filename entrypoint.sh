#!/bin/bash
# ===================================================================
# 🎮 AutoGen DekuDeals - Docker Container Entrypoint
# Smart startup script with multiple operation modes
# ===================================================================

set -e  # Exit on any error

# ===================================================================
# Configuration and Environment
# ===================================================================
APP_NAME="AutoGen DekuDeals"
APP_VERSION="6.3.0"
APP_ENV="${APP_ENV:-production}"
WORKERS="${WORKERS:-1}"

# ===================================================================
# Logging Setup
# ===================================================================
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') [ENTRYPOINT] $1"
}

log_info() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') [INFO] $1"
}

log_warn() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') [WARN] $1"
}

log_error() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') [ERROR] $1"
}

# ===================================================================
# Environment Validation
# ===================================================================
validate_environment() {
    log_info "Validating environment..."
    
    # Check if OpenAI API key is set
    if [ -z "$OPENAI_API_KEY" ]; then
        log_warn "OPENAI_API_KEY not set. Some features may not work."
    else
        log_info "OpenAI API key detected (length: ${#OPENAI_API_KEY} chars)"
    fi
    
    # Check Python environment
    python_version=$(python --version 2>&1)
    log_info "Python version: $python_version"
    
    # Check required packages
    if python -c "import pyautogen" 2>/dev/null; then
        log_info "PyAutoGen package available"
    else
        log_error "PyAutoGen package not found!"
        exit 1
    fi
    
    if python -c "import openai" 2>/dev/null; then
        log_info "OpenAI package available"
    else
        log_error "OpenAI package not found!"
        exit 1
    fi
}

# ===================================================================
# Directory Setup
# ===================================================================
setup_directories() {
    log_info "Setting up application directories..."
    
    # Ensure required directories exist
    mkdir -p /app/logs
    mkdir -p /app/cache
    mkdir -p /app/data
    
    # Set proper permissions (in case volume mounted)
    chmod 755 /app/logs /app/cache /app/data
    
    log_info "Directory setup completed"
}

# ===================================================================
# Health Check Function
# ===================================================================
health_check() {
    log_info "Running health check..."
    
    # Basic Python health check
    if python -c "import pyautogen, openai; print('Health check passed')" 2>/dev/null; then
        log_info "Health check: PASSED"
        return 0
    else
        log_error "Health check: FAILED"
        return 1
    fi
}

# ===================================================================
# Application Modes
# ===================================================================

# API Mode (future: FastAPI server)
run_api() {
    log_info "Starting API server mode..."
    log_warn "API mode not yet implemented. Starting CLI mode instead."
    run_cli
}

# CLI Mode (Interactive)
run_cli() {
    log_info "Starting CLI mode..."
    exec python enhanced_cli.py --interactive
}

# CLI with specific command
run_cli_command() {
    local command="$1"
    log_info "Running CLI command: $command"
    exec python enhanced_cli.py $command
}

# Demo Mode
run_demo() {
    log_info "Starting demo mode..."
    exec python enhanced_cli.py --demo
}

# Batch Processing Mode
run_batch() {
    local batch_args="$*"
    log_info "Starting batch processing mode with args: $batch_args"
    exec python enhanced_cli.py --batch-analyze $batch_args
}

# Quick Analysis Mode
run_quick() {
    local game_name="$1"
    if [ -z "$game_name" ]; then
        log_error "Game name required for quick mode"
        exit 1
    fi
    log_info "Running quick analysis for: $game_name"
    exec python enhanced_cli.py --quick "$game_name"
}

# Testing Mode
run_tests() {
    log_info "Running test suite..."
    
    # Run basic tests
    if [ -f "/app/tests/test_phase1.py" ]; then
        log_info "Running Phase 1 tests..."
        python tests/test_phase1.py
    fi
    
    # Run comprehensive tests
    if [ -f "/app/examples/test_phase4_complete.py" ]; then
        log_info "Running Phase 4 complete tests..."
        python examples/test_phase4_complete.py
    fi
    
    log_info "Test execution completed"
}

# System Information
show_info() {
    log_info "=== $APP_NAME v$APP_VERSION ==="
    log_info "Environment: $APP_ENV"
    log_info "Python: $(python --version)"
    log_info "Working Directory: $(pwd)"
    log_info "User: $(whoami)"
    log_info "Available Commands:"
    log_info "  api        - Start API server (future)"
    log_info "  cli        - Interactive CLI mode"
    log_info "  demo       - Demo mode"
    log_info "  quick <game> - Quick game analysis"
    log_info "  batch <games> - Batch processing"
    log_info "  test       - Run test suite"
    log_info "  health     - Health check"
    log_info "  info       - Show this information"
}

# ===================================================================
# Main Entrypoint Logic
# ===================================================================
main() {
    # Banner
    echo "================================================================="
    echo "🎮 $APP_NAME v$APP_VERSION"
    echo "Enterprise-level game analysis with AutoGen agents"
    echo "Environment: $APP_ENV"
    echo "================================================================="
    
    # Setup
    validate_environment
    setup_directories
    
    # Parse command
    case "$1" in
        "api")
            run_api
            ;;
        "cli")
            run_cli
            ;;
        "demo")
            run_demo
            ;;
        "quick")
            shift
            run_quick "$@"
            ;;
        "batch")
            shift
            run_batch "$@"
            ;;
        "test")
            run_tests
            ;;
        "health")
            health_check
            ;;
        "info")
            show_info
            ;;
        "")
            # Default: API mode
            log_info "No command specified, defaulting to API mode"
            run_api
            ;;
        *)
            # Pass through to CLI with arguments
            log_info "Passing command to enhanced_cli.py: $*"
            exec python enhanced_cli.py "$@"
            ;;
    esac
}

# ===================================================================
# Signal Handling (Graceful Shutdown)
# ===================================================================
cleanup() {
    log_info "Received shutdown signal, cleaning up..."
    # Add any cleanup logic here
    exit 0
}

trap cleanup SIGTERM SIGINT

# ===================================================================
# Execute Main Function
# ===================================================================
main "$@" 