"""
Global Configuration for Application
"""
import os

# Get configuration from environment
# DATABASE_URI = os.getenv("DATABASE_URI", "sqlite:///../development.db")
DATABASE_URI = os.getenv(
    "DATABASE_URI", "mysql://root:DevOps_Promo@localhost:3306/promotion"
)

# Configure SQLAlchemy
SQLALCHEMY_DATABASE_URI = DATABASE_URI
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Secret for session management
# SECRET_KEY = os.getenv("SECRET_KEY", "s3cr3t-key-shhhh")
