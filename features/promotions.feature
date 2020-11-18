Feature: The promotion service back-end
    As a User
    I need a RESTful catalog service
    So that I can keep track of all the promotions

Background:
    Given the following promotions
        | title     | description                   | promo_code | promo_type | amount | start_date | end_date   | is_site_wide | products |
        | Promo1    | Active promotion, site-wide   | pro101     | DISCOUNT   | 10     | 09-09-2020 | 12-01-2021 | True         |          | 
        | Promo2    | Active promotion              | pro102     | BOGO       | 1      | 09-09-2020 | 12-01-2021 | False        |          |
        | Promo3    | Active promotion              | pro103     | BOGO       | 1      | 09-09-2020 | 12-01-2021 | True         |          |
        | Promo4    | Inactive promotion, site-wide | pro104     | DISCOUNT   | 20     | 09-09-2020 | 10-10-2020 | True         |          |
        | Promo5    | Active promotion, site-wide   | pro105     | BOGO       | 1      | 09-09-2020 | 10-10-2021 | True         |          |
    
Scenario: The server is running
    When I visit the "home page"
    Then I should see "Promotion RESTful Service"
    And I should not see "404 Not Found"

Scenario: List all active site-wide BOGO promotions 
    When I visit the "home page"
    And I select "BOGO" in the "promo_type" dropdown
    And I check the "is_site_wide" checkbox
    And I check the "active" checkbox
    And I press the "Search" button
    Then I should see "Promo3" in the results
    And I should see "Promo5" in the results
    And I should not see "Promo1" in the results
    And I should not see "Promo2" in the results
    And I should not see "Promo4" in the results

Scenario: Create a promotion
    When I visit the "Home Page"
    And I set the "title" to "Promo6"
    And I set the "description" to "Some items off to celebrate the coming festivals."
    And I set the "promo_code" to "pro106"
    And I select "BOGO" in the "promo_type" dropdown
    And I set the "amount" to "1"
    And I set the "start_date" to "11-16-2020"
    And I set the "end_date" to "12-31-2020"
    And I check the "is_site_wide" checkbox
    And I press the "Create" button
    Then I should see the message "Promotion successfully created" 
    When I copy the "Id" field
    And I press the "Clear" button
    Then the "Id" field should be empty
    And the "title" field should be empty
    And the "description" field should be empty
    And the "promo_code" field should be empty
    And the "amount" field should be empty
    And the "start_date" field should be empty
    And the "end_date" field should be empty
    And the "is_site_wide" checkbox should be empty
    When I paste the "Id" field
    And I press the "Retrieve" button
    Then I should see "Promo6" in the "title" field
    And I should see "Some items off to celebrate the coming festivals." in the "description" field
    And I should see "pro106" in the "promo_code" field
    And I should see "BOGO" in the "promo_type" dropdown
    And I should see "1" in the "amount" field
    And I should see "2020-11-16" in the "start_date" field
    And I should see "2020-12-31" in the "end_date" field
    And the "is_site_wide" checkbox should be checked