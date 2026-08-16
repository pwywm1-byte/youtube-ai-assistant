"""Test script to verify system is working."""

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_imports():
    """Test if all modules can be imported."""
    logger.info("🧪 Testing imports...")

    try:
        logger.info("  ✓ Importing config...")
        from config import settings  # noqa: F401

        logger.info("  ✓ Importing agents...")
        from agents import BaseAgent  # noqa: F401

        logger.info("  ✓ Importing workflow...")
        from workflow import ContentOrchestrator  # noqa: F401

        logger.info("  ✓ Importing API...")
        from api.main import app  # noqa: F401

        logger.info("  ✓ Importing tasks...")
        from tasks import debug_task  # noqa: F401

        logger.info("✅ All imports successful!")
        return True

    except Exception as e:
        logger.error(f"❌ Import failed: {str(e)}")
        return False


def test_config():
    """Test configuration loading."""
    logger.info("\n🧪 Testing configuration...")

    try:
        from config import settings  # noqa: F401

        logger.info(f"  ✓ API Host: {settings.API_HOST}")
        logger.info(f"  ✓ API Port: {settings.API_PORT}")
        logger.info(f"  ✓ Log Level: {settings.LOG_LEVEL}")
        logger.info(
            f"  ✓ Environment: {'Development' if settings.DEVELOPMENT_MODE else 'Production'}"
        )

        logger.info("✅ Configuration loaded!")
        return True

    except Exception as e:
        logger.error(f"❌ Config failed: {str(e)}")
        return False


def test_api():
    """Test API initialization."""
    logger.info("\n🧪 Testing API...")

    try:
        from api.main import app  # noqa: F401

        logger.info("  ✓ API initialized")
        logger.info(f"  ✓ Title: {app.title}")
        logger.info(f"  ✓ Version: {app.version}")
        logger.info(f"  ✓ Routes: {len(app.routes)}")

        logger.info("✅ API ready!")
        return True

    except Exception as e:
        logger.error(f"❌ API failed: {str(e)}")
        return False


if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("YOUTUBE AI ASSISTANT - SYSTEM TEST")
    logger.info("=" * 60 + "\n")

    results = {
        "Imports": test_imports(),
        "Configuration": test_config(),
        "API": test_api(),
    }

    logger.info("\n" + "=" * 60)
    logger.info("TEST RESULTS:")
    logger.info("=" * 60)

    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        logger.info(f"{test_name}: {status}")

    logger.info("=" * 60)

    if all(results.values()):
        logger.info("\n✅ ALL TESTS PASSED - System is ready!")
    else:
        logger.error("\n❌ Some tests failed - Fix issues above")
