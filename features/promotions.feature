Feature: The promotion service back-end
    As a User
    I need a RESTful catalog service
    So that I can keep track of all the promotions

Background:
    Given the server is started
    Given the following promotions
        | title     | description                   | promo_code | promo_type | amount | start_date | end_date   | is_site_wide | products |
        | Promo1    | Active promotion, site-wide   | pro101     | DISCOUNT   | 10     | 09-09-2020 | 12-01-2021 | True         |          |
        | Promo2    | Active promotion              | pro102     | BOGO       | 1      | 09-09-2020 | 12-01-2021 | False        |          |
        | Promo3    | Inactive promotion, site-wide | pro103     | DISCOUNT   | 20     | 09-09-2020 | 10-10-2020 | True         |          |
    
Scenario: The server is running
    When I visit the "home page"
    Then I should see "Promotion RESTful Service"
    And I should not see "404 Not Found"