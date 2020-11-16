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
- is_site_wide: (bool) whether the promotion is site wide
                (not associated with only certain product(s))
-----------
promotion_products - The relationship between promotion and product
- id: (int) primary key, product_id + promotion_id
- product_id: (int) foreign key, id of a product the promotion is valid for
- promotion_id: (int) foreign key, get to promotions.id
-----------

"""
import logging
from enum import Enum
from datetime import timedelta, datetime
from flask_sqlalchemy import SQLAlchemy
import dateutil.parser

logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()


class DataValidationError(Exception):
    """ Used for an data validation errors when deserializing """


class PromoType(Enum):
    """ Enumeration of valid promotion types"""

    BOGO = 1  # buy X get 1 free
    DISCOUNT = 2  # X% off
    FIXED = 3  # $X off


# pylint: disable=line-too-long
promotion_products = db.Table('promotion_products',
                              db.Column('promotion_id', db.Integer, db.ForeignKey('promotion.id'), primary_key=True),
                              db.Column('product_id', db.Integer, db.ForeignKey('product.id'), primary_key=True)
                              )


class Product(db.Model):
    """
    Class that represents a Product, which just has an ID and no further information.

    This version uses a relational database for persistence which is hidden
    from us by SQLAlchemy's object relational mappings (ORM)
    """

    id = db.Column(db.Integer, primary_key=True)

    def create(self):
        """
        Creates a Product in the database
        """
        logger.info("Creating Product with id: %s", self.id)
        db.session.add(self)
        db.session.commit()


    @classmethod
    def all(cls):
        """ Returns all of the Products in the database """
        logger.info("Processing all Products")
        return cls.query.all()


# pylint: disable=raise-missing-from
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
    products = db.relationship("Product", secondary=promotion_products, lazy="subquery")

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

    def update(self):
        """
        Updates a Promotion to the database
        """
        logger.info("Updating %s", self.title)
        if not self.id:
            raise DataValidationError("Update called with empty ID field")
        db.session.commit()

    def delete(self):
        """ Removes a Promotion from the database """
        logger.info("Deleting %s", self.title)
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def find(cls, promotion_id):
        """ Finds a Promotion by it's ID """
        logger.info("Processing lookup for id %s ...", promotion_id)
        return cls.query.get(promotion_id)

    @classmethod
    def find_or_404(cls, promotion_id):
        """ Find a Promotion by it's id """
        logger.info("Processing lookup or 404 for id %s ...", promotion_id)
        return cls.query.get_or_404(promotion_id)

    @classmethod
    def find_by_query_string(cls, args):
        """ Find a Promotion by query string """
        logger.info(" Processing lookup based on query string %s ...", args)
        data = cls.query
        if "id" in args:
            data = data.filter(cls.id == args["id"])
        if "title" in args:
            data = data.filter(cls.title == args["title"])
        if "promo_code" in args:
            data = data.filter(cls.promo_code == args["promo_code"])
        if "promo_type" in args:
            data = data.filter(cls.promo_type == args["promo_type"])
        if "amount" in args:
            data = data.filter(cls.amount == args["amount"])
        if "is_site_wide" in args:
            data = data.filter(cls.is_site_wide == args["is_site_wide"])
        if "start_date" in args:
            data = data.filter(
                cls.start_date == dateutil.parser.parse(args["start_date"])
            )
        if "end_date" in args:
            data = data.filter(cls.end_date == dateutil.parser.parse(args["end_date"]))
        if "duration" in args:
            # returns promotions that last the number of days specified
            data = data.filter(
                cls.start_date + timedelta(days=int(args.get("duration")))
                == cls.end_date
            )
        if "active" in args:
            if args.get("active") == "1":
                data = data.filter(cls.start_date <= datetime.now()).filter(
                    cls.end_date >= datetime.now()
                )
            if args.get("active") == "0":
                data = data.filter(
                    (cls.start_date > datetime.now()) | (datetime.now() > cls.end_date)
                )
        if "product" in args:
            data = data.filter(cls.products.any(id=int(args.get("product"))))
        return data.all()

    @classmethod
    def apply_best_promo(cls, product_id, pricing):
        """ Find a Promotion by query string """
        logger.info(" Finding best promotion for the product %s ...", product_id)
        promos = cls.query.filter(cls.start_date <= datetime.now()).filter(
            cls.end_date >= datetime.now()
        )

        product_promos = promos.filter(cls.products.any(id=product_id))
        site_wide_promos = promos.filter(cls.is_site_wide)
        logger.info("  Available site wide promos: " + str(site_wide_promos.all()))
        logger.info("  Available promos for this product: " + str(product_promos.all()))

        best_promo, best_discount = None, 0
        for p in site_wide_promos.all() + product_promos.all():
            if p.promo_type == PromoType.DISCOUNT:
                if p.amount > best_discount:
                    best_promo, best_discount = p, p.amount
            elif p.promo_type == PromoType.BOGO and best_discount < 50:
                best_promo, best_discount = p, 50
            elif p.promo_type == PromoType.FIXED:
                fixed_discount = ((pricing - p.amount) / pricing) * 100
                if fixed_discount > best_discount:
                    best_promo, best_discount = p, fixed_discount

        logger.info(
            "  Promotion selected: "
            + str(best_promo.promo_code if best_promo else None)
        )
        return {product_id: best_promo.promo_code} if best_promo else None

    def serialize(self):
        """ Serializes a Promotion into a dictionary """
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "promo_code": self.promo_code,
            "promo_type": self.promo_type.name,
            "amount": self.amount,
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat(),
            "is_site_wide": self.is_site_wide,
            "products": [product.id for product in self.products],
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
            self.promo_type = getattr(
                PromoType, data["promo_type"]
            )  # create enum from string
            self.amount = data["amount"]
            self.start_date = data["start_date"]
            self.end_date = data["end_date"]
            self.is_site_wide = data["is_site_wide"]
            self.products = []
            for product_id in data["products"]:
                product = Product.query.get(product_id)
                self.products.append(product)
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
