import uvicorn
import os
from dotenv import load_dotenv

if __name__ == "__main__":
    # Load environment variables
    load_dotenv()
    
    # Run the server with reload enabled
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8080,
        reload=True,  # Enable auto-reload
        reload_dirs=["./"],  # Watch the current directory for changes
        workers=1,  # Use single worker in debug mode
        log_level="debug"
    ) 