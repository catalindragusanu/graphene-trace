"""Quick test script to verify setup"""
import sys

def test_imports():
    """Test that all required packages are installed"""
    print("Testing imports...")
    try:
        import fastapi
        import uvicorn
        import sqlalchemy
        import alembic
        import pydantic
        import slowapi
        print("✓ All packages imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_config():
    """Test configuration loading"""
    print("\nTesting configuration...")
    try:
        from app.config import settings
        print(f"✓ Configuration loaded")
        print(f"  - Database URL: {settings.DATABASE_URL}")
        print(f"  - Debug mode: {settings.DEBUG}")
        print(f"  - CORS origins: {settings.CORS_ORIGINS}")
        return True
    except Exception as e:
        print(f"✗ Configuration error: {e}")
        return False

def test_database():
    """Test database connection"""
    print("\nTesting database connection...")
    try:
        from sqlalchemy import create_engine, text
        from app.config import settings

        engine = create_engine(settings.DATABASE_URL)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            print(f"✓ Database connected successfully")
            print(f"  - PostgreSQL version: {version[:50]}...")
            return True
    except Exception as e:
        print(f"✗ Database connection error: {e}")
        print("  Make sure PostgreSQL is running:")
        print("  docker ps | findstr graphene-trace-db")
        return False

def test_models():
    """Test that models can be imported"""
    print("\nTesting models...")
    try:
        from app.models.user import User
        from app.models.frame import Frame
        from app.models.metric import Metric
        from app.models.alert import Alert
        print("✓ All models imported successfully")
        return True
    except Exception as e:
        print(f"✗ Model import error: {e}")
        return False

def main():
    print("=" * 60)
    print("Graphene Trace - Setup Verification")
    print("=" * 60)

    tests = [
        ("Package Imports", test_imports),
        ("Configuration", test_config),
        ("Database Connection", test_database),
        ("Models", test_models),
    ]

    results = []
    for name, test_func in tests:
        try:
            results.append(test_func())
        except Exception as e:
            print(f"\n✗ Unexpected error in {name}: {e}")
            results.append(False)

    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)

    passed = sum(results)
    total = len(results)

    for i, (name, _) in enumerate(tests):
        status = "✓ PASS" if results[i] else "✗ FAIL"
        print(f"{status} - {name}")

    print(f"\nResults: {passed}/{total} tests passed")

    if passed == total:
        print("\n✓ All tests passed! You're ready to start the server.")
        print("\nNext steps:")
        print("  1. Run: .\\venv\\Scripts\\uvicorn.exe app.main:app --reload")
        print("  2. Visit: http://localhost:8000/docs")
        return 0
    else:
        print("\n✗ Some tests failed. Please fix the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
