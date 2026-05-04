// JavaScript Document
var blackBg = document.querySelector(".blackBg");
var p1Element = document.querySelector('.p1');
var p2Element = document.querySelector('.p2');



function showQuiz() {
    p1Element.classList.remove('noShow');
	blackBg.classList.remove('noShow');
}

function showSurvey() {
    p2Element.classList.remove('noShow');
	blackBg.classList.remove('noShow');
}	
	
function closeWindow() {
    p1Element.classList.add('noShow');
    p2Element.classList.add('noShow');
	blackBg.classList.add('noShow');
}
