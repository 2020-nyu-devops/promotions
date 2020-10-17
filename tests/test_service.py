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
from .factories import PromotionFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgres://postgres:postgres@localhost:5432/postgres"
)


######################################################################
#  T E S T   C A S E S
######################################################################
class TestPromotionService(TestCase):
    """ REST API Server Tests """

    @classmethod
    def setUpClass(cls):
        """ Run once before all tests """
        app.config['TESTING'] = True
        app.config['DEBUG'] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        init_db()

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        """ Runs before each test """
        db.drop_all()  # clean up the last tests
        db.create_all()  # create new tables
        self.app = app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def _create_promotions(self, count):
        """ Factory method to create promotions in bulk """
        promotions = []
        for _ in range(count):
            test_promotion = PromotionFactory()
            resp = self.app.post(
                "/promotions", json=test_promotion.serialize(), content_type="application/json"
            )
            self.assertEqual(
                resp.status_code, status.HTTP_201_CREATED, "Could not create test promotion"
            )
            new_promotion = resp.get_json()
            test_promotion.id = new_promotion["id"]
            promotions.append(test_promotion)
        return promotions

    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    def test_index(self):
        """ Test index call """
        resp = self.app.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_create_promotion(self):
        """ Create a new Promotion """
        test_promotion = PromotionFactory()
        logging.debug(test_promotion)
        resp = self.app.post(
            "/promotions", json=test_promotion.serialize(), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        # Check the data is correct
        new_promotion = resp.get_json()
        self.assertEqual(new_promotion["title"], test_promotion.title,
                         "Titles do not match")
        self.assertEqual(new_promotion["description"], test_promotion.description,
                         "Descriptions do not match")
        self.assertEqual(new_promotion["promo_code"], test_promotion.promo_code,
                         "Promo Codes do not match")
        self.assertEqual(new_promotion["promo_type"], test_promotion.promo_type.name,
                         "Promo Types do not match")
        self.assertEqual(new_promotion["amount"], test_promotion.amount,
                         "Amounts do not match")
        self.assertEqual(new_promotion["start_date"], test_promotion.start_date,
                         "Start Date does not match")
        self.assertEqual(new_promotion["end_date"], test_promotion.end_date,
                         "End Date does not match")
        self.assertEqual(new_promotion["is_site_wide"], test_promotion.is_site_wide,
                         "Is Site Wide bool does not match")

    def test_get_promotion(self):
        """ Get a single Promotion """
        # get the id of a promotion
        test_promotion = self._create_promotions(1)[0]
        resp = self.app.get(
            "/promotions/{}".format(test_promotion.id), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["title"], test_promotion.title)

    def test_get_promotion_not_found(self):
        """ Get a Promotion thats not found """
        resp = self.app.get("/promotions/0")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)


######################################################################
#   M A I N
######################################################################
if __name__ == "__main__":
    unittest.main()
