import json
import logging
import requests
from os import getenv
from service import app
from compare import expect, ensure
from behave import given, when, then
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait, Select

WAIT_SECONDS = int(getenv('WAIT_SECONDS', '10'))
ID_PREFIX = 'promotion_'

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


@when(u'I visit the "home page"')
def step_impl(context):
    """ GET Request to the home URL """
    context.driver.get(context.base_url)


@then('I should see "{message}"')
def step_impl(context, message):
    expect(context.driver.title).to_contain(message)


@then('I should not see "{message}"')
def step_impl(context, message):
    error_message = f'I should not see {message} in {context.resp.text}'
    ensure(message in context.resp.text, False, error_message)

@when('I select "{text}" in the "{element_name}" dropdown')
def step_impl(context, text, element_name):
    element_id = ID_PREFIX + element_name.lower()
    element = Select(context.driver.find_element_by_id(element_id))
    element.select_by_visible_text(text)

@when('I check the "{element_name}" checkbox')
def step_impl(context, element_name):
    element_id = ID_PREFIX + element_name.lower()
    context.driver.find_element_by_id(element_id).click()
    
@when('I press the "{button}" button')
def step_impl(context, button):
    button_id = button.lower() + '-btn'
    context.driver.find_element_by_id(button_id).click()

@then('I should see "{name}" in the results')
def step_impl(context, name):
    found = WebDriverWait(context.driver, WAIT_SECONDS).until(
        expected_conditions.text_to_be_present_in_element(
            (By.ID, 'search_results'),
            name
        )
    )
    expect(found).to_be(True)

@then('I should not see "{name}" in the results')
def step_impl(context, name):
    element = context.driver.find_element_by_id('search_results')
    error_msg = "I should not see '%s' in '%s'" % (name, element.text)
    ensure(name in element.text, False, error_msg)