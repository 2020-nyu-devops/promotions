"""
Test cases for Promotion Model

Test cases can be run with:
  nosetests
  coverage report -m
"""
import logging
import unittest
import os
from datetime import datetime
from werkzeug.exceptions import NotFound
from service.models import Promotion, Product, DataValidationError, db, PromoType
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
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Promotion.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """ This runs once after the entire test suite """

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
            start_date=datetime(2020, 10, 17),
            end_date=datetime(2020, 10, 18),
            is_site_wide=True,
        )
        self.assertTrue(promotion is not None)
        self.assertEqual(promotion.id, None)
        self.assertEqual(promotion.title, "test_create")
        self.assertEqual(promotion.promo_type, PromoType.DISCOUNT)
        self.assertEqual(promotion.amount, 10)
        self.assertEqual(promotion.start_date, datetime(2020, 10, 17))
        self.assertEqual(promotion.end_date, datetime(2020, 10, 18))
        self.assertEqual(promotion.is_site_wide, True)

    def test_create_a_product(self):
        products = Product.all()
        self.assertEqual(products, [])
        product = Product(id=123)
        self.assertTrue(product is not None)
        product.create()
        self.assertEqual(product.id, 123)
        products = Product.all()
        self.assertEqual(len(products), 1)


    def test_add_a_promotion(self):
        """ Create a promotion and add it to the database """
        promotions = Promotion.all()
        self.assertEqual(promotions, [])
        promotion = Promotion(
            title="test_create",
            promo_type=PromoType.DISCOUNT,
            amount=10,
            start_date=datetime(2020, 10, 17),
            end_date=datetime(2020, 10, 18),
            is_site_wide=True,
        )
        self.assertTrue(promotion is not None)
        self.assertEqual(promotion.id, None)
        promotion.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertEqual(promotion.id, 1)
        promotions = Promotion.all()
        self.assertEqual(len(promotions), 1)

    def test_create_a_promotion_associated_with_new_product(self):
        """ Create a promotion which is associated with a product thats not in our db yet"""
        promotions = Promotion.all()
        products = Product.all()
        self.assertEqual(promotions, [])
        self.assertEqual(products, [])

        promotion = Promotion(
            title="test_create",
            promo_type=PromoType.DISCOUNT,
            amount=10,
            start_date=datetime(2020, 10, 17),
            end_date=datetime(2020, 10, 18),
            is_site_wide=True,
        )
        product = Product(
            id=123
        )
        promotion.products.append(product)
        self.assertTrue(product is not None)
        promotion.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertEqual(promotion.id, 1)
        self.assertEqual(product.id, 123)
        products = Product.all()
        promotions = Promotion.all()
        self.assertEqual(len(products), 1)
        self.assertEqual(len(promotions), 1)


    def test_update_a_promotion(self):
        """ Update a Promotion """
        promotion = Promotion(
            title="test_create",
            promo_type=PromoType.DISCOUNT,
            amount=10,
            start_date=datetime(2020, 10, 17),
            end_date=datetime(2020, 10, 18),
            is_site_wide=True,
        )
        promotion.create()
        self.assertEqual(promotion.id, 1)
        # Change it and update it
        promotion.title = "test_update"
        promotion.update()
        self.assertEqual(promotion.id, 1)
        # Fetch it back and make sure the id hasn't changed
        # but the data did change
        promotions = Promotion.all()
        self.assertEqual(len(promotions), 1)
        self.assertEqual(promotions[0].title, "test_update")

    def test_update_a_promotion_fail(self):
        promotion = Promotion(
            title="test_create",
            promo_type=PromoType.DISCOUNT,
            amount=10,
            start_date=datetime(2020, 10, 17),
            end_date=datetime(2020, 10, 18),
            is_site_wide=True,
        )
        try:
            promotion.update()
        except:
            print("Update called with empty ID field")

    def test_delete_a_promotion(self):
        """ Delete a Promotion """
        promotion = Promotion(
            title="test_create",
            promo_type=PromoType.DISCOUNT,
            amount=10,
            start_date=datetime(2020, 10, 17),
            end_date=datetime(2020, 10, 18),
            is_site_wide=True,
        )
        promotion.create()
        self.assertEqual(len(Promotion.all()), 1)
        # delete the promotion and make sure it isn't in the database
        promotion.delete()
        self.assertEqual(len(Promotion.all()), 0)

    def test_test(self):
        """ Test if the test environment works """
        self.assertTrue(True)

    def test_serialize(self):
        """ Test serialization of a Promotion """
        promotion = Promotion(
            id=1,
            title="Halloween Special",
            description="Some items off in honor of the spookiest month.",
            promo_code="hween",
            promo_type=PromoType.DISCOUNT,
            amount=25,
            start_date=datetime(2020, 10, 20),
            end_date=datetime(2020, 11, 1),
            is_site_wide=True,
        )
        product_1 = Product()
        product_1.id = 123
        promotion.products.append(product_1)
        product_2 = Product()
        product_2.id = 456
        promotion.products.append(product_2)
        self.assertEqual(
            promotion.serialize(),
            {
                "id": 1,
                "title": "Halloween Special",
                "description": "Some items off in honor of the spookiest month.",
                "promo_code": "hween",
                "promo_type": "DISCOUNT",
                "amount": 25,
                "start_date": "2020-10-20T00:00:00",
                "end_date": "2020-11-01T00:00:00",
                "is_site_wide": True,
                "products": [123, 456],
            },
        )

    def test_deserialize(self):
        """ Test deserialization of a promotion """
        promotion = Promotion(
            id=2,
            title="Thanksgiving Special",
            description="Some items off in honor of the most grateful month.",
            promo_code="tgiving",
            promo_type=PromoType.DISCOUNT,
            amount=50,
            start_date=datetime(2020, 11, 1),
            end_date=datetime(2020, 11, 30),
            is_site_wide=False,
        )
        product_1 = Product()
        product_1.id = 123
        promotion.products.append(product_1)
        product_2 = Product()
        product_2.id = 456
        promotion.products.append(product_2)
        db.session.add(product_1)
        db.session.add(product_2)

        data = promotion.serialize()
        promotion.deserialize(data)

        self.assertNotEqual(promotion, None)
        self.assertEqual(promotion.id, 2)
        self.assertEqual(promotion.title, "Thanksgiving Special")
        self.assertEqual(
            promotion.description, "Some items off in honor of the most grateful month."
        )
        self.assertEqual(promotion.promo_code, "tgiving")
        self.assertEqual(promotion.amount, 50)
        self.assertEqual(promotion.start_date, "2020-11-01T00:00:00")
        self.assertEqual(promotion.end_date, "2020-11-30T00:00:00")
        self.assertEqual(promotion.is_site_wide, False)
        self.assertEqual(
            [product.id for product in promotion.products],
            [123, 456],
        )

    def test_deserialize_missing_data(self):
        """ Test deserialization of a Promotion with missing data """
        data = {"id": 1, "name": "kitty", "category": "cat"}
        promotion = Promotion()
        self.assertRaises(DataValidationError, promotion.deserialize, data)

    def test_deserialize_bad_data(self):
        """ Test deserialization of a Promotion with bad data """
        data = "this is not a dictionary"
        promotion = Promotion()
        self.assertRaises(DataValidationError, promotion.deserialize, data)

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

    def test_find_or_404_not_found(self):
        """ Find or return 404 NOT found """
        self.assertRaises(NotFound, Promotion.find_or_404, 0)


######################################################################
#   M A I N
######################################################################
if __name__ == "__main__":
    unittest.main()
