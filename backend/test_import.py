import sys
import traceback

sys.path.insert(0, '.')

try:
    print("Attempting to import app...")
    from app import app
    print("Import successful!")
    print(f"Number of routes: {len(list(app.url_map.iter_rules()))}")
    print("Routes:")
    for rule in app.url_map.iter_rules():
        print(f"  {rule.methods} {rule.rule}")
except Exception as e:
    print(f"Error during import: {e}")
    traceback.print_exc()
