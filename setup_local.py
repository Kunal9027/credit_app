#!/usr/bin/env python
"""
Setup script for local development environment
"""
import os
import sys
import subprocess
import platform
import socket

def check_redis_connection():
    """Check if Redis is running locally"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(("localhost", 6379))
        s.close()
        return True
    except (socket.error, ConnectionRefusedError):
        return False

def main():
    print("Setting up local development environment for Credit Approval System...")
    
    # Create data directory if it doesn't exist
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
    os.makedirs(data_dir, exist_ok=True)
    print(f"Data directory created at {data_dir}")
    
    # Check if virtual environment exists
    venv_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'venv')
    if not os.path.exists(venv_dir):
        print("Virtual environment not found. Please create one using:")
        print("python -m venv venv")
        print("Then activate it and run this script again.")
        return
    
    # Check if requirements are installed
    try:
        import django
        print(f"Django {django.__version__} is installed.")
    except ImportError:
        print("Django is not installed. Installing requirements...")
        pip_cmd = [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"]
        subprocess.run(pip_cmd)
    
    # Run migrations
    print("Running database migrations...")
    manage_py = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'credit_project', 'manage.py')
    subprocess.run([sys.executable, manage_py, "makemigrations", "credit_app"])
    subprocess.run([sys.executable, manage_py, "migrate"])
    
    # Check Redis connection
    redis_running = check_redis_connection()
    if redis_running:
        print("\n✅ Redis is running and accessible at localhost:6379")
    else:
        print("\n⚠️ Redis is not running or not accessible at localhost:6379")
        print("For Celery to work properly, you need Redis running.")
        if platform.system() == "Windows":
            print("For Windows, download Redis from https://github.com/microsoftarchive/redis/releases")
            print("- Download the MSI installer (Redis-x64-3.0.504.msi is recommended)")
            print("- Run the installer and follow the instructions")
        else:
            print("For Linux/Mac, install Redis using your package manager")
        print("Alternatively, you can run just the Redis service from Docker:")
        print("docker run -d -p 6379:6379 redis:7")
    
    # Create sample data directory and inform user
    print("\nSetup complete!")
    print("\nTo run the application locally:")
    print(f"1. Place 'customer_data.xlsx' and 'loan_data.xlsx' in the {data_dir} directory")
    print("2. Run the development server:")
    print(f"   python {manage_py} runserver")
    print("3. To ingest data from Excel files:")
    print(f"   python {manage_py} ingest_data")

if __name__ == "__main__":
    main()