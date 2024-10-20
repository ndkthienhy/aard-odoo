odoo.define('website_product_advance_filters.product_filters', function(require) {
    "use strict";

    var ajax = require('web.ajax');
    var core = require('web.core');
    var _t = core._t;

    $(document).ready(function() {

        $('.p_cart_header').on('click',function(){
            var $this = $(this);
            var $icon = $this.find('.p_cart_icon');
            if($icon.hasClass('fa-caret-up'))
            {
                $icon.removeClass('fa-caret-up')
                $icon.addClass('fa-caret-down')
            }
            else{
                if($icon.hasClass('fa-caret-down'))
                {
                    $icon.removeClass('fa-caret-down')
                    $icon.addClass('fa-caret-up')
                }
            }
            $this
                .next()
                    .slideToggle();
        });
    });
});