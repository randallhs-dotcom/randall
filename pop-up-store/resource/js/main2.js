var termsTitle, startHour;
var navItems = [];
var focusItems = [];
var saleItems = [];
var topicItems = [];
var topicNames = [];
var topicUrls = [];
var categoryCaption = [];
var venueItems = [];
var activeDays = [];
var activeHours = [10,11,12,13,14,15,16,17,18,19,20,21,22,23];

jQuery(function ($) {
  //push topics name and url into array for slider using
  for (var i in topicItems) {
    topicNames.push([topicItems[i].name]);
    topicUrls.push([topicItems[i].url]);
  };

  //init
  $(document).ready(function () {
    //navigation
    $('.nav-item').each(function (index) {
      $(this).attr('href', navItems[index].url)
        .append(navItems[index].name)
        .find('.img-nav').attr('alt', navItems[index].name);
    });

    //name and link of focus banners
    $('.focus-item').each(function (index) {
      $(this).attr({
        'href': focusItems[index].url,
        'title': focusItems[index].name
      })
        .find('.img-focus').attr('alt', focusItems[index].name);
    });

    //name and link of sale banners
    $('.sale-item').each(function (index) {
      $(this).attr({
        'href': saleItems[index].url,
        'title': saleItems[index].name
      })
        .find('.img-sale').attr('alt', saleItems[index].name);
    });

    //create category container
    $('.categories').append(
      categoryContainer()
    );

    //name of category
    $('.product-caption').each(function (index) {
      $(this).html(categoryCaption[index]);
    });

    //name and link of venues
    $('.venue-item').each(function (index) {
      $(this).attr({
        'href': venueItems[index].url,
        'title': venueItems[index].name
      })
        .find('.img-venue').attr('alt', venueItems[index].name);
    });

    //term title
    $('.terms-title').html(termsTitle);
  });

  //create category container
  function categoryContainer() {
    var containerDiv = '';
    for (var i = 1; i <= categoryCaption.length; i++) {
      containerDiv += '<a id="list' + i + '"></a>';
      containerDiv += '<div class="products py-3" style="background-image: url(images/bg-list' + i + '.png">';
      containerDiv += '<div class="container">';
      containerDiv += '<h3 class="product-caption text-center mb-3 py-2" style="background-image: url(images/product-caption' + i + '.png"></h3>';
      containerDiv += '<div class="product-list row" id="productlist_' + i + '"></div>';
      containerDiv += '</div></div>';
    };
    return containerDiv;
  };

  //slider
  function getToday() {
    let today = new Date()
    let month = today.getMonth() + 1
    let day = today.getDate()
    return Number(today.getFullYear() + ((month > 9 ? '' : '0') + month) + ((day > 9 ? '' : '0') + day))
  }
  var initialSlide = 0
  // var today = getToday()
  // initialSlide = activeDays.indexOf(getToday().toString()) >= 0 ? activeDays.indexOf(getToday().toString()) : 0
  // if (new Date().getHours() < startHour) {
  //   initialSlide = (initialSlide - 1) >= 0 ? initialSlide - 1 : 0
  // }
  initialSlide = activeHours.indexOf(new Date().getHours()) >= 0 ? activeHours.indexOf(new Date().getHours()) : 0

  var topicBanners = new Swiper('.slider-topics', {
    initialSlide: initialSlide,
    slidesPerView: 'auto',
    spaceBetween: 8,
    loop: true,
    mousewheel: true,
    grabCursor: true,
    centeredSlides: true,
    breakpoints: {
      768: {
        slidesPerView: 3,
      },
    },
    pagination: {
      el: '.swiper-pagination',
      clickable: true,
    },
    navigation: {
      nextEl: '.swiper-button-next',
      prevEl: '.swiper-button-prev',
    },
    on: {
      init: function () {
        //link and alternate of slides
        $('.topic-item').each(function (index) {
          $('.topic-item' + (index + 1)).attr({
            'href': topicUrls[index],
            'title': topicNames[index]
          })
            .find('.img-slide').attr('alt', topicNames[index]);
        });
      },
    }
  });

  //toggle affix
  $('.btn-toggle-nav').on('click', function () {
    $(this).removeClass('show');
    $('.nav-affix').addClass('show');
  });
  $('.btn-close-nav').on('click', function () {
    $('.nav-affix').removeClass('show');
    $('.btn-toggle-nav').addClass('show');
  });

  var currentPosition = $(window).scrollTop();
  $(window).on('scroll', function () {
    var currentScroll = $(window).scrollTop();
    var scrollHeight = $(document).height();
    var scrollPosition = $(window).height() + currentScroll;

    //when begining to scroll AND scroll going up OR scroll below the fold
    if (currentScroll > 0 && currentScroll < currentPosition || (scrollHeight - scrollPosition) / scrollHeight === 0) {
      $('.btn-gotop').addClass('show');
    }
    else {
      $('.btn-gotop').removeClass('show');
    }

    //header
    if (currentScroll > 56) {
      $('.l-header').addClass('scrolled');
      $('.bbbar ').addClass('scrolled');
    }
    else {
      $('.l-header').removeClass('scrolled');
      $('.bbbar ').removeClass('scrolled');
    }

    currentPosition = currentScroll;
  });

  

  
  
  
  
  //go to top
  $('.btn-gotop').on('click', function () {
    $('html, body').animate({
      scrollTop: 0
    }, 'fast', 'swing');
    return false;
  });

  
  
  
  //下拉選單share
  $('.dropdown-toggle').dropdown();
  var pageUrl = window.location;
  $('.btn-share').on('click', function () {
    if ($(this).attr('data-share') == 'facebook') {
      window.open('https://www.facebook.com/sharer.php?u=' + pageUrl);
    }
    else if ($(this).attr('data-share') == 'line') {
      window.open('https://line.naver.jp/R/msg/text/?' + pageUrl);
    }
  });
});



//手機底部面板
$('.other_loaction').on('click', function (e) {
  e.preventDefault();
  if ($('.leftnav').hasClass('tab-show')) {
    $('.leftnav').removeClass('tab-show');
  } else {
    $('.leftnav').addClass('tab-show');
  }
})
$('.leftnav_list-dismiss').on('click', function (e) {
  $('.leftnav').removeClass('tab-show');
})






jQuery(function ($) {
    //copy to clipboard
    $('.btn-copy-clipboard').on('click', function () {
      var value = $(this).data('content');
      var $temp = $("<input>");
      $("body").append($temp);
      $temp.val(value).select();
      document.execCommand("copy");
      $temp.remove();
      $('#snackbar').addClass('show')
        .find('.snackbar-dialog').html("已複製折扣碼");
      setTimeout(
        function () {
          $('#snackbar').removeClass('show');
        }, 2000);
    });
  });
  
  
 /* 設定倒數時間 */
$(function(){   countDown("2021/1/30 00:00:00","#colockbox1");  }); 
function countDown(time,id){ 
  var day_elem=$(id).find('.day'); 
  var hour_elem=$(id).find('.hour'); 
  var minute_elem=$(id).find('.minute'); 
  var second_elem=$(id).find('.second'); 
  var end_time = new Date(time).getTime();
  var sys_second = (end_time-new Date().getTime())/1000; 
  var timer = setInterval(function(){ 
    if(sys_second>1) { 
      sys_second-=1; 
      var day=Math.floor((sys_second/3600)/24); 
      var hour=Math.floor((sys_second/3600)%24); 
      var minute=Math.floor((sys_second/60)%60); 
      var second=Math.floor(sys_second%60); 
      $(day_elem).text(day);
      $(hour_elem).text(hour<10?"0"+hour:hour);
      $(minute_elem).text(minute<10?"0"+minute:minute); 
      $(second_elem).text(second<10?"0"+second:second);
    } 
    else { 
      clearInterval(timer); 
    } 
  }, 1000); 
} 
  
  
  
  
  
  $(".navbar-toggler").click(function () {
    // 當點擊上述被選擇的元素後，要執行的流程
    console.log("點到按鈕了!!")
    // 小駝峰命名法 signInWithGoogle && signInWithEmailAndPassword
    // 選.navbar-list 並為它「切換」 class="active"
    // addClass() 新增class
    $(".navbar-list").toggleClass("active")
    $(".line").toggleClass("rotate")
})
  
  
  
  
  





  
  


var mySwiper = new Swiper('.swiper-container',{
slidesPerView: 8.5,
  spaceBetween: 40,
    breakpoints: { 
    
    320: {
      slidesPerView: 4.5,
      spaceBetween: 10
    },
  
    480: { 
      slidesPerView: 4.5,
      spaceBetween: 20
    },
   
    640: {
      slidesPerView: 8.5,
      spaceBetween: 30
    }
  }
})

  
  


var mySwiper = new Swiper('.swiper-container-2',{
slidesPerView: 4,
  spaceBetween: 40,

	   autoplay: {
        delay: 2500,
        disableOnInteraction: false,
      }, 
  breakpoints: { 
    
    320: {
      slidesPerView: 3,
      spaceBetween: 10
    },
  
    480: { 
      slidesPerView: 3,
      spaceBetween: 20
    },
   
    640: {
      slidesPerView: 4,
      spaceBetween: 30
    }
  }
})





var mySwiper = new Swiper('.swiper-container-3',{
slidesPerView: 1,
  spaceBetween: 40,
  autoplay: {
        delay: 2500,
        disableOnInteraction: false,
      },
      pagination: {
        el: '.swiper-pagination',
        clickable: true,
      },
  breakpoints: { 
    
    320: {
      slidesPerView: 1,
      spaceBetween: 10
    },
  
    480: { 
      slidesPerView: 1,
      spaceBetween: 20
    },
   
    640: {
      slidesPerView: 1,
      spaceBetween: 30
    }
  }
})


var mySwiper = new Swiper('.swiper-container-4',{
slidesPerView: 1,
  spaceBetween: 40,
  autoplay: {
        delay: 2500,
        disableOnInteraction: false,
      },
      pagination: {
        el: '.swiper-pagination',
        clickable: true,
      },
  breakpoints: { 
    
    320: {
      slidesPerView: 1,
      spaceBetween: 10
    },
  
    480: { 
      slidesPerView: 1,
      spaceBetween: 20
    },
   
    640: {
      slidesPerView: 1,
      spaceBetween: 30
    }
  }
})



