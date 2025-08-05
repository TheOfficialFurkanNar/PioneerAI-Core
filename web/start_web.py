#!/usr/bin/env python3
"""
PioneerAI Web Interface Startup Script
Professional production-ready Flask application launcher with CLI support.
"""

import os
import sys
import argparse
import logging
from pathlib import Path
from dotenv import load_dotenv

# Add project root to Python path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

def setup_logging(debug_mode: bool = False) -> None:
    """Configure professional logging setup"""
    log_level = logging.DEBUG if debug_mode else logging.INFO
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    # Ensure logs directory exists
    log_dir = PROJECT_ROOT / "logs"
    log_dir.mkdir(exist_ok=True)

    # Configure logging
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[
            logging.FileHandler(log_dir / "web_server.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )

def load_environment() -> dict:
    """Load and validate environment configuration"""
    # Load environment files in order of priority
    env_files = [
        PROJECT_ROOT / ".env",
        PROJECT_ROOT / ".env.safe",
        PROJECT_ROOT / ".env.local"
    ]

    for env_file in env_files:
        if env_file.exists():
            load_dotenv(env_file)
            logging.info(f"Loaded environment from: {env_file}")
            break
    else:
        logging.warning("No environment file found, using system environment variables")

    # Validate critical environment variables
    config = {
        'JWT_SECRET': os.getenv('JWT_SECRET', 'pioneer-ai-secret-key-2024'),
        'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY', ''),
        'ALLOWED_ORIGINS': os.getenv('ALLOWED_ORIGINS', '*'),
        'DATABASE_PATH': os.getenv('DATABASE_PATH', str(PROJECT_ROOT / "data" / "users.db")),
        'CORS_ORIGINS': os.getenv('CORS_ORIGINS', '*')
    }

    # Warn about missing critical configurations
    if not config['OPENAI_API_KEY']:
        logging.warning("OPENAI_API_KEY not set - AI features may not work")

    if config['JWT_SECRET'] == 'pioneer-ai-secret-key-2024':
        logging.warning("Using default JWT_SECRET - set JWT_SECRET environment variable for production")

    return config

def check_database_initialization() -> bool:
    """Check if database is properly initialized"""
    try:
        from web.database import init_database, test_database_connection

        logging.info("Initializing database...")
        init_database()

        if test_database_connection():
            logging.info("Database connection successful")
            return True
        else:
            logging.error("Database connection failed")
            return False

    except Exception as e:
        logging.error(f"Database initialization failed: {e}")
        return False

def create_flask_app(config: dict, debug_mode: bool = False):
    """Create and configure Flask application"""
    try:
        from web.chat_interface import app

        # Configure Flask app
        app.config['DEBUG'] = debug_mode
        app.config['JWT_SECRET'] = config['JWT_SECRET']
        app.config['CORS_ORIGINS'] = config['CORS_ORIGINS']

        # Set environment variables for the app
        os.environ['JWT_SECRET'] = config['JWT_SECRET']
        os.environ['ALLOWED_ORIGINS'] = config['ALLOWED_ORIGINS']

        logging.info("Flask application configured successfully")
        return app

    except Exception as e:
        logging.error(f"Failed to create Flask application: {e}")
        raise

def add_static_file_routes(app):
    """Add static file serving routes for production"""
    from flask import send_from_directory

    @app.route('/')
    def serve_landing():
        """Serve landing page as root"""
        return send_from_directory('html', 'landing.html')

    @app.route('/html/<path:filename>')
    def serve_html(filename):
        """Serve HTML files"""
        return send_from_directory('html', filename)

    @app.route('/css/<path:filename>')
    def serve_css(filename):
        """Serve CSS files"""
        return send_from_directory('css', filename)

    @app.route('/js/<path:filename>')
    def serve_js(filename):
        """Serve JavaScript files"""
        return send_from_directory('js', filename)

    logging.info("Static file routes configured")

def print_startup_info(host: str, port: int, debug_mode: bool):
    """Print professional startup information"""
    print("\n" + "=" * 60)
    print("🧠 PioneerAI Web Interface")
    print("=" * 60)
    print(f"🌐 Server: http://{host}:{port}")
    print(f"🔧 Debug Mode: {'Enabled' if debug_mode else 'Disabled'}")
    print(f"📁 Project Root: {PROJECT_ROOT}")
    print(f"📊 Logs Directory: {PROJECT_ROOT / 'logs'}")
    print("=" * 60)
    print("📋 Available Endpoints:")
    print("  • /                    - Landing page")
    print("  • /html/login.html     - User login")
    print("  • /html/registry.html  - User registration")
    print("  • /html/dashboard.html - User dashboard")
    print("  • /html/index.html     - Chat interface")
    print("  • /auth/register       - Registration API")
    print("  • /auth/login          - Login API")
    print("  • /auth/logout         - Logout API")
    print("  • /auth/userinfo       - User info API")
    print("  • /ask/summary         - Chat API")
    print("  • /ask/summary/stream  - Streaming chat API")
    print("=" * 60)
    print("🚀 Server starting...")
    print()

def main():
    """Main application entry point"""
    parser = argparse.ArgumentParser(
        description="PioneerAI Web Interface - Professional Flask Application",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python start_web.py                    # Start with default settings
  python start_web.py --debug            # Start in debug mode
  python start_web.py --port 8080        # Start on port 8080
  python start_web.py --host 0.0.0.0     # Listen on all interfaces
  python start_web.py --debug --port 3000 --host localhost
        """
    )

    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug mode (default: False)'
    )

    parser.add_argument(
        '--port',
        type=int,
        default=5000,
        help='Port to run the server on (default: 5000)'
    )

    parser.add_argument(
        '--host',
        type=str,
        default='localhost',
        help='Host to bind the server to (default: localhost)'
    )

    parser.add_argument(
        '--no-db-check',
        action='store_true',
        help='Skip database initialization check'
    )

    args = parser.parse_args()

    # Setup logging
    setup_logging(args.debug)
    logger = logging.getLogger(__name__)

    try:
        logger.info("Starting PioneerAI Web Interface...")

        # Load environment configuration
        config = load_environment()

        # Check database initialization
        if not args.no_db_check:
            if not check_database_initialization():
                logger.error("Database initialization failed. Use --no-db-check to skip this check.")
                sys.exit(1)

        # Create Flask application
        app = create_flask_app(config, args.debug)

        # Add static file routes
        add_static_file_routes(app)

        # Print startup information
        print_startup_info(args.host, args.port, args.debug)

        # Start the server
        app.run(
            host=args.host,
            port=args.port,
            debug=args.debug,
            threaded=True
        )

    except KeyboardInterrupt:
        logger.info("Server shutdown requested by user")
        print("\n👋 PioneerAI Web Interface stopped.")

    except Exception as e:
        logger.error(f"Critical error: {e}")
        print(f"\n❌ Critical error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()