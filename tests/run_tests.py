#!/usr/bin/env python3
"""
Test runner for qdrant-mcp-server tests.
"""
import pytest
import sys
import os
import logging
import shutil

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("test_runner")

def main():
    """Run all tests."""
    logger.info("Starting Qdrant MCP Server tests")
    
    # Force SSL verification off for all tests
    os.environ["QDRANT_VERIFY_SSL"] = "False"
    logger.info("Disabled SSL verification for tests")
    
    # Add the parent directory to sys.path so we can import qdrant_mcp_server
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    sys.path.insert(0, project_root)
    
    # Check for test env file
    test_env_file = os.path.join(project_root, '.env.test')
    env_file = os.path.join(project_root, '.env')
    
    use_test_env = False
    if os.path.exists(test_env_file):
        logger.info(f"Test environment file found: {test_env_file}")
        # Temporarily rename .env.test to .env for the tests
        if os.path.exists(env_file):
            env_backup = f"{env_file}.backup"
            logger.info(f"Backing up existing .env to {env_backup}")
            shutil.copy2(env_file, env_backup)
        
        logger.info("Using test environment for testing")
        shutil.copy2(test_env_file, env_file)
        use_test_env = True
    else:
        logger.info("No test environment file found, using existing .env if available")
    
    try:
        # Run tests
        args = [
            "-xvs",  # x: stop on first failure, v: verbose, s: don't capture output
            "--tb=native",  # Use native traceback style
            os.path.dirname(__file__)  # Test directory
        ]
        
        result = pytest.main(args)
        
        if result == 0:
            logger.info("All tests passed!")
        else:
            logger.error(f"Some tests failed. Exit code: {result}")
        
        return result
    finally:
        # Restore original .env if we used the test env
        if use_test_env and os.path.exists(f"{env_file}.backup"):
            logger.info("Restoring original .env file")
            shutil.move(f"{env_file}.backup", env_file)

if __name__ == "__main__":
    sys.exit(main()) 