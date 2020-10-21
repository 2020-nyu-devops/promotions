"""
Package: service
Package for the application models and service routes
This module creates and configures the Flask app and sets up the logging
and SQL database
"""
import os
import sys
import logging
from flask import Flask

# Create Flask application
app = Flask(__name__)
app.config.from_object('config')

# pylint: disable=wrong-import-position
# Import the routes After the Flask app is created
from service import service, models

# pylint: disable=fixme
# Set up logging for production #TODO

app.logger.info(70 * "*")
app.logger.info("  P R O M O   S E R V I C E   R U N N I N G  ".center(70, "*"))
app.logger.info(70 * "*")

try:
    service.init_db()  # make our sqlalchemy tables
except Exception as error:
    app.logger.critical("%s: Cannot continue", error)
    # gunicorn requires exit code 4 to stop spawning workers when they die
    sys.exit(4)

app.logger.info("Service initialized!")
