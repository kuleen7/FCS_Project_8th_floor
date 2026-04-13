#!/bin/bash

# Setup Script for Secure Job Search Platform
# This script sets up the entire development environment

set -e  # Exit on any error

echo "🚀 Setting up Secure Job Search Platform..."
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Check if running on Ubuntu
if [ ! -f /etc/os-release ]; then
    print_error "Cannot determine OS. This script is designed for Ubuntu."
    exit 1
fi

# Update system packages
echo "📦 Updating system packages..."
sudo apt update
print_success "System packages updated"

# Install Python
echo "🐍 Installing Python 3.11..."
sudo apt install -y python3 python3-pip python3-venv python3-dev
print_success "Python installed"

# Install Node.js
echo "📦 Installing Node.js 18..."
if ! command -v node &> /dev/null; then
    curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
    sudo apt install -y nodejs
    print_success "Node.js installed"
else
    print_success "Node.js already installed"
fi

# Install PostgreSQL
echo "🐘 Installing PostgreSQL..."
if ! command -v psql &> /dev/null; then
    sudo apt install -y postgresql postgresql-contrib
    print_success "PostgreSQL installed"
else
    print_success "PostgreSQL already installed"
fi

# Install Nginx
echo "🌐 Installing Nginx..."
if ! command -v nginx &> /dev/null; then
    sudo apt install -y nginx
    print_success "Nginx installed"
else
    print_success "Nginx already installed"
fi

# Generate SSL certificate
echo "🔒 Generating SSL certificate..."
chmod +x generate-ssl.sh
./generate-ssl.sh
print_success "SSL certificate generated"

# Setup Backend
echo "🔧 Setting up backend..."
cd backend

# Create virtual environment
if [ ! -d "venv" ]; then
    python3 -m venv venv
    print_success "Virtual environment created"
fi

# Activate virtual environment and install dependencies
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
print_success "Backend dependencies installed"

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    cp .env.example .env
    print_warning "Created .env file from template - PLEASE UPDATE WITH YOUR VALUES"
fi

# Create uploads directory
mkdir -p uploads
print_success "Uploads directory created"

cd ..

# Setup Frontend
echo "⚛️  Setting up frontend..."
cd frontend

# Install dependencies
if [ ! -d "node_modules" ]; then
    npm install
    print_success "Frontend dependencies installed"
else
    print_success "Frontend dependencies already installed"
fi

cd ..

# Setup Database
echo "🗄️  Setting up database..."
print_warning "Please run the following commands to create the database:"
echo ""
echo "sudo -u postgres psql"
echo "CREATE DATABASE secure_job_platform;"
echo "CREATE USER jobplatform WITH PASSWORD 'your_secure_password';"
echo "GRANT ALL PRIVILEGES ON DATABASE secure_job_platform TO jobplatform;"
echo "\q"
echo ""
print_warning "Then update the DATABASE_URL in backend/.env file"

# Setup Nginx
echo "🌐 Configuring Nginx..."
print_warning "To configure Nginx, run:"
echo ""
echo "sudo cp nginx/nginx.conf /etc/nginx/sites-available/secure-job-platform"
echo "sudo ln -s /etc/nginx/sites-available/secure-job-platform /etc/nginx/sites-enabled/"
echo "sudo nginx -t"
echo "sudo systemctl restart nginx"
echo ""

# Final instructions
echo ""
echo "================================================================"
print_success "Setup completed!"
echo "================================================================"
echo ""
echo "📝 Next steps:"
echo ""
echo "1. Update database credentials:"
echo "   - Edit backend/.env file"
echo "   - Set DATABASE_URL with your password"
echo ""
echo "2. Create database:"
echo "   - Run the PostgreSQL commands shown above"
echo ""
echo "3. Start the backend:"
echo "   cd backend"
echo "   source venv/bin/activate"
echo "   uvicorn app.main:app --host 0.0.0.0 --port 8000 --ssl-keyfile=../ssl/key.pem --ssl-certfile=../ssl/cert.pem"
echo ""
echo "4. Start the frontend (in a new terminal):"
echo "   cd frontend"
echo "   HTTPS=true npm start"
echo ""
echo "5. Access the application:"
echo "   Frontend: https://localhost:3000"
echo "   Backend API: https://localhost:8000/api/docs"
echo ""
echo "⚠️  You will see browser warnings about self-signed certificates."
echo "   This is expected for development. Click 'Advanced' and 'Proceed'."
echo ""
print_success "All done! Happy coding! 🎉"
