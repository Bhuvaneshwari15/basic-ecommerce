// store.js

$(document).ready(function() {
    var productListDiv = $('#productList');

    // Initial load of products
    loadProducts();

    // Search button click handling
    $('#searchBtn').on('click', function() {
        var query = $('#searchInput').val().trim();
        if (query.length > 0) {
            searchProducts(query);
        } else {
            loadProducts();
        }
    });

    function loadProducts() {
        $.ajax({
            url: '{% url "store" %}', // Adjust URL as per your Django URL configuration
            method: 'GET',
            success: function(response) {
                updateProductList(response.products);
            },
            error: function(xhr, errmsg, err) {
                console.log(xhr.status + ": " + xhr.responseText); // Handle errors
            }
        });
    }

    function searchProducts(query) {
        $.ajax({
            url: '{% url "store" %}?q=' + query, // Adjust URL for search
            method: 'GET',
            success: function(response) {
                updateProductList(response.products);
            },
            error: function(xhr, errmsg, err) {
                console.log(xhr.status + ": " + xhr.responseText); // Handle errors
            }
        });
    }

    function updateProductList(products) {
        productListDiv.empty(); // Clear existing products

        products.forEach(function(product) {
            var card = `
                <div class="col-lg-3 mb-3">
                    <div class="card">
                        <div class="card-body">
                            <h5 class="card-title">${product.name}</h5>
                            <p class="card-text">Price: $${product.price}</p>
                            <a href="#" class="btn btn-primary">Add to Cart</a>
                        </div>
                    </div>
                </div>`;
            productListDiv.append(card);
        });
    }
});
