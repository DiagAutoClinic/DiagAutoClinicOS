"""
test_build.py - Simple test to verify PyInstaller works
"""

print("=" * 60)
print("AutoDiag Build Test")
print("=" * 60)

# Test imports
try:
    import sys
    print(f"Python version: {sys.version}")
    
    # Test PyQt6
    try:
        from PyQt6 import QtCore
        print("✓ PyQt6 imported successfully")
    except ImportError as e:
        print(f"✗ PyQt6 import failed: {e}")
    
    # Test other critical imports
    imports_to_test = ['pandas', 'numpy', 'pyserial']
    
    for import_name in imports_to_test:
        try:
            __import__(import_name)
            print(f"✓ {import_name} imported successfully")
        except ImportError as e:
            print(f"✗ {import_name} import failed: {e}")
    
    print("\n" + "=" * 60)
    print("Import test complete!")
    print("If all imports succeed, PyInstaller should work.")
    
except Exception as e:
    print(f"Error: {e}")

input("\nPress Enter to exit...")