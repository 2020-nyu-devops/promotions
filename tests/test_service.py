"""
Promotion API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
"""
import os
import logging
import unittest
from datetime import datetime
from unittest import TestCase
from flask_api import status  # HTTP Status Codes
from service.models import Promotion, DataValidationError, db, PromoType, Product
from service import app
from service.service import init_db
from .factories import PromotionFactory
from freezegun import freeze_time


DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgres://postgres:postgres@localhost:5432/postgres"
)


######################################################################
#  T E S T   C A S E S
######################################################################
@freeze_time("2020-11-03")
class TestPromotionService(TestCase):
    """ REST API Server Tests """

    @classmethod
    def setUpClass(cls):
        """ Run once before all tests """
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
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
                "/promotions",
                json=test_promotion.serialize(),
                content_type="application/json",
            )
            self.assertEqual(
                resp.status_code,
                status.HTTP_201_CREATED,
                "Could not create test promotion",
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
            "/promotions",
            json=test_promotion.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        # Check the data is correct
        new_promotion = resp.get_json()
        self.assertEqual(
            new_promotion["title"], test_promotion.title, "Titles do not match"
        )
        self.assertEqual(
            new_promotion["description"],
            test_promotion.description,
            "Descriptions do not match",
        )
        self.assertEqual(
            new_promotion["promo_code"],
            test_promotion.promo_code,
            "Promo Codes do not match",
        )
        self.assertEqual(
            new_promotion["promo_type"],
            test_promotion.promo_type.name,
            "Promo Types do not match",
        )
        self.assertEqual(
            new_promotion["amount"], test_promotion.amount, "Amounts do not match"
        )
        self.assertEqual(
            new_promotion["start_date"],
            test_promotion.start_date.isoformat(),
            "Start Date does not match",
        )
        self.assertEqual(
            new_promotion["end_date"],
            test_promotion.end_date.isoformat(),
            "End Date does not match",
        )
        self.assertEqual(
            new_promotion["is_site_wide"],
            test_promotion.is_site_wide,
            "Is Site Wide bool does not match",
        )

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

    def test_list_promotion(self):
        """ List all promotions in the database """

        # create two promotions
        test_promotion00 = self._create_promotions(1)[0]
        test_promotion01 = self._create_promotions(1)[0]

        # if it gets 200 status, we pass
        resp = self.app.get("/promotions")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        # check that the ID of test promos match JSON returned
        data = resp.get_json()
        self.assertEqual(data[0]["id"], test_promotion00.id)
        self.assertEqual(data[1]["id"], test_promotion01.id)

    def test_update_promotion(self):
        """ Update an existing Promotion """
        # create a promotion to update
        test_promotion = PromotionFactory()
        resp = self.app.post(
            "/promotions",
            json=test_promotion.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        # update the promotion
        new_promotion = resp.get_json()
        new_promotion["title"] = "unknown"
        resp = self.app.put(
            "/promotions/{}".format(new_promotion["id"]),
            json=new_promotion,
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        updated_promotion = resp.get_json()
        self.assertEqual(updated_promotion["title"], "unknown")

        # check that trying to update a non-existent promotion returns 404 not found
        resp = self.app.put(
            "/promotions/{}".format("999999999999999"),
            json=new_promotion,
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_promotion(self):
        """ Delete a Promotion """
        test_promotion = self._create_promotions(1)[0]
        resp = self.app.delete(
            "/promotions/{}".format(test_promotion.id), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(resp.data), 0)
        # make sure they are deleted
        resp = self.app.get(
            "/promotions/{}".format(test_promotion.id), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    # If you call the DELETE function on a promotion that doesn't exist, should return OK
    def test_delete_promotion_not_exist(self):
        resp = self.app.delete(
            "/promotions/{}".format("9999999999999999"), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_query_promotion_list_by_site_wide(self):
        """ Query all promotions in the database by site-wide """
        # Create a set of promotions
        promotions, is_site_wide_list = [], [True, False, True]
        for site_wide in is_site_wide_list:
            test_promotion = PromotionFactory()
            test_promotion.is_site_wide = site_wide
            resp = self.app.post(
                "/promotions",
                json=test_promotion.serialize(),
                content_type="application/json",
            )
            new_promotion = resp.get_json()
            promotions.append(new_promotion)
            logging.debug(new_promotion)
        resp = self.app.get("/promotions", query_string=f"is_site_wide={True}")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        for promotion, site_wide in zip(promotions, is_site_wide_list):
            if site_wide:
                self.assertIn(promotion, data)
            else:
                self.assertNotIn(promotion, data)

    def test_query_promotion(self):
        """ Query all promotions in the database by multiple parameters """
        product_1 = Product()
        product_1.id = 100

        product_2 = Product()
        product_2.id = 200

        db.session.add(product_1)
        db.session.add(product_2)

        # Define the test cases
        test_cases = [
            {
                "title": "0",
                "promo_code": "XYZ0000",
                "promo_type": PromoType.DISCOUNT,
                "amount": 50,
                "is_site_wide": False,
                "start_date": datetime(2020, 10, 17),
                "end_date": datetime(2020, 10, 21),
            },
            {
                "title": "1",
                "promo_code": "XYZ0001",
                "promo_type": PromoType.DISCOUNT,
                "amount": 10,
                "is_site_wide": True,
                "start_date": datetime(2020, 10, 21),
                "end_date": datetime(2020, 10, 23),
            },
            {
                "title": "2",
                "promo_code": "XYZ0002",
                "promo_type": PromoType.BOGO,
                "amount": 2,
                "is_site_wide": False,
                "start_date": datetime(2020, 10, 14),
                "end_date": datetime(2020, 10, 18),
            },
            {
                "title": "3",
                "promo_code": "XYZ0003",
                "promo_type": PromoType.DISCOUNT,
                "amount": 20,
                "is_site_wide": False,
                "start_date": datetime(2020, 10, 14),
                "end_date": datetime(2021, 10, 18),
            },
        ]
        tests = [
            ("is_site_wide=true", 1),
            ("is_site_wide=true&product=100", 0),
            ("is_site_wide=false", 3),
            ("is_site_wide=false&product=200", 1),
            ("promo_code=XYZ0004", 0),
            ("promo_code=XYZ0003", 1),
            ("promo_code=XYZ0003&is_site_wide=false", 1),
            ("amount=20&is_site_wide=false", 1),
            ("amount=20&is_site_wide=true", 0),
            ("promo_type=DISCOUNT&is_site_wide=true", 1),
            ("promo_type=BOGO", 1),
            ("start_date=Sat, 17 Oct 2020 00:00:00 GMT", 2),
            ("start_date=Tue, 14 Oct 2020 00:00:00 GMT&end_date=Wed, 18 Oct 2020 00:00:00 GMT", 1),
            ("duration=4", 3),
            ("active=0", 3),
            ("active=1", 1),
            ("product=100", 3),
            ("product=200", 1),
            ("", 4),
        ]
        # Create the set of Promotions
        for test_case in test_cases:
            test_promotion = Promotion()
            if not test_case["is_site_wide"]:
                test_promotion.products = [product_1]
                if test_case["promo_code"] == "XYZ0003":
                    test_promotion.products.append(product_2)

            for attribute in test_case:
                setattr(test_promotion, attribute, test_case[attribute])

            resp = self.app.post(
                "/promotions",
                json=test_promotion.serialize(),
                content_type="application/json",
            )
        # Carry out the tests
        for query_str, length_of_result in tests:
            logging.debug(query_str)
            resp = self.app.get("/promotions", query_string=query_str)
            self.assertEqual(resp.status_code, status.HTTP_200_OK)
            data = resp.get_json()
            print(query_str)
            self.assertEqual(len(data), length_of_result)

    def test_cancel_promotion(self):
        """ Cancel a promotion """

        # try to cancel it before it's in there
        resp = self.app.post(
            "/promotions/{}/cancel".format(1), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

        # create a new promotion
        test_promotion = self._create_promotions(1)[0]

        # cancel the promotion
        resp = self.app.post(
            "/promotions/{}/cancel".format(test_promotion.id),
            content_type="application/json",
        )

        # if it gets 200 status, we pass
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_invalid_content_type(self):
        resp = self.app.post(
            "/promotions", json="This is a string", content_type="text/html"
        )
        self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_bad_request(self):
        """ Test Bad Request """
        resp = self.app.post(
            "/promotions", json="{'test': 'promotion'}", content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_apply_best_promotions(self):
        """ Test Apply Best Promotion """
        # API: /promotions/apply?product_id=product_price

        # Product - Promotion mapping
        # Product 1
        ## Available: Promo 1, Promo 2 (Store-wide), Promo 3, Promo 6 (Store-wide, Expired)
        ## Best: Promo 3 (BOGO)
        # Product 2
        ## Available: Promo 1, Promo 2 (Store-wide), Promo_4, Promo 6 (Store-wide, Expired)
        ## Best: Promo 4 (80%)
        # Product 3
        ## Available: Promo 2 (Store-wide), Promo 6 (Store-wide, Expired)
        ## Best: Promo 2 (10%)
        # Product 4
        ## Available: Promo 2 (Store-wide), Promo 5, Promo 6 (Store-wide, Expired)
        ## Best: Promo 5 (FIXED, 150)

        product_1 = Product()
        product_1.id = 100
        product_2 = Product()
        product_2.id = 200
        product_3 = Product()
        product_3.id = 300
        product_4 = Product()
        product_4.id = 400

        db.session.add(product_1)
        db.session.add(product_2)
        db.session.add(product_3)
        db.session.add(product_4)

        # Define the promotions
        promotions = [
            {
                "promo_code": "promo_code_1",
                "promo_type": PromoType.DISCOUNT,
                "amount": 40,
                "is_site_wide": False,
                "start_date": datetime(2020, 9, 2),
                "end_date": datetime(2021, 10, 21),
            },
            {
                "promo_code": "promo_code_2",
                "promo_type": PromoType.DISCOUNT,
                "amount": 10,
                "is_site_wide": True,
                "start_date": datetime(2020, 8, 21),
                "end_date": datetime(2021, 10, 23),
            },
            {
                "promo_code": "promo_code_3",
                "promo_type": PromoType.BOGO,
                "amount": 1,
                "is_site_wide": False,
                "start_date": datetime(2020, 9, 1),
                "end_date": datetime(2021, 5, 30),
            },
            {
                "promo_code": "promo_code_4",
                "promo_type": PromoType.DISCOUNT,
                "amount": 80,
                "is_site_wide": False,
                "start_date": datetime(2020, 10, 14),
                "end_date": datetime(2021, 5, 18),
            },
            {
                "promo_code": "promo_code_5",
                "promo_type": PromoType.FIXED,
                "amount": 150,
                "is_site_wide": False,
                "start_date": datetime(2020, 10, 14),
                "end_date": datetime(2021, 10, 18),
            },
            {
                "promo_code": "promo_code_6",
                "promo_type": PromoType.DISCOUNT,
                "amount": 80,
                "is_site_wide": True,
                "start_date": datetime(2020, 9, 14),
                "end_date": datetime(2020, 10, 15),
            },
        ]
        tests = [
            ("100=1000&200=5000", []),
            (
                "100=1000&200=5000&300=268&400=255",
                [
                    {"100": "promo_code_3"},
                    {"200": "promo_code_4"},
                    {"300": "promo_code_2"},
                    {"400": "promo_code_5"},
                ],
            ),
            ("", []),
        ]
        # Carry out the tests without promotions in the system
        for cart, result in tests[:1]:
            resp = self.app.get("/promotions/apply", query_string=cart)
            self.assertEqual(resp.status_code, status.HTTP_200_OK)
            data = resp.get_json()
            self.assertEqual(data, result)

        # Create the set of Promotions
        logging.debug("Creating promotions")
        for promo in promotions:
            test_promotion = PromotionFactory()
            for attribute in promo:
                setattr(test_promotion, attribute, promo[attribute])
            if promo["promo_code"] == "promo_code_1":
                test_promotion.products.append(product_1)
                test_promotion.products.append(product_2)
            elif promo["promo_code"] == "promo_code_3":
                test_promotion.products.append(product_1)
            elif promo["promo_code"] == "promo_code_4":
                test_promotion.products.append(product_2)
            elif promo["promo_code"] == "promo_code_5":
                test_promotion.products.append(product_4)
            logging.debug(
                f" Promo: {promo['promo_code']} (Promo ID: {test_promotion.id}): Products - {test_promotion.products}"
            )
            self.app.post(
                "/promotions",
                json=test_promotion.serialize(),
                content_type="application/json",
            )
        logging.debug("Promotions created")
        # Carry out the tests
        for cart, result in tests[1:]:
            logging.debug(cart)
            resp = self.app.get("/promotions/apply", query_string=cart)
            self.assertEqual(resp.status_code, status.HTTP_200_OK)
            data = resp.get_json()
            self.assertEqual(data, result)


######################################################################
#   M A I N
######################################################################
if __name__ == "__main__":
    unittest.main()
