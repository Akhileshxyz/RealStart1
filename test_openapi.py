import json
from app.main import app

def test_openapi():
    print("Generating OpenAPI schema...")
    try:
        schema = app.openapi()
        print("OpenAPI Generation OK")
        # print(json.dumps(schema, indent=2))
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_openapi()
