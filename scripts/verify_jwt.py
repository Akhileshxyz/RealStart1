
try:
    import jwt
    print(f"Successfully imported jwt. Version: {jwt.__version__}")
except ImportError as e:
    print(f"Failed to import jwt: {e}")
