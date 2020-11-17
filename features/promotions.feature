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