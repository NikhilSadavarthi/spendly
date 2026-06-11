import os
import tempfile
import pytest
from app import app as flask_app
import database.db as db_module

@pytest.fixture
def app():
    # Setup temporary database file
    db_fd, db_path = tempfile.mkstemp()
    
    # Override database path in db module
    old_database = db_module.DATABASE
    db_module.DATABASE = db_path
    
    flask_app.config.update({
        "TESTING": True,
        "SECRET_KEY": "test-secret-key"
    })

    # Initialize and seed database
    with flask_app.app_context():
        db_module.init_db()
        db_module.seed_db()

    yield flask_app

    # Teardown
    os.close(db_fd)
    if os.path.exists(db_path):
        os.unlink(db_path)
    
    # Restore original database path
    db_module.DATABASE = old_database

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def db(app):
    with app.app_context():
        yield db_module.get_db()
