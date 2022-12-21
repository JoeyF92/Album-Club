//logic to show albums in different orders for group stats
let statButton = document.getElementsByClassName('stat-button');
let showStats = document.getElementsByClassName('flex-container');

//work out how many stat buttons on page
let length = statButton.length;
console.log(length)
//loop over all the buttons, listening for a click
for (let i=0; i < length; i++)
{
    statButton[i].addEventListener("click", myFunction);
    //if there is a click- set all fields to display none, and just display clicked field
  function myFunction() 
  {


    for (let j=0; j < length; j++)
    {
        showStats[j].style.display = "none";
    } 
    showStats[i].style.display = "flex";
  }
}
