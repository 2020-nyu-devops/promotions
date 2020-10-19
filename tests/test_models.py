"""
Test cases for Promotion Model

Test cases can be run with:
  nosetests
  coverage report -m
"""
import logging
import unittest
import os
from service.models import Promotion, DataValidationError, db, PromoType
from service import app
from .factories import PromotionFactory


DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgres://postgres:postgres@localhost:5432/postgres"
)


######################################################################
#  P R O M O T I O N   M O D E L   T E S T   C A S E S
######################################################################
class TestPromotion(unittest.TestCase):
    """ Test Cases for Promotion Model """

    @classmethod
    def setUpClass(cls):
        app.config['TESTING'] = True
        app.config['DEBUG'] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Promotion.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """ This runs once after the entire test suite """
        pass

    def setUp(self):
        db.drop_all()  # clean up the last tests
        db.create_all()  # make our sqlalchemy tables

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    def test_create_a_promotion(self):
        """ Create a promotion and assert that it exists """
        promotion = Promotion(
            title="test_create",
            promo_type=PromoType.DISCOUNT,
            amount=10,
            start_date="Sat, 17 Oct 2020 00:00:00 GMT",
            end_date="Sun, 18 Oct 2020 00:00:00 GMT",
            is_site_wide=True)
        self.assertTrue(promotion is not None)
        self.assertEqual(promotion.id, None)
        self.assertEqual(promotion.title, "test_create")
        self.assertEqual(promotion.promo_type, PromoType.DISCOUNT)
        self.assertEqual(promotion.amount, 10)
        self.assertEqual(promotion.start_date, "Sat, 17 Oct 2020 00:00:00 GMT")
        self.assertEqual(promotion.end_date, "Sun, 18 Oct 2020 00:00:00 GMT")
        self.assertEqual(promotion.is_site_wide, True)

    def test_add_a_promotion(self):
        """ Create a promotion and add it to the database """
        promotions = Promotion.all()
        self.assertEqual(promotions, [])
        promotion = Promotion(
            title="test_create",
            promo_type=PromoType.DISCOUNT,
            amount=10,
            start_date="Sat, 17 Oct 2020 00:00:00 GMT",
            end_date="Sun, 18 Oct 2020 00:00:00 GMT",
            is_site_wide=True)
        self.assertTrue(promotion != None)
        self.assertEqual(promotion.id, None)
        promotion.create()
        # Asert that it was assigned an id and shows up in the database
        self.assertEqual(promotion.id, 1)
        promotions = Promotion.all()
        self.assertEqual(len(promotions), 1)

    def test_test(self):
        """ Test if the test environment works """
        self.assertTrue(True)

    def test_find_promotion(self):
        """ Find a Promotion by ID """
        promotions = PromotionFactory.create_batch(3)
        for promotion in promotions:
            promotion.create()
        logging.debug(promotions)
        # find the 2nd promotion in the list
        promotion = Promotion.find(promotions[1].id)
        self.assertIsNot(promotion, None)
        self.assertEqual(promotion.id, promotions[1].id)
        self.assertEqual(promotion.title, promotions[1].title)
        self.assertEqual(promotion.description, promotions[1].description)
        self.assertEqual(promotion.promo_code, promotions[1].promo_code)
        self.assertEqual(promotion.promo_type, promotions[1].promo_type)
        self.assertEqual(promotion.amount, promotions[1].amount)
        self.assertEqual(promotion.start_date, promotions[1].start_date)
        self.assertEqual(promotion.end_date, promotions[1].end_date)
        self.assertEqual(promotion.is_site_wide, promotions[1].is_site_wide)


######################################################################
#   M A I N
######################################################################
if __name__ == "__main__":
    unittest.main()