import os
import sys
import subprocess
from dotenv import load_dotenv

def main():
    # Load environment variables from .env file
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if not os.path.exists(env_path):
        print(f"Error: .env file not found at {env_path}")
        sys.exit(1)
    
    load_dotenv(env_path)
    
    # Verify required environment variables
    required_vars = ['APP_HOST', 'APP_PORT', 'CORS_ORIGINS']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"Error: Missing required environment variables: {', '.join(missing_vars)}")
        sys.exit(1)
    
    try:
        # Run the FastAPI application using uvicorn
        cmd = [
            sys.executable, "-m", "uvicorn",
            "main:app",
            "--host", os.getenv('APP_HOST', '0.0.0.0'),
            "--port", os.getenv('APP_PORT', '7171'),
            "--reload"
        ]
        
        print(f"Starting Financial Insights API server...")
        print(f"Host: {os.getenv('APP_HOST')}")
        print(f"Port: {os.getenv('APP_PORT')}")
        
        subprocess.run(cmd)
        
    except KeyboardInterrupt:
        print("\nShutting down server...")
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()