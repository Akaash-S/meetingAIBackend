#!/bin/bash

# AI Meeting Assistant - Docker Build Script
echo "🐳 Building AI Meeting Assistant Backend Docker Image"

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

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker is running
if ! docker info &> /dev/null; then
    print_error "Docker is not running. Please start Docker first."
    exit 1
fi

print_status "Docker is installed and running"

# Build the Docker image
print_status "Building Docker image..."
docker build -t ai-meeting-backend:latest .

if [ $? -eq 0 ]; then
    print_success "Docker image built successfully!"
else
    print_error "Docker build failed!"
    exit 1
fi

# Test the image
print_status "Testing Docker image..."
docker run --rm -d --name ai-meeting-test -p 5000:5000 \
    -e DATABASE_URL="postgresql://test:test@localhost:5432/test" \
    -e SECRET_KEY="test-secret-key" \
    ai-meeting-backend:latest

# Wait a moment for the container to start
sleep 5

# Check if container is running
if docker ps | grep -q ai-meeting-test; then
    print_success "Container is running!"
    
    # Test health endpoint
    print_status "Testing health endpoint..."
    sleep 10  # Give the app time to start
    
    if curl -f http://localhost:5000/api/health &> /dev/null; then
        print_success "Health endpoint is responding!"
    else
        print_warning "Health endpoint not responding (this is expected without database)"
    fi
    
    # Stop the test container
    print_status "Stopping test container..."
    docker stop ai-meeting-test
    print_success "Test container stopped"
else
    print_error "Container failed to start!"
    docker logs ai-meeting-test
    exit 1
fi

print_success "Docker build and test completed successfully!"
print_status "Image: ai-meeting-backend:latest"
print_status "Ready for deployment to Render!"

echo ""
echo "🚀 Next Steps:"
echo "1. Push your code to GitHub"
echo "2. Create a new Web Service on Render"
echo "3. Connect your GitHub repository"
echo "4. Set the root directory to 'backend'"
echo "5. Choose 'Docker' as the runtime"
echo "6. Add your environment variables"
echo "7. Deploy!"
