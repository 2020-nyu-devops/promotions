"""
Promotion API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
"""
import os
import logging
import unittest
from unittest import TestCase
from unittest.mock import MagicMock, patch
from flask_api import status  # HTTP Status Codes
from service.models import Promotion, DataValidationError, db
from service import app
from service.service import init_db

######################################################################
#  T E S T   C A S E S
######################################################################
class TestPromotionService(TestCase):
    """ REST API Server Tests """

    @classmethod
    def setUpClass(cls):
        """ This runs once before the entire test suite """
        app.debug = False
        app.testing = True
        pass

    @classmethod
    def tearDownClass(cls):
        """ This runs once after the entire test suite """
        pass

    def setUp(self):
        """ This runs before each test """
        self.app = app.test_client()


    def tearDown(self):
        """ This runs after each test """
        pass

######################################################################
#  P L A C E   T E S T   C A S E S   H E R E 
######################################################################

    def test_index(self):
        """ Test index call """
        resp = self.app.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)


######################################################################
#   M A I N
######################################################################
if __name__ == "__main__":
    unittest.main()
