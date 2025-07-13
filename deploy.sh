#!/bin/bash

# Sales Agent Commission v1.1.0 - Deployment Script
# This script automates the deployment of the Sales Agent Commission app

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to get user input
get_input() {
    local prompt="$1"
    local default="$2"
    local input
    
    if [ -n "$default" ]; then
        read -p "$prompt [$default]: " input
        echo "${input:-$default}"
    else
        read -p "$prompt: " input
        echo "$input"
    fi
}

# Main deployment function
deploy_app() {
    print_status "🚀 Sales Agent Commission v1.1.0 Deployment Script"
    echo "=================================================="
    
    # Check prerequisites
    print_status "Checking prerequisites..."
    
    if ! command_exists "bench"; then
        print_error "Bench command not found. Please install Frappe Framework first."
        exit 1
    fi
    
    if ! command_exists "python3"; then
        print_error "Python 3 not found. Please install Python 3."
        exit 1
    fi
    
    print_success "Prerequisites check passed"
    
    # Get deployment parameters
    print_status "Getting deployment parameters..."
    
    BENCH_PATH=$(get_input "Enter your Frappe bench path" "$(pwd)")
    SITE_NAME=$(get_input "Enter your site name" "")
    
    if [ -z "$SITE_NAME" ]; then
        print_error "Site name is required"
        exit 1
    fi
    
    # Validate bench path
    if [ ! -d "$BENCH_PATH" ]; then
        print_error "Bench path does not exist: $BENCH_PATH"
        exit 1
    fi
    
    if [ ! -f "$BENCH_PATH/apps/frappe/setup.py" ]; then
        print_error "Invalid bench path. Frappe not found in: $BENCH_PATH/apps/"
        exit 1
    fi
    
    # Check if site exists
    if [ ! -d "$BENCH_PATH/sites/$SITE_NAME" ]; then
        print_error "Site does not exist: $SITE_NAME"
        exit 1
    fi
    
    print_success "Parameters validated"
    
    # Pre-installation checks
    print_status "Running pre-installation checks..."
    
    # Check if app already exists
    if [ -d "$BENCH_PATH/apps/sales_agent_commission" ]; then
        print_warning "Sales Agent Commission app already exists"
        OVERWRITE=$(get_input "Do you want to overwrite it? (y/n)" "n")
        
        if [ "$OVERWRITE" = "y" ] || [ "$OVERWRITE" = "Y" ]; then
            print_status "Removing existing app..."
            rm -rf "$BENCH_PATH/apps/sales_agent_commission"
            print_success "Existing app removed"
        else
            print_error "Deployment cancelled"
            exit 1
        fi
    fi
    
    # Run fix script if available
    if [ -f "fix_installation.py" ]; then
        print_status "Running installation fix script..."
        python3 fix_installation.py
        print_success "Installation fixes applied"
    fi
    
    # Copy app files
    print_status "Copying app files..."
    
    if [ ! -d "sales_agent_commission" ]; then
        print_error "Sales Agent Commission app directory not found"
        exit 1
    fi
    
    cp -r sales_agent_commission "$BENCH_PATH/apps/"
    print_success "App files copied"
    
    # Set permissions
    print_status "Setting permissions..."
    chmod -R 755 "$BENCH_PATH/apps/sales_agent_commission"
    print_success "Permissions set"
    
    # Change to bench directory
    cd "$BENCH_PATH"
    
    # Install app
    print_status "Installing app..."
    if bench --site "$SITE_NAME" install-app sales_agent_commission; then
        print_success "App installed successfully"
    else
        print_error "App installation failed"
        exit 1
    fi
    
    # Migrate database
    print_status "Migrating database..."
    if bench --site "$SITE_NAME" migrate; then
        print_success "Database migration completed"
    else
        print_error "Database migration failed"
        exit 1
    fi
    
    # Restart services
    print_status "Restarting services..."
    if bench restart; then
        print_success "Services restarted"
    else
        print_warning "Service restart failed, you may need to restart manually"
    fi
    
    # Post-installation verification
    print_status "Running post-installation verification..."
    
    # Check if app is installed
    if bench --site "$SITE_NAME" list-apps | grep -q "sales_agent_commission"; then
        print_success "App is installed and listed"
    else
        print_error "App not found in installed apps list"
        exit 1
    fi
    
    # Verify doctypes
    print_status "Verifying doctypes..."
    DOCTYPE_COUNT=$(bench --site "$SITE_NAME" console --execute "import frappe; print(len(frappe.get_all('DocType', filters={'module': 'Sales Agent Commission'})))" 2>/dev/null || echo "0")
    
    if [ "$DOCTYPE_COUNT" -gt "5" ]; then
        print_success "Doctypes created successfully ($DOCTYPE_COUNT doctypes)"
    else
        print_warning "Some doctypes may not have been created properly"
    fi
    
    # Final success message
    echo ""
    print_success "🎉 Sales Agent Commission v1.1.0 deployed successfully!"
    echo ""
    echo "Next steps:"
    echo "1. Login to your ERPNext site: http://your-site"
    echo "2. Go to Selling module"
    echo "3. Look for 'Sales Commission' in the sidebar"
    echo "4. Create your first Sales Agent"
    echo ""
    echo "For support, check the documentation files:"
    echo "- README.md"
    echo "- INSTALLATION_GUIDE.md"
    echo "- INSTALLATION_TROUBLESHOOTING.md"
    echo ""
    print_success "Deployment completed successfully!"
}

# Function to create package
create_package() {
    print_status "Creating deployment package..."
    
    # Check if app directory exists
    if [ ! -d "sales_agent_commission" ]; then
        print_error "Sales Agent Commission app directory not found"
        exit 1
    fi
    
    # Create package directory
    PACKAGE_DIR="sales_agent_commission_v1.1.0_package"
    mkdir -p "$PACKAGE_DIR"
    
    # Copy app files
    cp -r sales_agent_commission "$PACKAGE_DIR/"
    
    # Copy documentation
    cp README.md INSTALLATION_GUIDE.md CHANGELOG.md DEPLOYMENT_PACKAGE.md "$PACKAGE_DIR/" 2>/dev/null || true
    cp INSTALLATION_TROUBLESHOOTING.md SYSTEM_DESIGN.md "$PACKAGE_DIR/" 2>/dev/null || true
    cp fix_installation.py deploy.sh "$PACKAGE_DIR/" 2>/dev/null || true
    
    # Create archive
    tar -czf "${PACKAGE_DIR}.tar.gz" "$PACKAGE_DIR"
    
    print_success "Package created: ${PACKAGE_DIR}.tar.gz"
    
    # Cleanup
    rm -rf "$PACKAGE_DIR"
}

# Function to show help
show_help() {
    echo "Sales Agent Commission v1.1.0 - Deployment Script"
    echo ""
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Options:"
    echo "  deploy     Deploy the app to ERPNext (default)"
    echo "  package    Create deployment package"
    echo "  help       Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                    # Deploy the app"
    echo "  $0 deploy             # Deploy the app"
    echo "  $0 package            # Create package"
    echo "  $0 help               # Show help"
}

# Main script logic
case "${1:-deploy}" in
    "deploy")
        deploy_app
        ;;
    "package")
        create_package
        ;;
    "help"|"-h"|"--help")
        show_help
        ;;
    *)
        print_error "Unknown option: $1"
        show_help
        exit 1
        ;;
esac