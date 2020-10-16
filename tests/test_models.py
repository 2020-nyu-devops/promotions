"""
Test cases for Promotion Model

Test cases can be run with:
  nosetests
  coverage report -m
"""
import logging
import unittest
import os
from service.models import Promotion, DataValidationError, db
from service import app

######################################################################
#  P R O M O T I O N   M O D E L   T E S T   C A S E S
######################################################################
class TestPromotion(unittest.TestCase):
    """ Test Cases for Promotion Model """

    @classmethod
    def setUpClass(cls):
        """ This runs once before the entire test suite """
        app.debug = False
        pass

    @classmethod
    def tearDownClass(cls):
        """ This runs once after the entire test suite """
        pass

    def setUp(self):
        """ This runs before each test """
        pass

    def tearDown(self):
        """ This runs after each test """
        pass

######################################################################
#  P L A C E   T E S T   C A S E S   H E R E 
######################################################################

    def test_test(self):
        """ Test if the test environment works """
        self.assertTrue(True)


######################################################################
#   M A I N
######################################################################
if __name__ == "__main__":
    unittest.main()