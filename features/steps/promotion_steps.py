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

WAIT_SECONDS = int(getenv('WAIT_SECONDS', '120'))
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
            "active": row['active'],
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
    error_message = u'I should not see {message} in {context.resp.text}'
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






@when('I set the "{element_name}" to "{text_string}"')
def step_impl(context, element_name, text_string):
    element_id = ID_PREFIX + element_name.lower()
    element = context.driver.find_element_by_id(element_id)
    element.clear()
    element.send_keys(text_string)




#double check
@then('the "{element_name}" checkbox should be empty')
def step_impl(context, element_name):
    element_id = ID_PREFIX + element_name.lower()
    element = context.driver.find_element_by_id(element_id).is_selected()
    expect(element).to_be(False)

#double check
@then('the "{element_name}" checkbox should be checked')
def step_impl(context, element_name):
    element_id = ID_PREFIX + element_name.lower()
    element = context.driver.find_element_by_id(element_id).is_selected()
    expect(element).to_be(True)

@then('the "{element_name}" checkbox should not be checked')
def step_impl(context, element_name):
    element_id = ID_PREFIX + element_name.lower()
    element = context.driver.find_element_by_id(element_id).is_selected()
    expect(element).to_be(False)

@then('I should see "{text}" in the "{element_name}" dropdown')
def step_impl(context, text, element_name):
    element_id = ID_PREFIX + element_name.lower()
    element = Select(context.driver.find_element_by_id(element_id))
    expect(element.first_selected_option.text).to_equal(text)

@then('the "{element_name}" field should be empty')
def step_impl(context, element_name):
    element_id = ID_PREFIX + element_name.lower()
    element = context.driver.find_element_by_id(element_id)
    expect(element.get_attribute('value')).to_be(u'')


##################################################################
# These two function simulate copy and paste
##################################################################
@when('I copy the "{element_name}" field')
def step_impl(context, element_name):
    element_id = ID_PREFIX + element_name.lower()
    # element = context.driver.find_element_by_id(element_id)
    element = WebDriverWait(context.driver, WAIT_SECONDS).until(
        expected_conditions.presence_of_element_located((By.ID, element_id))
    )
    context.clipboard = element.get_attribute('value')
    logging.info('Clipboard contains: %s', context.clipboard)

@when('I paste the "{element_name}" field')
def step_impl(context, element_name):
    element_id = ID_PREFIX + element_name.lower()
    # element = context.driver.find_element_by_id(element_id)
    element = WebDriverWait(context.driver, WAIT_SECONDS).until(
        expected_conditions.presence_of_element_located((By.ID, element_id))
    )
    element.clear()
    element.send_keys(context.clipboard)

##################################################################
# This code works because of the following naming convention:
# The buttons have an id in the html hat is the button text
# in lowercase followed by '-btn' so the Clean button has an id of
# id='clear-btn'. That allows us to lowercase the name and add '-btn'
# to get the element id of any button
##################################################################

@then('I should see the message "{message}"')
def step_impl(context, message):
    #element = context.driver.find_element_by_id('flash_message')
    #expect(element.text).to_contain(message)
    found = WebDriverWait(context.driver, WAIT_SECONDS).until(
        expected_conditions.text_to_be_present_in_element(
            (By.ID, 'flash_message'),
            message
        )
    )
    expect(found).to_be(True)


##################################################################
# This code works because of the following naming convention:
# The id field for text input in the html is the element name
# prefixed by ID_PREFIX so the Name field has an id='pet_name'
# We can then lowercase the name and prefix with pet_ to get the id
##################################################################

@then('I should see "{text_string}" in the "{element_name}" field')
def step_impl(context, text_string, element_name):
    element_id = ID_PREFIX + element_name.lower()
    #element = context.driver.find_element_by_id(element_id)
    #expect(element.get_attribute('value')).to_equal(text_string)
    found = WebDriverWait(context.driver, WAIT_SECONDS).until(
        expected_conditions.text_to_be_present_in_element_value(
            (By.ID, element_id),
            text_string
        )
    )
    expect(found).to_be(True)

