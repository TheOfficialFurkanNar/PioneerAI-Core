#!/usr/bin/env python3
"""
PioneerAI Web Server Startup Script
===================================

This script starts the PioneerAI web interface with proper configuration.
It includes database initialization, environment setup, and error handling.

Usage:
    python3 start_web.py [--port PORT] [--debug] [--host HOST]

Example:
    python3 start_web.py --port 5000 --debug
"""

import os
import sys
import argparse
import logging
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def setup_logging():
    """Setup basic logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('logs/web_server.log', mode='a')
        ]
    )

def ensure_directories():
    """Ensure required directories exist"""
    directories = ['logs', 'data', 'cache', 'summary_cache']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✓ Directory '{directory}' ready")

def check_environment():
    """Check if required environment variables are set"""
    required_vars = ['OPENAI_API_KEY']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("⚠️  Warning: The following environment variables are not set:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nThe application will work in demo mode, but AI features may not function.")
        print("Please set your OpenAI API key in the .env file or as an environment variable.")
        return False
    
    return True

def initialize_database():
    """Initialize the database"""
    try:
        from web.database import init_database
        init_database()
        print("✓ Database initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False

def start_server(host='0.0.0.0', port=5000, debug=False):
    """Start the Flask web server"""
    try:
        from web.chat_interface import app
        
        print(f"""
🧠 PioneerAI Web Interface Starting...
=====================================
Host: {host}
Port: {port}
Debug: {debug}
URL: http://localhost:{port}

Features Available:
• User Registration & Authentication
• JWT-based Session Management  
• AI Chat Interface (Turkish)
• Streaming & Standard Response Modes
• Responsive Web Design

Press Ctrl+C to stop the server
=====================================
        """)
        
        app.run(host=host, port=port, debug=debug, threaded=True)
        
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")
        sys.exit(1)

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Start PioneerAI Web Interface',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 start_web.py                    # Start with default settings
  python3 start_web.py --port 8080        # Start on port 8080
  python3 start_web.py --debug             # Start in debug mode
  python3 start_web.py --host 127.0.0.1   # Start on localhost only
        """
    )
    
    parser.add_argument('--host', default='0.0.0.0', 
                       help='Host to bind to (default: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=5000,
                       help='Port to bind to (default: 5000)')
    parser.add_argument('--debug', action='store_true',
                       help='Enable debug mode')
    
    args = parser.parse_args()
    
    print("🚀 PioneerAI Web Server Initialization")
    print("=" * 40)
    
    # Setup logging
    setup_logging()
    
    # Ensure directories exist
    ensure_directories()
    
    # Check environment
    env_ok = check_environment()
    
    # Initialize database
    db_ok = initialize_database()
    
    if not db_ok:
        print("❌ Critical error: Database initialization failed")
        sys.exit(1)
    
    if not env_ok:
        print("\n⚠️  Continuing in demo mode without OpenAI API key...")
        print("AI chat features will not work until you configure OPENAI_API_KEY")
    
    # Start the server
    start_server(host=args.host, port=args.port, debug=args.debug)

if __name__ == '__main__':
    main()