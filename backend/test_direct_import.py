import sys
import traceback

try:
    import app
    print("Import successful!")
    print(f"Has 'app' attribute: {hasattr(app, 'app')}")
    if hasattr(app, 'app'):
        print(f"App type: {type(app.app)}")
    print(f"Module attributes: {[attr for attr in dir(app) if not attr.startswith('_')]}")
except Exception as e:
    print(f"Import failed: {e}")
    traceback.print_exc()
