#!/bin/bash
# ==========================================
# Robot Diagnosis System - Rollback Script
# ==========================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE=${1:-production}
REVISION=${2:-0}
TIMEOUT=${3:-300}
RELEASE_NAME="robot-diagnosis-prod"

# Functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    if ! command -v kubectl &> /dev/null; then
        log_error "kubectl is not installed"
        exit 1
    fi
    
    if ! command -v helm &> /dev/null; then
        log_error "Helm is not installed"
        exit 1
    fi
    
    if ! kubectl cluster-info &> /dev/null; then
        log_error "Cannot connect to Kubernetes cluster"
        exit 1
    fi
    
    log_info "Prerequisites check passed"
}

# Show current status
show_current_status() {
    log_info "Current deployment status in namespace: $NAMESPACE"
    
    echo ""
    echo "=== Helm Release History ==="
    helm history $RELEASE_NAME -n $NAMESPACE --max 5
    
    echo ""
    echo "=== Running Pods ==="
    kubectl get pods -n $NAMESPACE -o wide
    
    echo ""
    echo "=== Service Status ==="
    kubectl get svc -n $NAMESPACE
    
    echo ""
    echo "=== Ingress Status ==="
    kubectl get ingress -n $NAMESPACE
}

# Perform rollback
perform_rollback() {
    log_info "Starting rollback process..."
    
    if [ "$REVISION" -eq "0" ]; then
        log_info "Rolling back to previous revision"
    else
        log_info "Rolling back to revision $REVISION"
    fi
    
    # Perform Helm rollback
    helm rollback $RELEASE_NAME $REVISION -n $NAMESPACE
    
    if [ $? -eq 0 ]; then
        log_info "Helm rollback completed successfully"
    else
        log_error "Helm rollback failed"
        exit 1
    fi
}

# Wait for rollback to complete
wait_for_rollback() {
    log_info "Waiting for rollback to complete (timeout: ${TIMEOUT}s)..."
    
    local deployments=("backend" "frontend" "java-service")
    local failed=0
    
    for deployment in "${deployments[@]}"; do
        log_info "Waiting for $deployment deployment..."
        if ! kubectl rollout status deployment/$RELEASE_NAME-$deployment -n $NAMESPACE --timeout=${TIMEOUT}s; then
            log_error "Rollback failed for $deployment"
            failed=1
        fi
    done
    
    if [ $failed -eq 0 ]; then
        log_info "All deployments rolled back successfully"
    else
        log_error "Some deployments failed to rollback"
        exit 1
    fi
}

# Verify application health
verify_health() {
    log_info "Verifying application health..."
    
    # Get ingress host
    local host=$(kubectl get ingress -n $NAMESPACE -o jsonpath='{.items[0].spec.rules[0].host}')
    
    if [ -z "$host" ]; then
        log_warn "Could not determine ingress host, skipping health check"
        return
    fi
    
    # Wait a bit for services to be ready
    sleep 10
    
    # Check health endpoint
    local max_attempts=10
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        log_info "Health check attempt $attempt/$max_attempts"
        
        if curl -sf https://$host/actuator/health > /dev/null 2>&1; then
            log_info "Application is healthy"
            return 0
        fi
        
        sleep 5
        attempt=$((attempt + 1))
    done
    
    log_warn "Health check failed after $max_attempts attempts"
    return 1
}

# Send notification
send_notification() {
    local status=$1
    local message=$2
    
    log_info "Sending notification: $message"
    
    # Slack notification (if webhook is configured)
    if [ -n "$SLACK_WEBHOOK_URL" ]; then
        curl -s -X POST -H 'Content-type: application/json' \
            --data "{\"text\":\"Rollback $status in $NAMESPACE: $message\"}" \
            $SLACK_WEBHOOK_URL > /dev/null 2>&1 || true
    fi
    
    # PagerDuty notification (if key is configured)
    if [ -n "$PAGERDUTY_KEY" ] && [ "$status" == "FAILED" ]; then
        curl -s -X POST -H 'Content-type: application/json' \
            -H "Authorization: Token token=$PAGERDUTY_KEY" \
            --data "{\"incident\":{\"type\":\"incident\",\"title\":\"Rollback Failed in $NAMESPACE\",\"service\":{\"id\":\"$PAGERDUTY_SERVICE_ID\",\"type\":\"service_reference\"},\"urgency\":\"high\"}}" \
            https://api.pagerduty.com/incidents > /dev/null 2>&1 || true
    fi
}

# Create rollback report
create_report() {
    local report_file="rollback-report-$(date +%Y%m%d-%H%M%S).txt"
    
    log_info "Creating rollback report: $report_file"
    
    cat > $report_file << EOF
Rollback Report
===============
Date: $(date)
Namespace: $NAMESPACE
Release: $RELEASE_NAME
Revision: $REVISION

Pod Status:
$(kubectl get pods -n $NAMESPACE)

Events:
$(kubectl get events -n $NAMESPACE --sort-by='.lastTimestamp' | tail -20)

Helm History:
$(helm history $RELEASE_NAME -n $NAMESPACE)
EOF
    
    log_info "Report saved to: $report_file"
}

# Main function
main() {
    echo "=========================================="
    echo "Robot Diagnosis System - Rollback Script"
    echo "=========================================="
    echo ""
    
    # Show usage if no arguments
    if [ $# -eq 0 ]; then
        echo "Usage: $0 <namespace> [revision] [timeout]"
        echo ""
        echo "Arguments:"
        echo "  namespace  - Kubernetes namespace (default: production)"
        echo "  revision   - Helm revision to rollback to (default: 0 = previous)"
        echo "  timeout    - Timeout in seconds (default: 300)"
        echo ""
        echo "Examples:"
        echo "  $0 production           # Rollback production to previous version"
        echo "  $0 staging 5            # Rollback staging to revision 5"
        echo "  $0 production 0 600     # Rollback with 10 minute timeout"
        exit 1
    fi
    
    log_info "Starting rollback process..."
    log_info "Namespace: $NAMESPACE"
    log_info "Revision: $REVISION"
    log_info "Timeout: ${TIMEOUT}s"
    
    # Execute rollback steps
    check_prerequisites
    show_current_status
    
    echo ""
    read -p "Do you want to proceed with the rollback? (y/N) " -n 1 -r
    echo ""
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "Rollback cancelled by user"
        exit 0
    fi
    
    perform_rollback
    wait_for_rollback
    verify_health
    create_report
    
    log_info "Rollback completed successfully!"
    send_notification "SUCCESS" "Rollback to revision $REVISION completed successfully"
    
    echo ""
    echo "=========================================="
    log_info "Rollback process completed"
    echo "=========================================="
}

# Run main function
main "$@"
