$(document).ready(function(){
    $("#testimonial-slider").owlCarousel({
        items:1,
        itemsDesktop:[1000,1],
        itemsDesktopSmall:[979,1],
        itemsTablet:[768,1],
        dots: true,
        autoplay: true,
    });

	$(".as_our_blog").owlCarousel({
        items: 3,
        margin: 10,
        nav: true,
        pagination: false,
        responsive: {
            0: {
                items: 1,
            },
            481: {
                items: 1,
            },
            768: {
                items: 2,
            },
            1024: {
                items: 3,
            }
        }

    });
});
$(document).ready(function () {
    if(window.location.pathname.split('/')[2] == 'product'){
        if($('#wrapwrap').length){
            $('#wrapwrap').css('display','grid');
        }
    }
});
