import os
import uuid
import datetime
#request module allows you to send HTTP requests using Python
import requests
from bs4 import BeautifulSoup
from cs50 import SQL

from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import apology, pass_hash, login_required, image_upload, image_delete, seven_day_check


# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


# Configure app to use SQLite database
db = SQL("sqlite:///database.db")

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    #work out what groups user is a part of if any
    user = session.get('user_id')
    user_groups = db.execute("SELECT group_id FROM user_groups WHERE user_id = ?", user)
    #if user isnt in any groups render homepage:
    if len(user_groups) < 1:
        #create boolean varaible so we can do some rendering logic
        in_groups = False
        return render_template("homepage.html", in_groups=in_groups)
    #if user is a member of a group already, redirect to the groups overview page
    else:
        in_groups = True
        return redirect("/groups")
    
@app.route("/register", methods=["GET", "POST"])
def register():
#if request is a post
    if request.method == "POST":
        if not request.form.get("username"):
            flash("Please enter a username", "error")
            return redirect(request.url)
        if not request.form.get("password"):
            flash("Please enter a password", "error")
            return redirect(request.url)
        if not request.form.get("password_conf"):
            flash("Please confirm password", "error")
            return redirect(request.url)
        if not request.form.get("email"):
            flash("Please enter an email", "error")
            return redirect(request.url)
        #extract username, password (hashing it) and email from form
        username = request.form.get("username")
        if not request.form.get("password") == request.form.get("password_conf"):
            flash("Your passwords don't match", "error")
            return redirect(request.url)
        hashword = pass_hash(request.form.get("password"))
        email = request.form.get("email")
        #stock image for temp profile pic
        image = "https://res.cloudinary.com/dwxery2ci/image/upload/v1669651367/cs50/album_club/alien_nk3x3y.jpg"
        #look at current database, is the username wanted in use?
        current_users = db.execute("SELECT username, email FROM users")
        for x in current_users:
            xuser = x['username']
            email_user = x['email']
            if xuser == username:
                flash("Username already in use!", "error")
                return redirect(request.url)
            if email_user == email:
                flash("Email already in use!", "error")
                return redirect(request.url)
        #else add user, hashed password, email and stock image to the database
        db.execute("INSERT INTO users (username, hash_word, email, image) VALUES(?,?,?,?)", username, hashword, email, image)
        #log user in- by finding new users id and adding to sessions
        new_user = db.execute("SELECT user_id FROM users WHERE username = ?", username)
        #Remember which user has logged in
        session["user_id"] = new_user[0]["user_id"]
        # Redirect user to home page
        return redirect("/")
    else:
        return render_template("register.html")
    

@app.route("/login", methods=["GET", "POST"])
def login():
    # Forget any user_id
    if request.method == "POST":
        # Ensure username and password was submitted
        if not request.form.get("username"):
            flash("Please enter a username", "error")
            return redirect(request.url)
        if not request.form.get("password"):
            flash("Please enter a password", "error")
            return redirect(request.url)
        # check username matched password
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
        if len(rows) != 1 or not check_password_hash(rows[0]["hash_word"], request.form.get("password")):
            flash("Username or Password incorrect", "error")
            return redirect(request.url)
        session.clear()
        # Remember which user has logged in
        session["user_id"] = rows[0]["user_id"]
        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out"""
    # Forget any user_id
    session.clear()
    # Redirect user to login form
    return redirect("/")

@app.route("/edit_profile" , methods=["GET", "POST"])
@login_required
def edit_profile():
    user = session.get('user_id')
    if request.method == "POST":
        #if user editing username
        if request.form['submit_button'] == 'edit_username':
            #check form has username field and it's not blank
            if request.form.get("username") and not request.form.get("username") == "":
                username = request.form.get("username")
                #check username doesnt exist already
                current_users = db.execute("SELECT username FROM users")
                for x in current_users:
                    xuser = x['username']
                    if xuser == username:
                        flash("Sorry username already in use", "error")
                        return redirect(request.url)
                db.execute("UPDATE users SET username=? WHERE user_id=?", username, user)
                flash("username succesfully updated")
                return redirect(request.url)
            else:
                flash("Please submit a username", "error")
                return redirect(request.url)
        #if user changing password - first check all fields present
        if request.form['submit_button'] == 'edit_password':
            if not request.form.get("current_pass") or request.form.get("current_pass") == "":
                flash("Please submit your current password", "error")
                return redirect(request.url)
            if not request.form.get("new_pass") or request.form.get("new_pass") == "":
                flash("Please submit your new password", "error")
                return redirect(request.url)
            if not request.form.get("new_pass_conf") or request.form.get("new_pass_conf") == "":
                flash("Please confirm your new password", "error")
                return redirect(request.url)
            else:
                #check current password correct
                rows = db.execute("SELECT * FROM users WHERE user_id = ?", user)
                if len(rows) != 1 or not check_password_hash(rows[0]["hash_word"], request.form.get("current_pass")):
                    flash("Password Incorrect", "error")
                    return redirect(request.url)
                #check new password and confirmed password are the same 
                if not request.form.get("new_pass") == request.form.get("new_pass_conf"):
                    flash("Your passwords don't match", "error")
                    return redirect(request.url)
                #if they are - update the pass for that user
                hashword = pass_hash(request.form.get("new_pass"))
                db.execute("UPDATE users SET hash_word=? WHERE user_id=?", hashword, user)
                flash("Password updated")
                return redirect(request.url)               
        if request.form['submit_button'] == 'edit_picture':
            #extract image - and update to cloudinary
            image = image_upload(request)
            if image == None:
                return redirect(request.url)
            #upload image to user
            db.execute("UPDATE users SET image=? WHERE user_id=?", image, user)
            flash("Image updated")
            return redirect(request.url)            
        if request.form['submit_button'] == 'delete_picture':
            image = "https://res.cloudinary.com/dwxery2ci/image/upload/v1669651367/cs50/album_club/alien_nk3x3y.jpg"
            db.execute("UPDATE users SET image=? WHERE user_id=?", image, user)
            flash("Image deleted")
            #check user 
            return redirect(request.url)
        else:
            return redirect(request.url)
        
    else:
        user = db.execute("SELECT * FROM users WHERE user_id=?", user)
        user = user[0]
        return render_template("edit_profile.html", user=user)

@app.route("/delete_profile" , methods=["GET", "POST"])
@login_required
def delete_profile():
    user = session.get('user_id')
    if request.method == "POST":
        #check password correct
        if not request.form.get("password"):
            flash("Please enter your password", "error")
            return redirect(request.url)
        rows = db.execute("SELECT * FROM users WHERE user_id = ?", user)
        if len(rows) != 1 or not check_password_hash(rows[0]["hash_word"], request.form.get("password")):
            flash("Password Incorrect", "error")
            return redirect(request.url)
        #work out what groups that user was an admin for 
        group_admin = db.execute("SELECT group_id FROM groups WHERE admin_id = ?", user)
        #delete username and email from the user table
        delete_member = db.execute("UPDATE users SET username = '(deleted profile)', email = '(deleted profile)', image = 'https://res.cloudinary.com/dwxery2ci/image/upload/v1669651367/cs50/album_club/alien_nk3x3y.jpg', hash_word = 'xxxdeleted' WHERE user_id=?", user)
        #if user was a group admin of anything - loop over each group and assign new admin
        if group_admin:
            group_admin_length = len(group_admin)
            for i in range(group_admin_length):
                #select another admin for the group- where user != deleted profile
                new_admin = db.execute("SELECT user_id FROM (SELECT * FROM user_groups INNER JOIN users ON users.user_id= user_groups.user_id WHERE username != '(deleted profile)') WHERE group_id=?", group_admin[i]['group_id'] )
                if new_admin:
                    new_admin = new_admin[0]['user_id']
                    #insert new admin to that group
                    insert_admin = db.execute("UPDATE groups SET admin_id =?", new_admin)
        #delete next submission from any groups user was a member of
        delete_submission = db.execute("DELETE FROM submissions WHERE user_id=?", user)
        flash("Profile Deleted")
        session.clear()
        # Redirect user to login form
        return redirect("/")
    else:
        return redirect("/edit_profile")


#album suggestion route
@app.route("/album_submission/<group_id>/<week>", methods=["GET", "POST"])
@login_required
def album_submission(group_id, week):
    #if request is a post
    user = session.get('user_id')
    group_id = group_id
    if request.method == "POST":
        #check user is a member of that group    
        access_check = db.execute("SELECT user_id FROM user_groups WHERE user_id = ? AND group_id = ?", user, group_id )
        if len(access_check) == 0:
            return apology("Sorry you arn't a member of that group", 400) 
        
        #extract what week is coming up - and then save/update/delete the album to submissions for that week
        week = db.execute("SELECT week_tracker FROM week WHERE group_id=?", group_id)
        week = week[0]['week_tracker']
        upcoming_week = int(week) + 1
        
        #check if user is looking to delete submission:
        if request.form.get("delete"):
            db.execute("DELETE FROM submissions WHERE group_id=? AND user_id=?", group_id, user)
            flash("Submission Deleted")
            return redirect(request.url)        
        #else we move to submitting or updating
        if not request.form.get("album_title"):
            flash("Please enter an album title", "error")
            return redirect(request.url) 
        if not request.form.get("album_artist"):
            flash("Please enter an artist name", "error")
            return redirect(request.url) 
        #get artist, title, reason and url from from form request
        artist = request.form.get("album_artist")
        album = request.form.get("album_title")
        reason = request.form.get("reason")
        #retrive uploaded image - and send to cloudinary
        artwork = image_upload(request)

        #check if there's already been a submission from that user - if there is, update rather than insert
        is_submission = db.execute("SELECT * FROM submissions WHERE group_id=? AND user_id=?", group_id, user)
        if  len(is_submission) > 0:
            #update the route - however check if user inserted new artwork, if they didnt dont update that bit
            if artwork == None:
                db.execute("UPDATE submissions SET artist=?, album=?, reason=? WHERE group_id=? AND user_id=?", artist, album, reason, group_id, user)
                return redirect(request.url)
            else:
                db.execute("UPDATE submissions SET artist=?, album=?, artwork=?, reason=? WHERE group_id=? AND user_id=?", artist, album, artwork, reason, group_id, user)
                return redirect(request.url)
        #if we havent yet got a submission for that user do this:
        else:
            #check artwork uploaded - if it didnt redirect back to the page
            if artwork == None:
                return redirect(request.url)
            else:
                #or insert new submission
                db.execute("INSERT INTO submissions (week, user_id, album, artist, artwork, reason, group_id )VALUES (?, ?, ?, ?, ?, ?, ?)", upcoming_week, user, album, artist, artwork, reason, group_id)
                week = week-1
                #render info to album page        
                return redirect(request.url)
    else:
        return redirect("/new_week/" + group_id + "/" + week)

@app.route("/album_submission/<group_id>/<week>/delete", methods=["GET", "POST"])
@login_required
def album_submission_delete(group_id, week):
    user = session.get('user_id')
    group_id = group_id



#route incase user submits new week with no extra info:
@app.route("/new_week/")
@login_required
def new_week_blank():
    return redirect("/")

#route incase user submits new week with no extra info:
@app.route("/new_week/<group_id>")
@login_required
def new_week_blank_week(group_id):
    return redirect("/")


#get for showcasing current aotw, post for generating a new one:
@app.route("/new_week/<group_id>/<week>", methods=["GET", "POST"])
@login_required
def new_week(group_id, week):
    if request.method == "POST":
        #check there are some albums to pick from
        week = int(week) 
        album_check = db.execute("SELECT * FROM submissions WHERE group_id=? AND week=?", group_id, week+1)
        
        if len(album_check) == 0:
            flash("Sorry there arnt any albums to pick from", "error")
            return redirect(request.url) 

        #add one to the groups current week in sql week tracker + reset the time stamp to now
        time = str(datetime.datetime.now())
        new_week = week + 1
        testing_sql = db.execute("UPDATE week SET week_tracker = week_tracker + 1, Timestamp=? WHERE group_id=?", time, group_id)
        help_me = db.execute("SELECT * FROM week WHERE group_id=?", group_id)
             
        #extract what week it is, so we can pass to template
        week = db.execute("SELECT week_tracker FROM week WHERE group_id=?", group_id)
        week = week[0]['week_tracker']
        
        #pick a random entry from the submissions table:
        random_selection = db.execute("SELECT * FROM submissions WHERE user_id IN (SELECT user_id FROM submissions WHERE group_id=? ORDER BY RANDOM() LIMIT 1) AND group_id=?", group_id, group_id)
        album_picked = random_selection[0]['album']
        artist_picked = random_selection[0]['artist']
        user_picked = random_selection[0]['user_id']
        artwork_picked = random_selection[0]['artwork']
        reason_picked = random_selection[0]['reason']
        
        #work out username from id
        user_name = db.execute("SELECT username FROM users WHERE user_id = ?", user_picked)
        user_name = user_name[0]['username']
        random_selection = random_selection[0]

        #add the album selected to the achive database
        db.execute("INSERT INTO archive (week, user_id, album, artist, artwork, reason, group_id)VALUES (?, ?, ?, ?, ?, ?, ?)", week, user_picked, album_picked, artist_picked, artwork_picked, reason_picked, group_id)
        
        #remove the selected album for the submissions list, so it doesn't get repeated
        db.execute("DELETE FROM submissions WHERE user_id=? AND group_id=?", user_picked, group_id)

        #return render_template("new_week.html", random_selection=random_selection, user_name=user_name, week=week)
        return redirect("/new_week/" + str(group_id) + "/" + str(week))
    else:
        #check user has access to that group
        user = session.get('user_id')
        access_check = db.execute("SELECT user_id FROM user_groups WHERE user_id = ? AND group_id = ?", user, group_id )
        if len(access_check) == 0:
            return apology("Sorry you arn't a member of that group", 400) 
        #check user is accessing latest week for this route- if not just redirect to right page
        latest_week = db.execute("SELECT week_tracker FROM week WHERE group_id=?", group_id)
        latest_week = latest_week[0]['week_tracker']
        latest_week = int(latest_week)
        week = int(week)
        if latest_week > week:
            return redirect("/new_week/" + str(group_id) + "/" + str(latest_week))
        else:
            #if we're on week 1 or greater do the following:
            if week > 0:
                #extract what was selected last (as this is just a get request)
                random_selection = db.execute("SELECT * FROM archive WHERE week=? AND group_id=?", week, group_id)
                random_selection = random_selection[0]
                user_picked = random_selection['user_id']
                user_name = db.execute("SELECT username FROM users WHERE user_id = ?", user_picked)
                user_name = user_name[0]['username']

                #extract comments associated with album
                comments = db.execute("SELECT comment, Timestamp, username, image, users.user_id FROM comments JOIN users ON users.user_id=comments.user_id  WHERE week =? AND group_id=?", week, group_id)



                #extract archive entry information.
                archive = db.execute("SELECT artist, artwork, album, week, username FROM (SELECT * FROM archive INNER JOIN users ON users.user_id= archive.user_id) WHERE group_id = ?", group_id)
                archive_len =(len(archive))

                #work out how many people have suggested albums for next week
                albums_suggested = len(db.execute("SELECT * FROM submissions  WHERE week = ? AND group_id = ?", week+1, group_id))
                

                #extract if user has submission ready for next week:
                next_submission = db.execute("SELECT * FROM submissions WHERE user_id=? AND group_id=? AND week=?", user, group_id, week+1)
                if not next_submission:
                    next_submission = None
                else:
                    next_submission = next_submission[0]      

                #see if user has rated it already, how many others have rated/ and what the average score is
                user_rated = db.execute("SELECT * FROM rating WHERE user_id=? AND group_id=? AND week=?", user, group_id, week)
                #create dict to pass through various ratings stats to template
                ratings_dict = {}
                ratings_dict['user_rating'] = None

                #if we have a user rating for that album, append to dictionary. Creat slider value too to pass through
                if user_rated:             
                    user_rated = user_rated[0]
                    ratings_dict['user_rating'] = user_rated['rating']
                    ratings_dict['slider_value'] = user_rated['rating']
                else:
                    ratings_dict['slider_value'] = 50
               
                #work out average group rating + numbers of raters
                groups_average =  db.execute("SELECT AVG(rating) FROM rating WHERE group_id=? AND week=?", group_id, week)
                ratings_dict['average_rating'] = groups_average[0]['AVG(rating)']
                ratings_count = db.execute("SELECT  COUNT(*) FROM rating WHERE group_id=? AND week=?", group_id, week)
                ratings_dict['ratings_count'] = ratings_count[0]['COUNT(*)']
                return render_template("new_week.html", random_selection=random_selection, user_name=user_name, week=week, comments=comments, archive=archive, archive_len=archive_len, latest_week=latest_week, group_id=group_id, next_submission=next_submission, user=user, user_rated=user_rated, albums_suggested=albums_suggested, ratings_dict=ratings_dict)
            else:
                albums_suggested = len(db.execute("SELECT * FROM submissions  WHERE week = ? AND group_id = ?", week+1, group_id))
                archive_len = 0
                #extract if user has submission ready for next week:
                next_submission = db.execute("SELECT * FROM submissions WHERE user_id=? AND group_id=? AND week=?", user, group_id, week+1)
                if not next_submission:
                    next_submission = None
                else:
                    next_submission = next_submission[0]  
                #logic for whether we show the user the button for generating a new week.
                if albums_suggested < 1:
                    generate_button = False
                else:
                    generate_button = db.execute("SELECT * FROM groups WHERE group_id=? AND admin_id=?", group_id, user)
                    #if user isnt the group admin -check if it's been a week + there are submissions to choose from
                    if not generate_button:
                        #has it been a week yet? get timestamp from week tracker
                        last_week = db.execute("SELECT Timestamp FROM week WHERE group_id =?", group_id)
                        if seven_day_check(last_week[0]['Timestamp']):
                            generate_button = True
                        else:
                            generate_button = False
                    else:
                        generate_button = True
                return render_template("new_week.html", week=week, archive_len=archive_len, albums_suggested=albums_suggested, group_id=group_id, user=user, generate_button=generate_button, next_submission=next_submission)


@app.route("/comment/<group_id>/<week>" , methods=["GET", "POST"])
@login_required
def comment(group_id, week):
    if request.method == "POST":
        #check user is member of the group
        user = session.get('user_id')
        access_check = db.execute("SELECT user_id FROM user_groups WHERE user_id = ? AND group_id = ?", user, group_id )
        if len(access_check) == 0:
            return apology("Sorry you arn't a member of that group", 403) 
            
        #is it a delete or edit request?
        if request.form['submit_button'] == 'delete':
            comment_id = request.form['comment_id']
            db.execute("UPDATE comments SET comment = '(comment deleted)' WHERE comment_id=?", comment_id)
            return redirect(request.url)
         #if edit?
        if request.form['submit_button'] == 'edit':
            user_comment = request.form.get("comment")
            comment_id = request.form['comment_id']
            db.execute("UPDATE comments SET comment = ?, edited = 1 WHERE comment_id=?", user_comment, comment_id)
            return redirect(request.url)
        else:
            #check comment is added
            if not request.form.get("comment"):
                return apology("Please enter the comment, 403")
            #extract comment and insert it into comments database for that week and group
            user_comment = request.form.get("comment")
            db.execute("INSERT INTO comments (week, user_id, comment, group_id) VALUES (?,?,?,?)", week, user, user_comment, group_id)
            return redirect("/new_week/" + group_id + "/" + week)
    else:
        return redirect("/new_week/" + group_id + "/" + week)



#archiveroute for displaying all previous entries in a group:
@app.route("/archive_week/<group_id>")
@login_required
def archive_page(group_id):
    #check user is member of the group
        user = session.get('user_id')
        access_check = db.execute("SELECT user_id FROM user_groups WHERE user_id = ? AND group_id = ?", user, group_id )
        if len(access_check) == 0:
            return apology("Sorry you arn't a member of that group", 403) 
        #get group info to render to page
        group_info = db.execute("SELECT group_name, artwork, group_id FROM groups WHERE group_id = ?", group_id)
        group_info = group_info[0]
        #get previous albums for that group with user rating, and average group rating- we'll order differently so we can render numbers on the page
        week_order = db.execute("SELECT artist, album, group_rating, user_rating, week, username, artwork FROM ( SELECT artist, album, group_rating, week as q1week, username, artwork, q1.user_id as q1user_id FROM (SELECT AVG(rating) as group_rating, artist, album, week, user_id , artwork FROM (SELECT * FROM archive JOIN rating ON rating.week= archive.week WHERE archive.group_id = ?) GROUP BY week ORDER BY group_rating DESC) as q1 JOIN users ON users.user_id =q1.user_id ) as q2 JOIN (SELECT rating as user_rating, week FROM rating WHERE user_id=? AND group_id= ?)  as q3 ON q3.week = q1week ORDER BY week ", group_id, user, group_id)  
        group_order = db.execute("SELECT artist, album, group_rating, user_rating, week, username, artwork FROM ( SELECT artist, album, group_rating, week as q1week, username, artwork, q1.user_id as q1user_id FROM (SELECT AVG(rating) as group_rating, artist, album, week, user_id , artwork FROM (SELECT * FROM archive JOIN rating ON rating.week= archive.week WHERE archive.group_id = ?) GROUP BY week ORDER BY group_rating DESC) as q1 JOIN users ON users.user_id =q1.user_id ) as q2 JOIN (SELECT rating as user_rating, week FROM rating WHERE user_id=? AND group_id= ?)  as q3 ON q3.week = q1week ORDER BY group_rating DESC ", group_id, user, group_id)  
        user_order = db.execute("SELECT artist, album, group_rating, user_rating, week, username, artwork FROM ( SELECT artist, album, group_rating, week as q1week, username, artwork, q1.user_id as q1user_id FROM (SELECT AVG(rating) as group_rating, artist, album, week, user_id , artwork FROM (SELECT * FROM archive JOIN rating ON rating.week= archive.week WHERE archive.group_id = ?) GROUP BY week ORDER BY group_rating DESC) as q1 JOIN users ON users.user_id =q1.user_id ) as q2 JOIN (SELECT rating as user_rating, week FROM rating WHERE user_id=? AND group_id= ?)  as q3 ON q3.week = q1week ORDER BY user_rating DESC ", group_id, user, group_id)  
        #delete line below
        prev_albums = db.execute("SELECT artist, album, group_rating, user_rating, week, username, artwork FROM ( SELECT artist, album, group_rating, week as q1week, username, artwork, q1.user_id as q1user_id FROM (SELECT AVG(rating) as group_rating, artist, album, week, user_id , artwork FROM (SELECT * FROM archive JOIN rating ON rating.week= archive.week WHERE archive.group_id = ?) GROUP BY week ORDER BY group_rating DESC) as q1 JOIN users ON users.user_id =q1.user_id ) as q2 JOIN (SELECT rating as user_rating, week FROM rating WHERE user_id=? AND group_id= ?)  as q3 ON q3.week = q1week ORDER BY week ", group_id, user, group_id)  
        #work out latest week for group so we can do a link to direct to it
        latest_week = db.execute("SELECT week_tracker FROM week WHERE group_id=?", group_id)
        latest_week = latest_week[0]['week_tracker']
        return render_template('group_stats.html', prev_albums=prev_albums, group_info=group_info , group_id=group_id, latest_week=latest_week, week_order=week_order, group_order=group_order, user_order=user_order)
  


#archive route, for looking at previous aotw entrys
@app.route("/archive_week/<group_id>/<week>")
@login_required
def archive_route(group_id, week):
        #check user is member of the group
        user = session.get('user_id')
        access_check = db.execute("SELECT user_id FROM user_groups WHERE user_id = ? AND group_id = ?", user, group_id )
        if len(access_check) == 0:
            return apology("Sorry you arn't a member of that group", 403)        
              
        """ fix this bit """ """ and do logic for if week out of range"""
        if week == None:
            return apology("Something's gone wrong here, 403")
                       
        #repeat logic from new week form - but with the week changed:
        #extract what was selected last (as this is just a get request)
        random_selection = db.execute("SELECT * FROM archive WHERE week=? AND group_id=?", week, group_id)
        random_selection = random_selection[0]
        user_picked = random_selection['user_id']
        user_name = db.execute("SELECT username FROM users WHERE user_id = ?", user_picked)
        user_name = user_name[0]['username']

        #extract comments associated with album
        comments = db.execute("SELECT comment, Timestamp, username, image, users.user_id FROM comments JOIN users ON users.user_id=comments.user_id  WHERE week =? AND group_id=?", week, group_id)


        #extract archive entry information.
        archive = db.execute("SELECT artist, artwork, album, week, reason, username FROM (SELECT * FROM archive INNER JOIN users ON users.user_id= archive.user_id) WHERE group_id=?;", group_id)
        archive_len =(len(archive))
        print(archive_len)
        print("this is the one")
        

        #extract the latest week from the tracker - so we can put some logic in on the page on what is shown:
        latest_week = db.execute("SELECT week_tracker FROM week WHERE group_id=?", group_id)
        latest_week = latest_week[0]['week_tracker']
        week = int(week)

        #see if user has rated it already, how many others have rated/ and what the average score is
        user_rated = db.execute("SELECT * FROM rating WHERE user_id=? AND group_id=? AND week=?", user, group_id, week)
        #create dict to pass through various ratings stats to template
        ratings_dict = {}
        ratings_dict['user_rating'] = None
        #if we have a user rating for that album, append to dictionary. Creat slider value too to pass through
        if user_rated:             
            user_rated = user_rated[0]
            ratings_dict['user_rating'] = user_rated['rating']
            ratings_dict['slider_value'] = user_rated['rating']
        else:
            ratings_dict['slider_value'] = 50
        #work out average group rating + numbers of raters
        groups_average =  db.execute("SELECT AVG(rating) FROM rating WHERE group_id=? AND week=?", group_id, week)
        ratings_dict['average_rating'] = groups_average[0]['AVG(rating)']
        ratings_count = db.execute("SELECT  COUNT(*) FROM rating WHERE group_id=? AND week=?", group_id, week)
        ratings_dict['ratings_count'] = ratings_count[0]['COUNT(*)']
        return render_template("new_week.html", random_selection=random_selection, user_name=user_name, week=week, comments=comments, archive=archive, archive_len=archive_len, latest_week=latest_week, group_id=group_id, ratings_dict=ratings_dict)
        

 
#route for accessing groups - or creating a new one
@app.route("/groups", methods=["GET", "POST"])
@login_required
def groups():
    user = session.get('user_id')
    if request.method == "POST":
        #route for if user creating a new group
        if request.form['submit_button'] == 'create':
            #extract user id from sessions and the other info from request
            admin_id = session.get('user_id')
            if not request.form.get("group_name"):
                flash("Please submit group name", "error")
                return redirect(request.url)
            group_name = request.form.get("group_name")
            description = request.form.get("description")
            #extract image - and update to cloudinary
            image = image_upload(request)
            if image == None:
                return redirect(request.url)
            #generate a unique code for the group using uuid - which we can use for others to join
            group_uuid = str(uuid.uuid1())
                    
            #insert the new group into sql group db
            db.execute("INSERT INTO groups (group_name, admin_id, artwork, description, access_code)VALUES (?, ?, ?, ?, ?)", group_name, admin_id, image, description, group_uuid)
            #update week tracker - setting week to zero for new group + setting the timestamp
            week = 0
            group_id = db.execute("SELECT group_id FROM groups WHERE access_code = ?", group_uuid)
            group_id = group_id[0]['group_id']  
            time = str(datetime.datetime.now())
            db.execute("INSERT INTO week (week_tracker, group_id, Timestamp) VALUES (?, ?,? )", week, group_id, time)
            
            #add the user id and group id to the user groups table
            db.execute("INSERT INTO user_groups (user_id, group_id) VALUES (?, ?)", admin_id, group_id)

            return redirect("groups")
        #route for if entering code to join a group
        else:
            if not request.form.get("group_code"):
                flash("Please enter in group access code", "error")
                return redirect(request.url)
            access_code = request.form.get("group_code")
            #work out group to join from access code
            group_id = db.execute("SELECT * FROM groups WHERE access_code=?", access_code)
            if not group_id:
                flash("Access code Not recognised", "error")
                return redirect(request.url)
            group_id = group_id[0]['group_id']
            #check user isnt already a member:
            check_user = db.execute("SELECT * FROM user_groups WHERE group_id=? AND user_id=?", group_id, user)
            if check_user:
                flash("You're already a member of that group!", "error")
                return redirect(request.url)
            #join current user to that group
            group_insert = db.execute("INSERT INTO user_groups (user_id, group_id) VALUES (?,?)", user, group_id)
            if not group_insert:
                flash("Database error joining you to group", "error")
                return redirect(request.url)
            flash("Successfully joined group", "error")
            return redirect("groups")
    else:
        #render page where you see new groups - and can create a new group
        user = session.get('user_id')
        #find groups that the user is a member of
        user_groups = db.execute("SELECT group_id FROM user_groups WHERE user_id = ?", user)
        
        #loop over user groups -so we can extract infomation from each group to send to template
        total_groups = len(user_groups)
        group_list = []
        for i in range(total_groups):
            #loop over the users groups to extract the ids
            group_id = (user_groups[i]['group_id'])
            #then with that id, extract that groups information
            group_info = db.execute("SELECT *, COUNT(*) AS member_count, username FROM groups INNER JOIN users ON groups.admin_id = users.user_id WHERE group_id =? ", group_id)
            group_info = group_info[0]
            #extract what week each group is in
            week_info = db.execute("SELECT week_tracker FROM week WHERE group_id=?", group_id)
            group_info["week"] = week_info[0]['week_tracker'] 
            #append that groups information to our groups list
            group_list.append(group_info)
            
        return render_template("groups.html", group_list=group_list, total_groups=total_groups)




@app.route("/rating/<group_id>/<week>" , methods=["GET", "POST"])
@login_required
def rating(group_id, week):
    user = session.get('user_id')
    #extract the latest week for that group from the tracker - so we can put some logic in on what route to redirect to:
    latest_week = db.execute("SELECT week_tracker FROM week WHERE group_id=?", group_id)
    latest_week = latest_week[0]['week_tracker']
    if latest_week > int(week):
        redirect_route = "/archive_week/" + group_id + "/" + week
    else:
        redirect_route = "/new_week/" + group_id + "/" + week

    if request.method == "POST":
        #check there is a rating field submitted
        if not request.form.get("rating"):
            flash("No Rating provided", "error") 
            return redirect(redirect_route)
        else:
            #check if there is a rating already from the user for that album
            rating = request.form.get("rating")
            is_rating = db.execute("SELECT * FROM rating WHERE user_id=? AND group_id=? AND week=?", user, group_id, week)
            if not is_rating:
                rating_success = db.execute("INSERT INTO rating (rating, user_id, group_id, week) VALUES (?,?,?,?)", rating, user, group_id, week)
                if not rating_success:
                    flash("Error updating rating", "error")
                    return redirect(redirect_route)
                flash("Sucessfully rated")
                return redirect(redirect_route)
            else:
                print("something here yet")
                rating_success = db.execute("UPDATE rating SET rating=? WHERE user_id=? AND group_id=? AND week=?", rating, user, group_id, week)
                if not rating_success:
                    flash("Error updating rating", "error")
                    return redirect(redirect_route)
                flash("Sucessfully updating rating")
                return redirect(redirect_route)

    
    else:
        return redirect(redirect_route)

#route for users listening history
@app.route("/listening_history")
@login_required
def history():
    user = session.get('user_id')
    ranked_history = db.execute("SELECT album, q1artwork as artwork, artist, rating, group_name, q1group_id FROM ( SELECT album, artwork as q1artwork, artist, archive.group_id as q1group_id, rating FROM archive JOIN rating ON rating.group_id = archive.group_id AND rating.week =archive.week WHERE rating.user_id = (SELECT group_id FROM user_groups WHERE user_id = ?) ) JOIN groups on groups.group_id = q1group_id ORDER BY rating DESC", user)
    return render_template("listening_history.html", ranked_history=ranked_history)



