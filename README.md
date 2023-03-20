# Album-Club

This was my independant final project completed for CS50

#### Video Demo:  https://youtu.be/-rCJeGRuk6o
## Description:

## Website overview:
A website for friends to share and discover and talk about music. The site allows you to register and join and create groups to generate albums of the week to listen to, discuss and score. Each group documents the listening history so the users can see how the albums then are ranked in comparison- and also the user has access to a personal history which will show all the albums for every group they're involved with and ordered how the user rated them

## Features
Python, Flask, Javascript, HTML, CSS, Jinja and SQLite3

### SQLite Database 
For the app to work, I needed to implement the following tables in SQLITE:

#### A users table:
This stored the users information - usernames, email, hashed password, an image for a profile picture and an id

#### A groups table:
This stored information on any groups made-including name, image, who is the admin (which is a user id) (admin is able to generate new weeks early), a description about the group, an access code (to allow other people to join) and an id number each group

#### A week tracker
This documents what week each group is on- it has week as an integer, the groups id, and a timestamp field so we can work out if a week has passed since the last album

#### A submission table
This keeps track of users album suggestions- it stores user id and group id and album information- so we know which group the user is suggesting the album for. It also keeps track of the week.

#### An Archive table
When the generate new album button is clicked, we use sql to pick from random 1 album for that group from the submissions table. This is then moved into the archive table. Here we keep track of the albums info, the groups id, the user id (so we know who picked it) and what week it was

#### User groups table
this keeps track of what groups, users are members of - we have a groupid and userid field

#### Comments table
This is where we keep track of comments made about albums - we have the user id, the comment, a timestamp, the groupid, what week it is, an edited field to let people know if comment has been edited.


#### Rating table 
Finally this is where we keep track of scores- we have the group id, what week it is, the user id, and what the rating was out of 100


## How it works

### Registering

When a new user clicks on the register button, they're taken to the register page and can enter details. Upon submitting, this triggers the /register post route in the app.py.

Here we check all fields are entered, check the username and email is unique by querying the user table. We hash the password, using the pass_hash function which is defined in helpers.py. This in turn users pass_hash_generator from werkzeug.security.

Any issues we flash the user (using flash from flask)- detail the error and return them back to the page they were on.

If no problems, we create a new user by inserting into users table

To avoid having to log in straight after, we then query the user table again to find out what the id generated is for the user. Then we log the user in automatically. By adding the id to sessions. (using sessions from flask_sessions)


### Logging in
Utilising sessions, if user tries to access any page while not logged in we are directed to the /login page. 

It has a form with log in information - upon submitting this, this triggers the post route for /login

Here we check user has submitted all the information - and then we query the group table to see if the user exists, and then utilist the check_password_hash function from helpers.py to see if the password matches the user (again from werkzeug.security).

Once logged in the user is taken to the groups.html page

### Log out route 
If user clicks log out, we send a post reuqest to logout - which clears session and returns them to the homepage

### Editing profile
We have a route for is the users want to make changes to the profile when they access the edit_profile page. They can change username and password (the latter checks the old password is correct first)
They can upload a photo - by default the users photo is a picture of an alien.
Here we utilise cloudinary to store images. 

If a user decides to submit a photo, we use the image_upload function from helpers.py. Inside helpers we have imported cloudinary and configured it. So when a user uploads a photo, we check it's a jpg/png/etc - and then it goes to cloudinary, cloudinary then returns the url for the image - which we then store in the user table.

The user can delete the image - which will revert them back to the alien. 

### Delete profile

From the edit_profile page there is also a button to delete their profile. Which submits a post request to /delete_profile.

User has to enter password- and if correct, we update the user table- setting username and email to 'deleted profile' (as we still want to keep their scores and comments - just anonymised)

We also query the group table and check if that userid was an admin for any groups. If so we query the groups table, joined with the user table and select the next user in the group that hasnt been deleted as the admin. (updating the table)

finally we clear session - and return user to homepage.

### Homepage
Once user is logged in a get request goes to /groups and we're directed to the /groups.html page

When a get request goes to /groups
we access the user_id from sessions - query the user groups table to find what groups the user is a member of - and extract the group info - which we render to the /groups template.

The user can now see the groups they are part of - including picture, member count and a links to access the groups new album of the week and the groups history.

The user can also create a new group themselves - and they can enter a group code to join another group too.

on the post route we check if it was a create button - if so we check user has submitted a group name,description, image. We use the users id as admin id for the group -and finally we create a unique code for the group using str(uuid.uuid1()).
With all this info, we insert a new group in the sql group table adding  week as 0 and timestamp to now (with datetime module)

if the user clicks the group_code button, instead we extract the code used from the form - and query the groups datebase for that code. IF it exists, we add that users id to that group. (unless they are a member already)

### Group album of the week pages
if the user clicks on the current week link for a group - it will request a get route for the /new_week/<group_id>/<week> route.

Here we check the userid from sessions is part of the group of the group_id requested- by querying the user groups table.

We check the week on the url matches the latest week for the group by querying the week table- looking up the group id.

If it's a new group - there wont be much to display on the page. Except asking the user for a suggestion for the next week.

If not, the get request queries the database- extracting what the album of that week is for that group and that week from archive table. It queries the comments table for all comments associated for that week and finally what the average rating is for that week- which is all rendered on to the template.

Finally - the route also does some logic to decide whether the generate new week button is displayed. If the user is either an admin for the group or it has been 1 week, it is rendered. To check is user is an admin, we query the group table for the admin id. TO see if it's been a week, we use the seven_day_check function from helpers - this compares the timestamp from the week table for that group and checks if it's been 7 days from now using(datetime.datetime.strptime)

If the user clicks the generate new week button, this generates a post request to the same route. 

This route, checks there are albums to choose from for the group, querying the submissions table.

If there is, we update the week to week+1 for the week table for the group. 

We then use sql to pick a random album from the submissions table with the group id. This gets inserted in to the archive table (with the group id and week)- and then deleted from submissions so it cant be selected again.

Next we're redirected back to the new_week/group_id_/week -- which will now show the new album of the week

### Group History

On either the homepage or the album of the week for a group age, the user can click a link to see the groups history. The link sends a get request to /archive_week/<group_id>

Here we check the user is a member for that group - querying the user groups table.

if user is a member, we query the database. taking all the album information for each week for that group, and the average groups rating for each album. Saving the information in a dict

Next we loop over the dict and on each week, query the db for the users individual rating for each week in the group.

Finally we sort the dict three ways - one by week, one by group rating, one by user rating and render to the group.stats.html page. 

On the page we loop over each album, showing them on the page. IN the group-stats.js file we listen for the user clicking on how they want to visualise the page - for example if they click user rating ascending, we see all albums from that loop. All the other loops are hidden.

### Archive route
On each album on the group stats page, the user can access the achived album of the week page for that album. This works exactly the same as the new_week/<group_id>/<week> route - except in this instance the route becomes archive_week/<group_id>/<week>

### Commenting
On any album of the week or archive week page there is a comment box. If there is any post to /comment/<group_id>/<week>

we check user is a member of the group - then check if user is posting new comment, editing or deleting.

If it's a new comment, we insert into the comments database the user comment, where the group id is x and the user is x

if it's an edit or delete - first to access this form the user clicks edit on the page, and through the groups.js we listen for this and reveal a form.

If the user edits - we extract the comment and then update the comments table where the comment id is x. We also update the edited field to be 1, indicting its an edited comment which we can mention next to the comment.

if it's a delete - we update the comment in the comment table where the comment id is x, to be "comment deleted"

### Rating
On the album of the week and archive week pages, the user can utilise a slider to submit their rating for the album. We use javascript to listen for the slider moving and adjust the html reading for it depending on its location. 

Upon submitting, a post request is sent to /rating/<group_id>/<week>. And providing the user is a member of the group and they have submitted a rating, we will insert a rating into the ratings table (out of 100), where user id = x, group id = x, week = x.

If the user has already rated - we will update the rating instead.

### Listening history
Finally the listening history page shows all the albums the user has listened to for any group it is a member for. If a get request is sent to /listening_history We query the database for the all the groups the user is a member of and extract the albums and users ratings for them.

This is the passed through as context to the listening_history template- where the user will see the albums listened to in order of their ranking.

