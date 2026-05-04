// JavaScript Document

document.addEventListener("DOMContentLoaded", function () {
  const weekSaleSlides = document.querySelectorAll(".weekSaleSlide");
  let currentweekSaleSlide = 0;

  function showweekSaleSlide(index) {
    weekSaleSlides.forEach((weekSaleSlide, i) => {
      weekSaleSlide.classList.toggle("weekSaleActive", i === index);
    });
  }

  function nextweekSaleSlide() {
    currentweekSaleSlide = (currentweekSaleSlide + 1) % weekSaleSlides.length;
    showweekSaleSlide(currentweekSaleSlide);
  }

  // 載入後立即顯示第一張圖片
  showweekSaleSlide(currentweekSaleSlide);

  setInterval(nextweekSaleSlide, 4000);
});