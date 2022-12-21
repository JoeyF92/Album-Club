//logic to show edit form
var edit_button = document.getElementsByClassName('edit-button');
var edit_form = document.getElementsByClassName('edit-reveal');

edit_button[0].addEventListener("click", myFunction);

counter = 0;

function myFunction() {
  counter++
  if (counter % 2 == 1)
  {
    edit_form[0].style.display = "block";
  }
  else
  {
    edit_form[0].style.display = "none";
  }
  
}


//rating slider logic:
var ratingSlider = document.getElementById("rating_slider");
var ratingText = document.getElementById("rating_text");
ratingText.innerHTML = ratingSlider.value;

ratingSlider.oninput = function(){
  ratingText.innerHTML = this.value;
}




