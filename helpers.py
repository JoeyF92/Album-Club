import os
import requests
import urllib.parse
import datetime
import cloudinary
#configure cloudinary
cloudinary.config(
    cloud_name="dwxery2ci",
    api_key="136137412315442",
    api_secret="TR1ZEhjcrs_e2s9oiv_6WpSl_p0"
)

import cloudinary.uploader
import cloudinary.api

from flask import Flask, flash, redirect, render_template, request, session
from functools import wraps
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename


#image logic to make sure files in right format
ALLOWED_EXTENSIONS = set(['png','jpg','jpeg','gif'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS 



def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code

def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

def seven_day_check(x):
    d = datetime.datetime.strptime(x, "%Y-%m-%d  %H:%M:%S.%f") 
    now = datetime.datetime.now()                 
    return (d - now).days < 7


def pass_hash(password):
    hash_pass = generate_password_hash(password)
    return str(hash_pass)


def pass_check(password, hashword):
    result = check_password_hash(hashword, password)
    return(result)


def image_upload(request):
        #check if user submitted a url for the image
        image = request.files["image"]
        if not image or image.filename == "" or not image.filename.split(".")[-1].lower() in ALLOWED_EXTENSIONS:
            flash("No image submitted - either upload or enter a url ending in jpg, png or jpeg or gif", "error")
            return None
        #if image uploaded, upload to cloudinary
        filename = secure_filename(image.filename)
        upload_result = cloudinary.uploader.upload(image, folder = "/cs50/album_club/group_images")
        if upload_result:
            #extract the cloudinary url for the image and return it
            image_url = upload_result['url']
            return image_url
        else:
            flash("error uploading image", "error")
            return None




