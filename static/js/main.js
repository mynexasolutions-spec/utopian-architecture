/*------------------------------------------------------------------
* Project:        Intereal - Architecture & Interior Design HTML Templates
* Author:         HtmlDesign Templates
* URL:            https://themeforest.net/user/htmldesigntemplates/portfolio
* Created:        11/14/2025
-------------------------------------------------------------------*/


(function ($) {
  "use strict";

  /* SlickNav Responsive Menu */
  $('#responsive-menu').slicknav({
    duration: 500,
    easingOpen: 'easeInExpo',
    easingClose: 'easeOutExpo',
    closedSymbol: '<i class="arrow-indicator fa fa-angle-down"></i>',
    openedSymbol: '<i class="arrow-indicator fa fa-angle-up"></i>',
    prependTo: '#slicknav-mobile',
    allowParentLinks: true,
    label: ""
  });

  /* Dropdown Menu */
  var selected = $('#navbar li');
  selected.on("mouseenter", function () {
      $(this).find('ul').first().stop(true, true).delay(350).slideDown(500, 'easeInOutQuad');
  }).on("mouseleave", function () {
      $(this).find('ul').first().stop(true, true).delay(100).slideUp(150, 'easeInOutQuad');
  });

  /* Arrow Indicator for Submenus */
  if ($(window).width() > 992) {
      $(".navbar-arrow ul ul > li").has("ul").children("a").append("<i class='arrow-indicator fa fa-angle-right'></i>");
  }
  

  /* Sticky Header */
  let $headerMenu = $('.header-nav-menu');

  $(window).on('scroll', function () {
    let curScroll = $(window).scrollTop();

    if (curScroll > 80) {
        $headerMenu.addClass('navbar-sticky-in');
    } else {
        $headerMenu.removeClass('navbar-sticky-in');
    }
  });

     /* Back-to-top js Start */
    $(document).ready(() => {
      $('#back-to-top, .fast-service-badge').hide(); // Hide button initially
  
      $(window).on('scroll', () => {
          if ($(window).scrollTop() > 500) {
              $('#back-to-top, .fast-service-badge').fadeIn(200);
          } else {
              $('#back-to-top, .fast-service-badge').fadeOut(200);
          }
      });
  
      $(document).on('click', '#back-to-top, .back-to-top', () => {
          $('html, body').animate({
              scrollTop: 0
          }, 500);
          return false;
      });
    });
    

  /* Counter for progress bar start */
  let valueDisplayss = document.querySelectorAll(".progress-num");
  let intervall = 3000;

  valueDisplayss.forEach((valueDisplay) => {
      let startValue = 0;
      let endValue = parseInt(valueDisplay.getAttribute("data-val"),10);
      let duration = Math.floor(intervall / endValue);
      let counter = setInterval(function() {
          startValue += 1;
          valueDisplay.textContent = startValue;
          if (startValue === endValue) {
              clearInterval(counter);
          }
      }, duration);
  });

  /* Counter for progress bar start */

  /* Countdown Timer */
    const targetTime = new Date(Date.now() + 100 * 24 * 60 * 60 * 1000); // 100 days from now
    function updateCountdown() {
      const now = Date.now();
      const diff = targetTime - now;
      if (diff <= 0) {
        clearInterval(interval);
        $('#days, #hours, #minutes, #seconds').text('00');
        return;
      }
      
      const d = Math.floor(diff / (1000 * 60 * 60 * 24));
      const h = Math.floor((diff / (1000 * 60 * 60)) % 24);
      const m = Math.floor((diff / (1000 * 60)) % 60);
      const s = Math.floor((diff / 1000) % 60);

      $('#days').text(d);
      $('#hours').text(h.toString().padStart(2, '0'));
      $('#minutes').text(m.toString().padStart(2, '0'));
      $('#seconds').text(s.toString().padStart(2, '0'));
    }
    
    updateCountdown();
    const interval = setInterval(updateCountdown, 1000);
  /* Countdown Timer */

  // Video Player
  document.addEventListener('DOMContentLoaded', function () {
    const videoInline = document.querySelector('.video-inline');
    if (videoInline) {
      videoInline.addEventListener('click', function(e){
        e.preventDefault();
        const src = this.getAttribute('data-src');
        this.innerHTML = `<iframe src="${src}?autoplay=1" width="100%" height="500" allow="autoplay; fullscreen" frameborder="0"></iframe>`;
      });
    }
  });

  // Slick Slider //

  // Banner Slider
  $('.banner-slider').slick({
    slidesToShow: 1,
    slidesToScroll: 1,
    autoplay: true,
    autoplaySpeed: 6000,
    arrows: false,
    dots: false,
    fade: true,  
    speed: 800, 
    cssEase: 'linear'
  });

  $('.partner-slider').slick({
    slidesToShow: 4,
    slidesToScroll: 1,
    autoplay: true,
    autoplaySpeed: 4000,
    arrows: false,
    dots: false,
    responsive: [
      { breakpoint: 1100, settings: { slidesToShow: 3, slidesToScroll: 1 } },
      { breakpoint: 600, settings: { slidesToShow: 1, slidesToScroll: 1 } },
    ]
  });

  $('.partner-slider1').slick({
    slidesToShow: 5,
    slidesToScroll: 1,
    autoplay: true,
    autoplaySpeed: 4000,
    arrows: false,
    dots: false,
    responsive: [
      { breakpoint: 1100, settings: { slidesToShow: 3, slidesToScroll: 1 } },
      { breakpoint: 600, settings: { slidesToShow: 1, slidesToScroll: 1 } },
    ]
  });

  $('.review-slider').slick({
    slidesToShow: 2,
    slidesToScroll: 1,
    autoplay: true,
    autoplaySpeed: 3000,
    arrows: true,
    dots: true,
    prevArrow: '<button type="button" class="slick-prev"><i class="fa fa-angle-left"></i></button>',
    nextArrow: '<button type="button" class="slick-next"><i class="fa fa-angle-right"></i></button>',
    responsive: [
      {
        breakpoint: 992,
        settings: {
          slidesToShow: 2,
          slidesToScroll: 1,
          arrows: true,
          dots: true
        }
      },
      {
        breakpoint: 600,
        settings: {
          slidesToShow: 1,
          slidesToScroll: 1,
          arrows: false,
          dots: true
        }
      }
    ]
  });

  $('.review-slider1').slick({
    slidesToShow: 1,
    slidesToScroll: 1,
    autoplay: true,
    autoplaySpeed: 3000,
    arrows: false,
    dots: false,
  });

  $('.banner-slider1').slick({
    slidesToShow: 1,
    slidesToScroll: 1,
    autoplay: true,
    autoplaySpeed: 1000,
    arrows: true,
    prevArrow: '<button type="button" class="slick-prev slick-arrow-beautiful"><i class="fa fa-angle-left"></i></button>',
    nextArrow: '<button type="button" class="slick-next slick-arrow-beautiful"><i class="fa fa-angle-right"></i></button>',
    dots: true,
    fade: true,  
    speed: 800, 
    cssEase: 'linear'
  });

  $('.testimonial-slider:not(.swiper)').slick({
    slidesToShow: 3,
    slidesToScroll: 1,
    autoplay: false,
    autoplaySpeed: 4000,
    arrows: false,
    dots: true,
    responsive: [
      { breakpoint: 1400, settings: { slidesToShow: 2, slidesToScroll: 1 } },
      { breakpoint: 976, settings: { slidesToShow: 1, slidesToScroll: 1 } }
    ]
  });

  /* ========================================= */
  /*             Gallery & Lightbox             */
  /* ========================================= */
  $(document).ready(function() {
    // Only execute if we are on a page with gallery filters/lightbox
    if (!$('.gallery-filter-btn').length && !$('.gallery-item').length) return;

    var $filterBtns = $('.gallery-filter-btn');
    var $galleryItems = $('.gallery-item');
    var $lightbox = $('#gallery-lightbox');
    var $lightboxImg = $('.lightbox-img');
    var $lightboxCounter = $('.lightbox-counter');
    var $activeItems = $galleryItems; // Keeps track of currently visible items for sliding
    var currentIndex = 0;

    // 1. Filtering Logic
    $filterBtns.on('click', function() {
      var filterValue = $(this).attr('data-filter');
      
      // Update active tab styling
      $filterBtns.removeClass('active');
      $(this).addClass('active');

      if (filterValue === 'all') {
        $galleryItems.fadeIn(300);
        $activeItems = $galleryItems;
      } else {
        $galleryItems.each(function() {
          var category = $(this).attr('data-category');
          if (category === filterValue) {
            $(this).fadeIn(300);
          } else {
            $(this).fadeOut(200);
          }
        });
        // Update active items list to exclude hidden ones
        $activeItems = $galleryItems.filter('[data-category="' + filterValue + '"]');
      }
    });

    // 2. Lightbox Show Logic
    $galleryItems.on('click', function() {
      // Find the index of the clicked item relative to the currently active (filtered) items
      var clickedSrc = $(this).find('img').attr('src');
      currentIndex = $activeItems.map(function() {
        return $(this).find('img').attr('src');
      }).get().indexOf(clickedSrc);

      if (currentIndex === -1) {
        currentIndex = 0;
      }

      openLightbox();
    });

    function openLightbox() {
      if ($activeItems.length === 0) return;
      var currentItem = $activeItems.eq(currentIndex);
      var imgSrc = currentItem.find('img').attr('src');
      var imgAlt = currentItem.find('img').attr('alt');

      $lightboxImg.attr('src', imgSrc).attr('alt', imgAlt);
      updateCounter();

      $lightbox.addClass('active').attr('aria-hidden', 'false');
      $('body').css('overflow', 'hidden'); // Lock background scroll
    }

    function closeLightbox() {
      $lightbox.removeClass('active').attr('aria-hidden', 'true');
      $('body').css('overflow', ''); // Restore background scroll
    }

    function updateCounter() {
      var displayIndex = currentIndex + 1;
      var total = $activeItems.length;
      $lightboxCounter.text(displayIndex + ' / ' + total);
    }

    // 3. Slider Navigation Logic
    function nextImage() {
      if ($activeItems.length <= 1) return;
      currentIndex = (currentIndex + 1) % $activeItems.length;
      updateLightboxImage();
    }

    function prevImage() {
      if ($activeItems.length <= 1) return;
      currentIndex = (currentIndex - 1 + $activeItems.length) % $activeItems.length;
      updateLightboxImage();
    }

    function updateLightboxImage() {
      var currentItem = $activeItems.eq(currentIndex);
      var imgSrc = currentItem.find('img').attr('src');
      var imgAlt = currentItem.find('img').attr('alt');
      
      // Smooth cross-fade effect in lightbox
      $lightboxImg.fadeOut(150, function() {
        $(this).attr('src', imgSrc).attr('alt', imgAlt).fadeIn(150);
      });
      updateCounter();
    }

    // Event Listeners for Lightbox
    $('.lightbox-close').on('click', function(e) {
      e.stopPropagation();
      closeLightbox();
    });

    $('.lightbox-next').on('click', function(e) {
      e.stopPropagation();
      nextImage();
    });

    $('.lightbox-prev').on('click', function(e) {
      e.stopPropagation();
      prevImage();
    });

    // Close on clicking the dark background overlay itself, but not the image
    $lightbox.on('click', function(e) {
      if ($(e.target).is('#gallery-lightbox') || $(e.target).is('.lightbox-content')) {
        closeLightbox();
      }
    });

    // Keyboard Navigation
    $(document).on('keydown', function(e) {
      if (!$lightbox.hasClass('active')) return;

      if (e.key === 'ArrowRight') {
        nextImage();
      } else if (e.key === 'ArrowLeft') {
        prevImage();
      } else if (e.key === 'Escape') {
        closeLightbox();
      }
    });
  });

})(jQuery);
