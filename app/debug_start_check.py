import sys
import os

# Add parent directory to path to allow importing app
sys.path.append(os.path.dirname(os.getcwd()))

try:
    from app.core.config import settings
    print(f"CWD: {os.getcwd()}")
    print(f"DEBUG={settings.DEBUG}")
    print(f"PROJECT_NAME={settings.PROJECT_NAME}")
except Exception as e:
    print(f"Error: {e}")
