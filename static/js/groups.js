//logic to show edit forms - first select edit button and the form to reveal
let edit_button = document.getElementsByClassName('edit-button');
let edit_form = document.getElementsByClassName('edit-reveal');

//work out how many edit buttons on page
let length = edit_button.length;
//create array of 0s which we use for working out if show or hide edit form
counter = [];
for (let i=0; i < length; i++)
{
  counter[i] = 0;
} 

//now loop over all the buttons, listening for a click
for (let i=0; i < length; i++)
{
  edit_button[i].addEventListener("click", myFunction);
  //if there is a click, add one to that buttons counter - and then either display or hide it's content
  function myFunction() 
  {
    counter[i] +=1;
    if (counter[i] % 2 == 1)
    {
      edit_form[i].style.display = "block";
      edit_button[i].innerHTML = "Exit";
    }
    else
    {
      edit_form[i].style.display = "none";
      edit_button[i].innerHTML = "Edit";
    }   
  }
}



//rating slider logic:
var ratingSlider = document.getElementById("rating_slider");
var ratingText = document.getElementById("rating_text");
ratingText.innerHTML = ratingSlider.value;

ratingSlider.oninput = function(){
  ratingText.innerHTML = this.value;
}



