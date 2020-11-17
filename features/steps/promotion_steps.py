import json
# import logging
import requests
# from os import getenv
from service import app
from compare import expect, ensure
from behave import given, when, then
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support import expected_conditions
# from selenium.webdriver.support.ui import WebDriverWait, Select

# WAIT_SECONDS = int(getenv('WAIT_SECONDS', '60'))
# ID_PREFIX = 'promotion_'

@given('the following promotions')
def step_impl(context):
    """ Delete all promotions and load new ones """
    headers = {'Content-Type': 'application/json'}
    # Deleting the existing promotions
    context.resp = requests.get(context.base_url + '/promotions', headers=headers)
    expect(context.resp.status_code).to_equal(200)
    for promo in context.resp.json():
        context.resp = requests.delete(context.base_url + '/promotions/' + str(promo["id"]), headers=headers)
        expect(context.resp.status_code).to_equal(204)
    
    # load the new promotions as per the Background
    create_url = context.base_url + '/promotions'
    for row in context.table:
        data = {
            "title": row['title'],
            "description": row['description'],
            "promo_code": row['promo_code'],
            "promo_type": row['promo_type'],
            "amount": row['amount'],
            "start_date": row['start_date'],
            "end_date": row['end_date'],
            "is_site_wide": row['is_site_wide'] in ['True', 'true', '1'],
            "products": row['products']
            }
        payload = json.dumps(data)
        context.resp = requests.post(create_url, data=payload, headers=headers)
        expect(context.resp.status_code).to_equal(201)


@given(u'the server is started')
def step_impl(context):
    context.app = app.test_client()


@when(u'I visit the "home page"')
def step_impl(context):
    """ GET Request to the home URL """
    context.resp = context.app.get('/')


@then('I should see "{message}"')
def step_impl(context, message):
    expect(str(context.resp.data)).to_contain(message)


@then('I should not see "{message}"')
def step_impl(context, message):
    error_message = f'I should not see {message} in {context.resp.data}'
    ensure(message in str(context.resp.data), False, error_message)