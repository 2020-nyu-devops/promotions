$(function () {

    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    // Updates the form with data from the response
    function update_form_data(res) {
        $("#promotion_id").val(res.id);
        $("#promotion_title").val(res.title);
        $("#promotion_description").val(res.description);
        $("#promotion_promo_code").val(res.promo_code);
        $("#promotion_promo_type").val(res.promo_type);
        $("#promotion_amount").val(res.amount);
        if (res.start_date !== undefined) $("#promotion_start_date").val(res.start_date.substring(0,10));
        if (res.end_date !== undefined) $("#promotion_end_date").val(res.end_date.substring(0,10));
        $("#promotion_products").val(res.products);
        $("#promotion_is_site_wide").val(res.is_site_wide ? "true" : "false");
        $("#promotion_active").val(res.active);
    }

    /// Clears all form fields
    function clear_form_data() {
        $("#promotion_id").val("");
        $("#promotion_title").val("");
        $("#promotion_description").val("");
        $("#promotion_promo_code").val("");
        $("#promotion_promo_type").val("");
        $("#promotion_amount").val("");
        $("#promotion_duration").val("");
        $("#promotion_start_date").val("");
        $("#promotion_end_date").val("");
        $("#promotion_products").val("");
        $("#promotion_product_pricings").val("");
        $("#promotion_is_site_wide").val("");
        $("#promotion_active").val("");
    }

    function clear_search_table(){
        $("#search_results").find("tr:gt(0)").remove();
    }

    // Updates the flash message area
    function flash_message(message) {
        $("#flash_message").empty();
        $("#flash_message").append(message);
    }

    // Gets the parameters
    function encodeGetParams(params) {
      return Object.entries(params)
        .filter(function(kv) { return kv[1] === false || !!kv[1]; })
        .map(function(kv) { return kv.map(encodeURIComponent).join("="); })
        .join("&");
    }

    // ****************************************
    // Create a Promotion
    // ****************************************

    $("#create-btn").click(function () {

        var data = {
            "id": $("#promotion_id").val(),
            "title": $("#promotion_title").val(),
            "description" : $("#promotion_description").val(),
            "promo_code" : $("#promotion_promo_code").val(),
            "promo_type" : $("#promotion_promo_type").val(),
            "amount" : $("#promotion_amount").val(),
            "start_date" : $("#promotion_start_date").val(),
            "end_date" : $("#promotion_end_date").val(),
            "products" : $("#promotion_products").val().split(","),
            "is_site_wide" : $("#promotion_is_site_wide").val() == "true",
        };

        var ajax = $.ajax({
            type: "POST",
            url: "/promotions",
            contentType: "application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Promotion successfully created")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });
    });

    // ****************************************
    // Cancel a Promotion
    // ****************************************

    $("#cancel-btn").click(function () {

        var id = $("#promotion_id").val();

        var ajax = $.ajax({
            type: "POST",
            url: "/promotions/" + id + "/cancel",
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            //alert(res.toSource())
            flash_message("Promotion canceled")
        });

        ajax.fail(function(res){
            clear_form_data()
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Retrieve a Promotion
    // ****************************************

    $("#retrieve-btn").click(function () {

        var id = $("#promotion_id").val();

        var ajax = $.ajax({
            type: "GET",
            url: "/promotions/" + id,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            //alert(res.toSource())
            update_form_data(res)
            flash_message("Promotion retrieved")
        });

        ajax.fail(function(res){
            clear_form_data()
            // flash_message(res.responseJSON.message)
            // flash_message(res.status + ' ' + res.statusText.toLowerCase())
            flash_message(res.status)
        });

    });

    // ****************************************
    // List all Promotion
    // ****************************************

    $("#list-btn").click(function () {

        var ajax = $.ajax({
            type: "GET",
            url: "/promotions",
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            //alert(res.toSource())
            $("#search_results").empty();
            var table = '<table class="table-striped table-bordered">';
            table += '<tr>';
            table += '<th>ID</th>';
            table += '<th>Title</th>';
            table += '<th>Description</th>';
            table += '<th>Promo Code</th>';
            table += '<th>Promo Type</th>';
            table += '<th>Amount</th>';
            table += '<th>Start Date</th>';
            table += '<th>End Date</th>';
            table += '<th>Products</th>';
            table += '<th>Site-wide Status</th>';
            table += '</tr>';

            var firstPromotion = "";
            for(var i = 0; i < res.length; i++) {
                var promotion = res[i];
                var row = "<tr><td>"+promotion.id+"</td><td>"+promotion.title+"</td><td>"+promotion.description+"</td><td>"+promotion.promo_code+"</td><td>"+promotion.promo_type+"</td><td>"+promotion.amount+"</td><td>"+promotion.start_date+"</td><td>"+promotion.end_date+"</td><td>"+promotion.products+"</td><td>"+promotion.is_site_wide+"</td></tr>";
                table += row;
                if (i == 0) {
                    firstPromotion = promotion;
                }
            }

            table += '</table>';
            $("#search_results").append(table);

            // copy the first result to the form
            if (firstPromotion != "") {
                update_form_data(firstPromotion)
            }

            flash_message("All promotions listed at the table below")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Update a Promotion
    // ****************************************

    $("#update-btn").click(function () {

        var data = {
            "id": $("#promotion_id").val(),
            "title": $("#promotion_title").val(),
            "description" : $("#promotion_description").val(),
            "promo_code" : $("#promotion_promo_code").val(),
            "promo_type" : $("#promotion_promo_type").val(),
            "amount" : $("#promotion_amount").val(),
            "start_date" : $("#promotion_start_date").val(),
            "end_date" : $("#promotion_end_date").val(),
            "products" : $("#promotion_products").val().trim().split(","),
            "is_site_wide" : $("#promotion_is_site_wide").val() == "true",
        };

        var ajax = $.ajax({
                type: "PUT",
                url: "/promotions/" + $("#promotion_id").val(),
                contentType: "application/json",
                data: JSON.stringify(data)
            })

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Promotion updated")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Delete a Promotion
    // ****************************************

    $("#delete-btn").click(function () {

        var id = $("#promotion_id").val();

        var ajax = $.ajax({
            type: "DELETE",
            url: "/promotions/" + id,
            contentType: "application/json",
            data: '',
        })

        ajax.done(function(res){
            clear_form_data()
            flash_message("Promotion has been deleted!")
        });

        ajax.fail(function(res){
            flash_message("Server error!")
        });
    });

    // ****************************************
    // Clear the form
    // ****************************************

    $("#clear-btn").click(function () {
        $("#promotion_id").val("");
        clear_form_data()
        clear_search_table()
        flash_message("All results cleared")
    });

    // ****************************************
    // Search for a Promotion
    // ****************************************

    $("#search-btn").click(function () {

        var queryString = encodeGetParams({
            title : $("#promotion_title").val(),
            promo_code : $("#promotion_promo_code").val(),
            promo_type : $("#promotion_promo_type").val(),
            amount : $("#promotion_amount").val(),
            start_date : $("#promotion_start_date").val(),
            end_date : $("#promotion_end_date").val(),
            duration : $("#promotion_duration").val(),
            product : $("#promotion_products").val(),
            is_site_wide : $("#promotion_is_site_wide").val(),
            active : $("#promotion_active").val(),
        });

        var ajax = $.ajax({
            type: "GET",
            url: "/promotions?" + queryString,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            //alert(res.toSource())
            $("#search_results").empty();
            var table = '<table class="table-striped table-bordered">';
            table += '<tr>';
            table += '<th>ID</th>';
            table += '<th>Title</th>';
            table += '<th>Description</th>';
            table += '<th>Promo Code</th>';
            table += '<th>Promo Type</th>';
            table += '<th>Amount</th>';
            table += '<th>Start Date</th>';
            table += '<th>End Date</th>';
            table += '<th>Products</th>';
            table += '<th>Site-wide Status</th>';
            table += '</tr>';

            var firstPromotion = "";
            for(var i = 0; i < res.length; i++) {
                var promotion = res[i];
                var row = "<tr><td>"+promotion.id+"</td><td>"+promotion.title+"</td><td>"+promotion.description+"</td><td>"+promotion.promo_code+"</td><td>"+promotion.promo_type+"</td><td>"+promotion.amount+"</td><td>"+promotion.start_date+"</td><td>"+promotion.end_date+"</td><td>"+promotion.products+"</td><td>"+promotion.is_site_wide+"</td></tr>";
                table += row;
                if (i == 0) {
                    firstPromotion = promotion;
                }
            }

            table += '</table>';
            $("#search_results").append(table);

            // copy the first result to the form
            if (firstPromotion != "") {
                update_form_data(firstPromotion)
            }

            flash_message("Search results at the table below")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Apply Best Promotion for the products
    // ****************************************

    $("#apply-btn").click(function () {
        let products = $("#promotion_products").val().split(",")
        let pricings = $("#promotion_product_pricings").val().split(",")
        let queryString = ""

        products.forEach(
            (product, index) => 
                queryString = queryString + "&"+ product + "=" + pricings[index])
        
        queryString = queryString.substring(1, queryString.length)

        if (queryString.length > 0) {
            var ajax = $.ajax({
                type: "GET",
                url: "/promotions/apply?" + queryString,
                contentType: "application/json",
                data: ''
            })
    
            ajax.done(function(results){
                let output = [];
                results.forEach(
                    (result, index) => {
                        let product_id = Object.keys(result)[0]
                        let promo_code = result[product_id]
                        var ajax_internal = $.ajax({
                            type: "GET",
                            url: "/promotions?promo_code=" + promo_code,
                            contentType: "application/json",
                            data: ''
                        })

                        ajax_internal.done(function(res){
                            res[0].products = product_id
                            output.push(res[0])
                            flash_message("Promotion retrieved")

                            if (index == results.length - 1) {
                                display_results(output, false);
                            }
                        });

                        ajax_internal.fail(function(res){
                            flash_message(res.responseJSON.message)
                        });
                    })
            });
    
            ajax.fail(function(res){
                flash_message(res.responseJSON.message)
            });
        }
    });

    let display_results = (results = [], update_form = false) => {
        $("#search_results").empty();
        let table = '<table class="table-striped table-bordered">';
        table += '<tr>';
        table += '<th>ID</th>';
        table += '<th>Title</th>';
        table += '<th>Description</th>';
        table += '<th>Promo Code</th>';
        table += '<th>Promo Type</th>';
        table += '<th>Amount</th>';
        table += '<th>Start Date</th>';
        table += '<th>End Date</th>';
        table += '<th>Products</th>';
        table += '<th>Site-wide Status</th>';
        table += '</tr>';
        
        var firstPromotion = "";
        for(var i = 0; i < results.length; i++) {
            var promotion = results[i];
            var row = "<tr><td>"+promotion.id+"</td><td>"+promotion.title+"</td><td>"+promotion.description+"</td><td>"+promotion.promo_code+"</td><td>"+promotion.promo_type+"</td><td>"+promotion.amount+"</td><td>"+promotion.start_date+"</td><td>"+promotion.end_date+"</td><td>"+promotion.products+"</td><td>"+promotion.is_site_wide+"</td></tr>";
            table += row;
            if (i == 0) {
                firstPromotion = promotion;
            }
        }

        table += '</table>';
        $("#search_results").append(table);

        // copy the first result to the form
        if (update_form && firstPromotion != "") {
            update_form_data(firstPromotion)
        }

        flash_message("Search results at the table below")
    }

 });
