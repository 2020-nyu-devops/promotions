"""
Models for Promotion Service

All of the models are stored in this module

Models
------
Promotion - A Promotion used in the eCommerce website
- id: (int) primary key
- title: (str) the name of the promotion
- description: (str) string/text
- promo_code: (str) the promo_code associated with this promotion 
- promo_type: (str or enum) [BOGO | DISCOUNT | FIXED]
- amount: (int) the amount of the promotion base on promo_type
- start_date: (date) the starting date
- end_date: (date) the ending date
- is_site_wide: (bool) whether the promotion is site wide (not associated with only certain product(s)
-----------
promotion_products - The relationship between promotion and product
- id: (int) primary key, product_id + promotion_id
- product_id: (int) foreign key, id of a product the promotion is valid for
- promotion_id: (int) foreign key, get to promotions.id
-----------

"""
import logging
from enum import Enum
from flask_sqlalchemy import SQLAlchemy

logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()


class DataValidationError(Exception):
    """ Used for an data validation errors when deserializing """
    pass


class PromoType(Enum):
    """ Enumeration of valid promotion types"""
    BOGO = 1  # buy X get 1 free
    DISCOUNT = 2  # X% off
    FIXED = 3  # $X off


promotion_products = db.Table('promotion_products',
                              db.Column('promotion_id', db.Integer, db.ForeignKey('promotion.id'), primary_key=True),
                              db.Column('product_id', db.Integer, db.ForeignKey('product.id'), primary_key=True)
                              )


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)


class Promotion(db.Model):
    """
    Class that represents a Promotion

    This version uses a relational database for persistence which is hidden
    from us by SQLAlchemy's object relational mappings (ORM)
    """

    app = None

    # Table Schema
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(63), nullable=False)
    description = db.Column(db.Text(), nullable=True)
    promo_code = db.Column(db.String(63), nullable=True)
    promo_type = db.Column(db.Enum(PromoType), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    start_date = db.Column(db.DateTime(), nullable=False)
    end_date = db.Column(db.DateTime(), nullable=False)
    is_site_wide = db.Column(db.Boolean(), nullable=False, default=False)
    # for promotion_products Many-to-Many relationship
    products = db.relationship('Product', secondary=promotion_products, lazy='subquery',
                               backref=db.backref('promotions', lazy=True))

    def __repr__(self):
        return "<Promotion %r id=[%s]>" % (self.title, self.id)

    def create(self):
        """
        Creates a Promotion in the database
        """
        logger.info("Creating %s", self.title)
        self.id = None  # id must be none to generate next primary key
        db.session.add(self)
        db.session.commit()

    def serialize(self):
        """ Serializes a Promotion into a dictionary """
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "promo_code": self.promo_code,
            "promo_type": self.promo_type.name,
            "amount": self.amount,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "is_site_wide": self.is_site_wide
        }

    def deserialize(self, data):
        """
        Deserializes a Promotion from a dictionary

        Args:
            data (dict): A dictionary containing the Promotion data
        """
        try:
            self.title = data["title"]
            self.description = data["description"]
            self.promo_code = data["promo_code"]
            self.promo_type = getattr(PromoType, data['promo_type'])  # create enum from string
            self.amount = data["amount"]
            self.start_date = data["start_date"]
            self.end_date = data["end_date"]
            self.is_site_wide = data["is_site_wide"]
        except KeyError as error:
            raise DataValidationError("Invalid promotion: missing " + error.args[0])
        except TypeError as error:
            raise DataValidationError(
                "Invalid promotion: body of request contained bad or no data"
            )
        return self

    @classmethod
    def all(cls):
        """ Returns all of the Promotions in the database """
        logger.info("Processing all Promotions")
        return cls.query.all()

    @classmethod
    def init_db(cls, app):
        """ Initializes the database session """
        logger.info("Initializing database")
        cls.app = app
        # This is where we initialize SQLAlchemy from the Flask app
        db.init_app(app)
        app.app_context().push()
        db.create_all()  # make our sqlalchemy tables
