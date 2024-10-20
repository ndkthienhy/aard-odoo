
$(document).ready(function() {

    /*=============================View Switcher===================*/
    $(".switch_list_view").click(function(e) {
        $(".switch_grid_view").removeClass('disabled')
        $(this).addClass('disabled')
        $('.product-list').addClass("list-view-items");
        $('.product-list').removeClass("grid-view-items");
        localStorage.setItem("product_switch_view", "list");
    });
    $(".switch_grid_view").click(function(e) {
        $(".switch_list_view").removeClass('disabled')
        $(this).addClass('disabled')
        $('.product-list').removeClass("list-view-items");
        $('.product-list').addClass("grid-view-items");
        localStorage.setItem("product_switch_view", "grid");
    });
    if (localStorage.getItem("product_switch_view") == 'list') {
        $(".switch_grid_view").removeClass('disabled')
        $(".switch_list_view").addClass('disabled')
        $('.product-list').addClass("list-view-items");
        $('.product-list').removeClass("grid-view-items");
    }
    if (localStorage.getItem("product_switch_view") == 'grid') {
        $(".switch_list_view").removeClass('disabled')
        $(".switch_grid_view").addClass('disabled')
        $('.product-list').removeClass("list-view-items");
        $('.product-list').addClass("grid-view-items");
    }

    $(".view-mode .switch_list_view").click(function(e) {
        e.preventDefault();
        $('.product-list').addClass("list-view-items");
        $('.product-list').removeClass("grid-view-items");

    });
    $(".view-mode .switch_grid_view").click(function(e) {
        e.preventDefault();
        $('.product-list').removeClass("list-view-items");
        $('.product-list').addClass("grid-view-items");
    });

});