#!/bin/bash

# US Crime Statistics REST API - Setup Script
# This script automates the setup process for the Django application

echo "========================================"
echo "US Crime Statistics REST API - Setup"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed. Please install Python 3.x"
    exit 1
fi

echo "Python version:"
python3 --version
echo ""

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "Installing dependencies..."
pip install -r requirements.txt

# Run migrations
echo ""
echo "Running database migrations..."
python manage.py makemigrations
python manage.py migrate

# Create superuser
echo ""
echo "========================================"
echo "Creating admin superuser..."
echo "========================================"
echo ""
echo "Please use these credentials for consistency:"
echo "Username: admin"
echo "Password: admin123"
echo ""
python manage.py createsuperuser

# Load data
echo ""
echo "========================================"
echo "Loading crime data from CSV..."
echo "========================================"
python manage.py load_crime_data data/state_crime.csv --clear

# Run tests
echo ""
echo "========================================"
echo "Running tests to verify installation..."
echo "========================================"
python manage.py test crime_api

echo ""
echo "========================================"
echo "Setup Complete!"
echo "========================================"
echo ""
echo "To start the development server:"
echo "  source venv/bin/activate"
echo "  python manage.py runserver"
echo ""
echo "Then visit: http://127.0.0.1:8000/"
echo ""
echo "Admin interface: http://127.0.0.1:8000/admin/"
echo "  Username: admin"
echo "  Password: admin123"
echo ""
