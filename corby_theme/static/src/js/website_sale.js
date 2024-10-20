odoo.define('tadeas_theme.cart', function (require) {
    'use strict';

    var sAnimations = require('website.content.snippets.animation');
    var core = require('web.core');
    var ajax = require('web.ajax');
    var _t = core._t;

    var timeout;

    sAnimations.registry.websiteSaleCartLink = sAnimations.Class.extend({
        selector: '.header_shopping_cart',
        read_events: {
            'mouseenter': '_onMouseEnter',
            'mouseleave': '_onMouseLeave',
        },

        /**
         * @override
         */
        start: function () {
            var def = this._super.apply(this, arguments);
            if (this.editableMode) {
                return def;
            }

            this.$el.popover({
                trigger: 'manual',
                animation: true,
                html: true,
                title: function () {
                    return _t("My Cart");
                },
                container: 'body',
                placement: 'auto',
                template: '<div class="popover mycart-popover" role="tooltip"><div class="arrow"></div><h3 class="popover-header"></h3><div class="popover-body"></div></div>'
            });
            return def;
        },

        //--------------------------------------------------------------------------
        // Handlers
        //--------------------------------------------------------------------------

        /**
         * @private
         * @param {Event} ev
         */
        _onMouseEnter: function (ev) {
            var self = this;
            clearTimeout(timeout);
            $(this.selector).not(ev.currentTarget).popover('hide');
            timeout = setTimeout(function () {
                if (!self.$el.is(':hover') || $('.mycart-popover:visible').length) {
                    return;
                }
                $.get("/shop/cart", {
                    type: 'popover',
                }).then(function (data) {
                    self.$el.data("bs.popover").config.content = data;
                    self.$el.popover("show");
                    $('.popover').on('mouseleave', function () {
                        self.$el.trigger('mouseleave');
                    });
                    $(".popover-cart-carousel").owlCarousel({
                        loop: true,
                        pagination: false,
                        nav: true,
                        autoplay: false,
                        responsiveClass: true,
                        dots: true,
                        responsive: {
                            768: {
                                items: 1
                            },
                            979: {
                                items: 1
                            },
                            479: {
                                items: 1
                            },
                            320: {
                                items: 1
                            },
                            1199: {
                                items: 1
                            },
                        },
                    });
                    $('.popover_remove_product').click(function (ev) {
                        if (confirm('Are you sure you want to Remove this Product?')) {
                            ajax.jsonRpc('/update/cart-qty', 'call', {
                                'product_id': $(ev.target).data('product_id'),
                                'line_id': $(ev.target).data('line_id'),
                                'set_qty': 0,
                            }).then(function (objects) {
                                $(ev.target).closest('.popover-content').empty();
                                location.reload();
                                $('.popover-content').append(
                                    objects + "<script>$('.owl-carousel') .owlCarousel({loop: true,dots: true,nav: true, pagination: false,autoplay: false,margin: 20,responsiveClass: true,responsive: {768: {items: 1},979: {items : 1},479: {items : 1},320: {items : 1},1199: {items : 1},},});</script>"
                                );
                            });
                        }
                    });
                    $('.js_theme_checkout_basket').on('click', function (e) {
                        $('#checkout_theme_form').submit();
                    });
                });
            }, 100);
        },
        /**
         * @private
         * @param {Event} ev
         */
        _onMouseLeave: function (ev) {
            var self = this;
            setTimeout(function () {
                if ($('.popover:hover').length) {
                    return;
                }
                if (!self.$el.is(':hover')) {
                    self.$el.popover('hide');
                }
            }, 1000);
        },
    });
});