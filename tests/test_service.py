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
from service.models import Promotion, DataValidationError, db, PromoType
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
        self.assertEqual(data[0]['id'], test_promotion00.id)
        self.assertEqual(data[1]['id'], test_promotion01.id)
    
    def test_update_promotion(self):
        """ Update an existing Promotion """
        # create a promotion to update
        test_promotion = PromotionFactory()
        resp = self.app.post(
            "/promotions", json=test_promotion.serialize(), content_type="application/json"
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
                "/promotions", json=test_promotion.serialize(), content_type="application/json"
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
        # Define the test cases
        test_cases = [
            {
                "promo_code": "XYZ0000",
                "promo_type": PromoType.DISCOUNT,
                "amount": 50,
                "is_site_wide": False,
                "start_date": "Sat, 17 Oct 2020 00:00:00 GMT",
                "end_date": "Wed, 21 Oct 2020 00:00:00 GMT"
            },
            { 
                "promo_code": "XYZ0001",
                "promo_type": PromoType.DISCOUNT,
                "amount": 10,
                "is_site_wide": True,
                "start_date": "Wed, 21 Oct 2020 00:00:00 GMT",
                "end_date": "Fri, 23 Oct 2020 00:00:00 GMT"
            },
            { 
                "promo_code": "XYZ0002",
                "promo_type": PromoType.BOGO,
                "amount": 2,
                "is_site_wide": False,
                "start_date": "Fri, 16 Oct 2020 00:00:00 GMT",
                "end_date": "Fri, 23 Oct 2020 00:00:00 GMT"
            },
            { 
                "promo_code": "XYZ0003",
                "promo_type": PromoType.DISCOUNT,
                "amount": 20,
                "is_site_wide": False,
                "start_date": "Wed, 14 Oct 2020 00:00:00 GMT",
                "end_date": "Sun, 18 Oct 2020 00:00:00 GMT"
            }
        ]
        tests = [
            (f"is_site_wide={True}", 1),
            (f"is_site_wide={False}", 3),
            (f"promo_code=XYZ0004", 0),
            (f"promo_code=XYZ0003", 1),
            (f"promo_code=XYZ0003&is_site_wide={False}", 1),
            (f"amount=20&is_site_wide={False}", 1),
            (f"amount=20&is_site_wide={True}", 0),
            (f"promo_type=DISCOUNT&is_site_wide={True}", 1),
            (f"promo_type=BOGO", 1),
            (f"start_date=Sat, 17 Oct 2020 00:00:00 GMT", 2),
            (f"start_date=Tue, 13 Oct 2020 00:00:00 GMT&end_date=Wed, 21 Oct 2020 00:00:00 GMT", 2),
            (f"duration=4", 3)
        ]
        # Create the set of Promotions
        for test_case in test_cases:
            test_promotion = PromotionFactory()
            for attribute in test_case:
                setattr(test_promotion, attribute, test_case[attribute])
            resp = self.app.post(
                "/promotions", json=test_promotion.serialize(), content_type="application/json"
            )
        # Carry out the tests
        for query_str, length_of_result in tests:
            logging.debug(query_str)
            resp = self.app.get("/promotions", query_string=query_str)
            self.assertEqual(resp.status_code, status.HTTP_200_OK)
            data = resp.get_json()
            self.assertEqual(len(data), length_of_result)
            
    def test_cancel_promotion(self):
        """ Cancel a promotion """
        
        # try to cancel it before it's in there
        resp = self.app.post('/promotions/cancel/{}'.format(1), content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        
        # create a new promotion
        test_promotion = self._create_promotions(1)[0]
        
        # cancel the promotion
        resp = self.app.post('/promotions/cancel/{}'.format(test_promotion.id), content_type='application/json')
                
        # if it gets 200 status, we pass
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

######################################################################
#   M A I N
######################################################################
if __name__ == "__main__":
    unittest.main()
