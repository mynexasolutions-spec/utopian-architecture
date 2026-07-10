/*------------------------------------------------------------------
* Project: INTERIOR-PROJECT
* File:    slider.js  — Banner & Testimonial slider initializations
-------------------------------------------------------------------*/
(function ($) {
  "use strict";

  /* Banner Slider (Slick) */
  $(document).ready(function () {
    if ($('.banner-slider1').length && !$('.banner-slider1').hasClass('slick-initialized')) {
      $('.banner-slider1').slick({
        autoplay: true,
        autoplaySpeed: 1000,
        speed: 800,
        infinite: true,
        dots: true,
        arrows: true,
        prevArrow: '<button type="button" class="slick-prev slick-arrow-beautiful"><i class="fa fa-angle-left"></i></button>',
        nextArrow: '<button type="button" class="slick-next slick-arrow-beautiful"><i class="fa fa-angle-right"></i></button>',
        fade: false,
        pauseOnHover: true,
        cssEase: 'cubic-bezier(0.645, 0.045, 0.355, 1.000)'
      });
    }

    /* Testimonial Slider (Swiper) */
    if ($('.testimonial-slider.swiper').length) {
      const $slider = $('.testimonial-slider.swiper');
      new Swiper($slider[0], {
        loop: true,
        speed: 800,
        autoplay: {
          delay: 2500,
          disableOnInteraction: false,
        },
        slidesPerView: 1,
        spaceBetween: 20,
        breakpoints: {
          992: {
            slidesPerView: 3,
          }
        },
        pagination: {
          el: $slider.parent().find('.swiper-pagination')[0],
          clickable: true,
        },
        navigation: {
          nextEl: $slider.parent().find('.swiper-button-next')[0],
          prevEl: $slider.parent().find('.swiper-button-prev')[0],
        },
      });
    }
  });

})(jQuery);
