

odoo.define('updat_to_arabic_theme.user_custom_code', function (require) {
'use strict';

$(document).ready(function(){
  console.log('load-----')

     document.getElementById("fixed_img").style.display = "none";

  })

var prevScrollpos = window.pageYOffset;

window.onscroll = function() {
var currentScrollPos = window.pageYOffset;
console.log('555ddd')
  if (prevScrollpos == currentScrollPos) {
    console.log('ddd')
    document.getElementById("fixed_img").style.display = "none";

  } else {
  console.log('block')
    document.getElementById("fixed_img").style.display = "block";}
}



});
