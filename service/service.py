"""
Promotion Service with Swagger

Paths:
------
GET / - Returns the UI and 200 code, for Selenium testing
POST /promotions - creates a new Promotion record in the database
"""
import os
import sys
import logging
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
# Error Handlers
######################################################################
@app.errorhandler(DataValidationError)
def request_validation_error(error):
    """ Handles Value Errors from bad data """
    return bad_request(error)


@app.errorhandler(status.HTTP_400_BAD_REQUEST)
def bad_request(error):
    """ Handles bad requests with 400_BAD_REQUEST """
    app.logger.warning(str(error))
    return (
        jsonify(
            status=status.HTTP_400_BAD_REQUEST, error="Bad Request", message=str(error)
        ),
        status.HTTP_400_BAD_REQUEST,
    )


@app.errorhandler(status.HTTP_404_NOT_FOUND)
def not_found(error):
    """ Handles resources not found with 404_NOT_FOUND """
    app.logger.warning(str(error))
    return (
        jsonify(
            status=status.HTTP_404_NOT_FOUND, error="Not Found", message=str(error)
        ),
        status.HTTP_404_NOT_FOUND,
    )


@app.errorhandler(status.HTTP_405_METHOD_NOT_ALLOWED)
def method_not_supported(error):
    """ Handles unsupported HTTP methods with 405_METHOD_NOT_SUPPORTED """
    app.logger.warning(str(error))
    return (
        jsonify(
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
            error="Method not Allowed",
            message=str(error),
        ),
        status.HTTP_405_METHOD_NOT_ALLOWED,
    )


@app.errorhandler(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
def mediatype_not_supported(error):
    """ Handles unsupported media requests with 415_UNSUPPORTED_MEDIA_TYPE """
    app.logger.warning(str(error))
    return (
        jsonify(
            status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            error="Unsupported media type",
            message=str(error),
        ),
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
    )


@app.errorhandler(status.HTTP_500_INTERNAL_SERVER_ERROR)
def internal_server_error(error):
    """ Handles unexpected server error with 500_SERVER_ERROR """
    app.logger.error(str(error))
    return (
        jsonify(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error="Internal Server Error",
            message=str(error),
        ),
        status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


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
api = Api(app,
          version='1.0.0',
          title='Promotions REST API Service',
          description='This is the Promotions server.',
          default='promotions',
          default_label='Promotions service operations',
          doc='/api-docs',
          # authorizations=authorizations,
          prefix='/'
          )

# Define the model so that the docs reflect what can be sent
create_model = api.model('Promotion', {
    'title': fields.String(required=False,
                           description='The name of the promotion'),
    'description': fields.String(required=False,
                                 description='The description of the promotion'),
    'promo_code': fields.String(required=False,
                                description='The promo code associated with this promotion'),
    'promo_type': fields.String(required=False,
                                description='The type of promotion [BOGO | DISCOUNT | FIXED]'),
    'amount': fields.Integer(required=False,
                             description='The amount of the promotion based on promo type'),
    'start_date': fields.DateTime(required=False,
                                  description='The start date of the promotion'),
    'end_date': fields.DateTime(required=False,
                                description='The end date of the promotion'),
    'is_site_wide': fields.Boolean(required=False,
                                   description='Is the promotion site wide?'),
    'products': fields.List(cls_or_instance=fields.Integer, required=False,
                            description='List of products associated with the promotion.')

})

promotion_model = api.inherit(
    'PromotionModel',
    create_model,
    {
        'id': fields.Integer(readOnly=True,
                             description='The unique id assigned internally by service'),
    }
)


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
            raise NotFound("Promotion with id '{}' was not found.".format(promotion_id))
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
        location_url = api.url_for(PromotionResource, promotion_id=promotion.id, _external=True)
        app.logger.info("Promotion with ID [%s] created.", promotion.id)
        return promotion.serialize(), status.HTTP_201_CREATED, {"Location": location_url}

######################################################################
# LIST ALL THE PROMOTIONS
######################################################################
@app.route("/promotions", methods=["GET"])
def list_promotions():
    """
    List all promotions
    """
    app.logger.info("Request to list all promotions")
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
    app.logger.info(request.args)
    if any(i in request.args for i in filters):
        promotions = Promotion.find_by_query_string(request.args)
    else:
        promotions = Promotion.all()
    results = [promo.serialize() for promo in promotions]
    app.logger.info("Returning %d promotions", len(results))
    return make_response(jsonify(results), status.HTTP_200_OK)


######################################################################
# UPDATE AN EXISTING PROMOTION
######################################################################
@app.route("/promotions/<int:promotion_id>", methods=["PUT"])
def update_promotions(promotion_id):
    """
    Update a Promotion
    This endpoint will update a Promotion based the body that is posted
    """
    app.logger.info("Request to update promotion with id: %s", promotion_id)
    check_content_type("application/json")
    promotion = Promotion.find(promotion_id)
    if not promotion:
        raise NotFound("Promotion with id '{}' was not found.".format(promotion_id))
    json = request.get_json()
    if "products" in json:
        for product_id in json["products"]:
            if product_id != "" and Product.query.get(product_id) is None:
                Product(id=product_id).create()
    promotion.deserialize(json)
    promotion.id = promotion_id
    promotion.update()
    app.logger.info("Promotion with ID [%s] updated.", promotion.id)
    return make_response(jsonify(promotion.serialize()), status.HTTP_200_OK)

######################################################################
# CANCEL A PROMOTION
######################################################################
@app.route("/promotions/<int:promotion_id>/cancel", methods=["POST"])
def cancel_promotions(promotion_id):
    """
    Cancel a Promotions
    This endpoint will cancel a Promotion based an ID
    """
    app.logger.info("Request to cancel promotion with id: %s", promotion_id)
    promotion = Promotion.find(promotion_id)
    if not promotion:
        raise NotFound("Promotion with id '{}' was not found.".format(promotion_id))
    promotion.end_date = datetime.now()
    promotion.update()
    app.logger.info("Promotion with ID [%s] cancelled", promotion_id)
    return make_response("", status.HTTP_200_OK)


######################################################################
# APPLY BEST PROMOTION
######################################################################
@app.route("/promotions/apply", methods=["GET"])
def apply_best_promotions():
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
    return make_response(jsonify(results), status.HTTP_200_OK)


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
