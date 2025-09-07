#!/usr/bin/env python3
"""
AI Trading System Startup Script
This script helps users get started with the trading system quickly.
"""

import os
import sys
import subprocess
import asyncio
from pathlib import Path

def print_banner():
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                   AI Trading System                          ║
║            Advanced Stock Analysis & AI Insights            ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def check_requirements():
    """Check if required tools are available."""
    print("🔍 Checking requirements...")
    
    # Check Python version
    if sys.version_info < (3, 11):
        print("❌ Python 3.11+ is required")
        return False
    print("✅ Python version OK")
    
    # Check if we're in the right directory
    if not Path("requirements.txt").exists():
        print("❌ Please run this script from the project root directory")
        return False
    print("✅ Project directory OK")
    
    # Check for .env file
    if not Path(".env").exists():
        print("⚠️  .env file not found. Creating from template...")
        if Path(".env.example").exists():
            subprocess.run(["cp", ".env.example", ".env"], shell=True)
            print("📝 Please edit .env file with your API keys")
        else:
            create_env_file()
    
    return True

def create_env_file():
    """Create a basic .env file."""
    env_content = """# AI Trading System Configuration

# API Keys (Required for AI features)
OPENAI_API_KEY=your_openai_api_key_here
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key_here

# Database Configuration
DATABASE_URL=postgresql://trading_user:secure_password@localhost:5432/trading_db
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=trading_db
DATABASE_USER=trading_user
DATABASE_PASSWORD=secure_password

# Redis Configuration
REDIS_URL=redis://localhost:6379/0
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=redis_password

# Application Settings
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO
API_HOST=0.0.0.0
API_PORT=8000

# Trading Configuration
DEFAULT_STOP_LOSS=0.02
DEFAULT_POSITION_SIZE=0.1
UPDATE_INTERVAL_MINUTES=15
"""
    with open(".env", "w") as f:
        f.write(env_content)
    print("✅ Created .env file")

def check_docker():
    """Check if Docker is available."""
    try:
        result = subprocess.run(["docker", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Docker is available")
            return True
    except FileNotFoundError:
        pass
    
    print("❌ Docker not found")
    return False

def check_docker_compose():
    """Check if Docker Compose is available."""
    try:
        result = subprocess.run(["docker-compose", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Docker Compose is available")
            return True
    except FileNotFoundError:
        pass
    
    # Try docker compose (new syntax)
    try:
        result = subprocess.run(["docker", "compose", "version"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Docker Compose is available")
            return True
    except FileNotFoundError:
        pass
    
    print("❌ Docker Compose not found")
    return False

def install_local_dependencies():
    """Install Python dependencies locally."""
    print("📦 Installing Python dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        return False

def start_docker_environment():
    """Start the system using Docker."""
    print("🐳 Starting Docker environment...")
    
    try:
        # Try docker-compose first
        result = subprocess.run(["docker-compose", "-f", "docker-compose.yml", "-f", "docker-compose.dev.yml", "up", "-d"], 
                              capture_output=True, text=True)
        if result.returncode != 0:
            # Try docker compose (new syntax)
            result = subprocess.run(["docker", "compose", "-f", "docker-compose.yml", "-f", "docker-compose.dev.yml", "up", "-d"], 
                                  capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Docker environment started successfully")
            print_access_info()
            return True
        else:
            print(f"❌ Failed to start Docker environment: {result.stderr}")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting Docker: {e}")
        return False

def start_local_environment():
    """Start the system locally."""
    print("🚀 Starting local development server...")
    
    try:
        # Change to the project directory
        os.chdir(Path(__file__).parent)
        
        # Start the FastAPI server
        import uvicorn
        uvicorn.run(
            "src.api.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
        
    except ImportError:
        print("❌ uvicorn not installed. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "uvicorn[standard]"], check=True)
        import uvicorn
        uvicorn.run(
            "src.api.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )

def print_access_info():
    """Print information about how to access the system."""
    print("\n" + "="*60)
    print("🎉 AI Trading System is now running!")
    print("="*60)
    print("📊 API Documentation: http://localhost:8000/docs")
    print("🩺 Health Check:      http://localhost:8000/health")
    print("🔧 PgAdmin:          http://localhost:5050")
    print("🗄️  Redis Commander:  http://localhost:8081")
    print("="*60)
    print("\n📝 Example API calls:")
    print("curl http://localhost:8000/analyze/AAPL")
    print("curl http://localhost:8000/signals/TSLA")
    print("curl http://localhost:8000/patterns/GOOGL")
    print("\n⚠️  Remember to set your OpenAI API key in the .env file for AI features!")

async def test_system():
    """Test if the system is working correctly."""
    print("🧪 Testing system functionality...")
    
    try:
        import aiohttp
        async with aiohttp.ClientSession() as session:
            # Test health endpoint
            async with session.get("http://localhost:8000/health") as response:
                if response.status == 200:
                    print("✅ API is responding")
                    data = await response.json()
                    print(f"   Status: {data.get('status', 'unknown')}")
                else:
                    print(f"❌ API health check failed: {response.status}")
            
            # Test a simple analysis
            async with session.get("http://localhost:8000/analyze/AAPL") as response:
                if response.status == 200:
                    print("✅ Stock analysis working")
                else:
                    print(f"⚠️  Stock analysis returned: {response.status}")
                    
    except Exception as e:
        print(f"❌ System test failed: {e}")

def show_menu():
    """Show the main menu."""
    print("\n🎯 Choose how to start the AI Trading System:")
    print("1. 🐳 Docker (Recommended - Full system with database)")
    print("2. 🐍 Local Python (Development - API only)")
    print("3. 🧪 Test existing system")
    print("4. 📚 Show documentation")
    print("5. 🚪 Exit")
    
    choice = input("\nEnter your choice (1-5): ").strip()
    return choice

def show_documentation():
    """Show basic documentation."""
    print("\n📚 Quick Start Guide:")
    print("-" * 50)
    print("1. Set up your .env file with API keys")
    print("2. Choose Docker (full system) or Local (API only)")
    print("3. Access the API at http://localhost:8000/docs")
    print("4. Try analyzing a stock: /analyze/AAPL")
    print("5. Get trading signals: /signals/TSLA")
    print("6. Detect patterns: /patterns/GOOGL")
    print("\n🔑 Required API Keys:")
    print("- OpenAI API key (for AI analysis)")
    print("- Alpha Vantage key (optional, for additional data)")
    print("\n📖 Full documentation: README.md")

def main():
    """Main function."""
    print_banner()
    
    if not check_requirements():
        sys.exit(1)
    
    while True:
        choice = show_menu()
        
        if choice == "1":
            # Docker environment
            if check_docker() and check_docker_compose():
                start_docker_environment()
                break
            else:
                print("❌ Docker is required for this option")
                
        elif choice == "2":
            # Local environment
            if install_local_dependencies():
                start_local_environment()
                break
            else:
                print("❌ Failed to set up local environment")
                
        elif choice == "3":
            # Test system
            asyncio.run(test_system())
            
        elif choice == "4":
            # Documentation
            show_documentation()
            
        elif choice == "5":
            # Exit
            print("👋 Goodbye!")
            sys.exit(0)
            
        else:
            print("❌ Invalid choice. Please try again.")

if __name__ == "__main__":
    main()