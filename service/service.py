"""
Promotion Service with Swagger

Paths:
------
GET / - Returns the UI and 200 code, for Selenium testing
POST /promotions - creates a new Promotion record in the database
"""
# pylint: disable=R0201
from datetime import datetime
from flask import Flask, jsonify, request, url_for, make_response, abort
from flask_api import status  # HTTP Status Codes
from flask_restx import Api, Resource, fields, reqparse, inputs
from werkzeug.exceptions import NotFound

# For this example we'll use SQLAlchemy, a popular ORM that supports a
# variety of backends including SQLite, MySQL, and PostgreSQL
from flask_sqlalchemy import SQLAlchemy
from service.models import Promotion, DataValidationError, Product

# Import Flask application
from . import app


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """ Root URL response """
    return app.send_static_file("index.html")


######################################################################
# Configure Swagger before initializing it
######################################################################
api = Api(
    app,
    version='1.0.0',
    title='Promotions REST API Service',
    description='This is the Promotions server.',
    default='promotions',
    default_label='Promotions service operations',
    doc='/api-docs',
    prefix='/',
)

# Define the model so that the docs reflect what can be sent
create_model = api.model(
    'Promotion',
    {
        'title': fields.String(required=False, description='The name of the promotion'),
        'description': fields.String(
            required=False, description='The description of the promotion'
        ),
        'promo_code': fields.String(
            required=False, description='The promo code associated with this promotion'
        ),
        'promo_type': fields.String(
            required=False,
            description='The type of promotion [BOGO | DISCOUNT | FIXED]',
        ),
        'amount': fields.Integer(
            required=False,
            description='The amount of the promotion based on promo type',
        ),
        'start_date': fields.DateTime(
            required=False, description='The start date of the promotion'
        ),
        'end_date': fields.DateTime(
            required=False, description='The end date of the promotion'
        ),
        'is_site_wide': fields.Boolean(
            required=False, description='Is the promotion site wide?'
        ),
        'products': fields.List(
            cls_or_instance=fields.Integer,
            required=False,
            description='List of products associated with the promotion.',
        ),
    },
)

promotion_model = api.inherit(
    'PromotionModel',
    create_model,
    {
        'id': fields.Integer(
            readOnly=True, description='The unique id assigned internally by service'
        ),
    },
)

######################################################################
# Error Handlers
######################################################################
@api.errorhandler(DataValidationError)
def request_validation_error(error):
    """ Handles Value Errors from bad data """
    app.logger.error(str(error))
    return {
        'status_code': status.HTTP_400_BAD_REQUEST,
        'error': 'Bad Request',
        'message': str(error),
    }, status.HTTP_400_BAD_REQUEST


# query string arguments
# --------------------------------------------------------------------------------------------------
promotion_args = reqparse.RequestParser()
promotion_args.add_argument('title', type=str, required=False, location='args', help='List Promotions by title')
promotion_args.add_argument('promo_code', type=str, required=False, location='args', help='List Promotions by promo code')
promotion_args.add_argument('promo_type', type=str, required=False, location='args', help='List Promotions by promo type')
promotion_args.add_argument('amount', type=int, required=False, location='args', help='List Promotions by the amount discounted')
promotion_args.add_argument('start_date', type=str, required=False, location='args', help='List Promotions by start date')
promotion_args.add_argument('end_date', type=str, required=False, location='args', help='List Promotions by end date')
promotion_args.add_argument('duration', type=int, required=False, location='args', help='List Promotions by duration')
promotion_args.add_argument('active', type=str, required=False, location='args', help='List Promotions by active status')
promotion_args.add_argument('is_site_wide', type=str, required=False, location='args', help='List Promotions by site wide status')
promotion_args.add_argument('product', type=int, required=False, location='args', help='List Promotions by a product')


######################################################################
#  PATH: /promotions/{id}
######################################################################
@api.route("/promotions/<int:promotion_id>")
@api.param('promotion_id', 'The Promotion identifier')
class PromotionResource(Resource):
    """
    PromotionResource class

    Allows the retrieval/manipulation of a single promotion
    GET /promotion/{id}     - Retrieves the promotion with the id
    PUT /promotion/{id}     - Update the promotion with the id
    DELETE /promotion/{id}  - Delete the promotion with the id
    """

    ######################################################################
    # RETRIEVE A PROMOTION
    ######################################################################
    @api.doc('get_promotions')
    @api.response(404, 'Promotion not found')
    @api.marshal_with(promotion_model)
    def get(self, promotion_id):
        """
        Retrieve a single Promotion
        This endpoint will return a Promotion based on it's id
        """
        app.logger.info("Request for promotion with id: %s", promotion_id)
        promotion = Promotion.find(promotion_id)
        if not promotion:
            api.abort(
                status.HTTP_404_NOT_FOUND,
                f"Promotion with id '{promotion_id}' was not found.",
            )
        return promotion.serialize(), status.HTTP_200_OK

    ######################################################################
    # UPDATE AN EXISTING PROMOTION
    ######################################################################
    @api.doc('update_promotions')
    @api.response(404, 'Promotion not found')
    @api.response(400, 'The posted data was not valid')
    @api.expect(promotion_model)
    @api.marshal_with(promotion_model)
    def put(self, promotion_id):
        """
        Update a Promotion
        This endpoint will update a Promotion based the body that is posted
        """
        app.logger.info("Request to update promotion with id: %s", promotion_id)
        check_content_type("application/json")
        json = request.get_json()
        promotion = Promotion.find(promotion_id)
        if not promotion:
            api.abort(
                status.HTTP_404_NOT_FOUND,
                "Promotion with id '{}' was not found.".format(promotion_id),
            )
        json = request.get_json()
        if "products" in json:
            for product_id in json["products"]:
                if product_id != "" and Product.query.get(product_id) is None:
                    Product(id=product_id).create()
        promotion.deserialize(json)
        promotion.id = promotion_id
        promotion.update()
        app.logger.info("Promotion with ID [%s] updated.", promotion.id)
        return promotion.serialize(), status.HTTP_200_OK

    ######################################################################
    # DELETE A PROMOTION
    ######################################################################
    @api.doc('delete_promotions')
    @api.response(204, 'Promotion deleted')
    @api.response(200, 'No promotion with that ID to delete')
    def delete(self, promotion_id):
        """
        Delete a Promotion
        This endpoint will delete a Promotion based the id specified in the path
        """
        # pylint: disable=R1705
        app.logger.info('Request to Delete a promotion with id [%s]', promotion_id)
        promo = Promotion.find(promotion_id)
        if promo:
            promo.delete()
            return '', status.HTTP_204_NO_CONTENT
        else:
            return '', status.HTTP_200_OK


######################################################################
#  PATH: /promotions
######################################################################
@api.route('/promotions', strict_slashes=False)
class PromotionCollection(Resource):
    """ Handles all interactions with collections of Promotions """

    # ------------------------------------------------------------------
    # LIST ALL PROMOTIONS
    # ------------------------------------------------------------------
    @api.doc('list_promotions')
    @api.expect(promotion_args, validate=True)
    @api.marshal_list_with(promotion_model)
    def get(self):
        """ Returns all of the Promotions """
        args = promotion_args.parse_args()
        app.logger.info("Request to list promotions based on query string %s ...", args)
        filters = [
            "title",
            "is_site_wide",
            "promo_code",
            "promo_type",
            "amount",
            "start_date",
            "end_date",
            "duration",
            "active",
            "product",
        ]
        promotions = Promotion.find_by_query_string(args)
        results = [promo.serialize() for promo in promotions]
        app.logger.info("Returning %d promotions", len(results))
        return results, status.HTTP_200_OK

    # ------------------------------------------------------------------
    # ADD A NEW PROMOTION
    # ------------------------------------------------------------------
    @api.doc('create_promotions')
    @api.expect(create_model)
    @api.response(400, 'The posted data was not valid')
    @api.response(201, 'Promotion created successfully')
    @api.marshal_with(promotion_model, code=201)
    def post(self):
        """
        Creates a Promotion
        This endpoint will create a Promotion based the data in the body that is posted
        """
        app.logger.info("Request to create a promotion")
        check_content_type("application/json")
        json = request.get_json()
        if "products" in json:
            for product_id in json["products"]:
                if product_id != "" and Product.query.get(product_id) is None:
                    Product(id=product_id).create()
        promotion = Promotion()
        promotion.deserialize(json)
        promotion.create()
        location_url = api.url_for(
            PromotionResource, promotion_id=promotion.id, _external=True
        )
        app.logger.info("Promotion with ID [%s] created.", promotion.id)
        return (
            promotion.serialize(),
            status.HTTP_201_CREATED,
            {"Location": location_url},
        )


######################################################################
#  CANCEL A PROMOTION - /promotions/{id}/cancel
######################################################################
@api.route("/promotions/<int:promotion_id>/cancel")
@api.param('promotion_id', 'The Promotion identifier')
class PromotionCancellation(Resource):
    @api.doc('cancel_promotions')
    @api.response(404, 'Promotion not found')
    @api.response(200, 'Promotion cancelled')
    def post(self, promotion_id):
        """
        Cancels a single Promotion
        This endpoint will cancel a Promotion based on it's id
        """
        app.logger.info("Request to cancel Promotion with id: %s", promotion_id)
        promotion = Promotion.find(promotion_id)
        if not promotion:
            raise NotFound("Promotion with id '{}' was not found.".format(promotion_id))
        promotion.end_date = datetime.now()
        promotion.update()
        app.logger.info("Promotion with ID [%s] cancelled", promotion_id)
        return make_response("", status.HTTP_200_OK)


@api.route('/promotions/apply', strict_slashes=False)
class PromotionCollection(Resource):

    ######################################################################
    # APPLY BEST PROMOTION
    ######################################################################
    @api.doc('apply_best_promotions')
    def get(self):
        """
        Apply best promotions
        """
        app.logger.info("Apply best promotions")
        app.logger.info(request.args)
        if len(request.args) > 0:
            results = [
                Promotion.apply_best_promo(product, int(request.args.get(product)))
                for product in request.args
            ]
            results = list(filter(None, results))
        else:
            results = []
        app.logger.info("Returning %d results.", len(results))
        return results, status.HTTP_200_OK


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################
def init_db():
    """ Initializes the SQLAlchemy app """
    global app
    Promotion.init_db(app)


def check_content_type(content_type):
    """ Checks that the media type is correct """
    if request.headers["Content-Type"] == content_type:
        return
    app.logger.error("Invalid Content-Type: %s", request.headers["Content-Type"])
    abort(415, "Content-Type must be {}".format(content_type))
