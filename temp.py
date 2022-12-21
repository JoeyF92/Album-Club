
"""
#Here i'm using BS to read a html file
with open("templates/Screamadelica.html", "r") as f:
doc = BeautifulSoup(f, "html.parser")

#printing it into the terminal - use prettify to have it nicely formatted
print(doc.prettify())
tag =doc.title
print(tag)
"""

#get spotify api token

# we send a post request to this url
auth_url = 'https://accounts.spotify.com/api/token'
#create a dictionary of values required to get api token
data = {
    'grant_type': 'client_credentials',
    'client_id': 'a04440db440140c7a7e80777f80dbd82',
    'client_secret': 'b5c0a5f79cf24af98fad798504fda8bd',
}
#here's the post request
auth_response = requests.post(auth_url, data=data)

#and here's the json request from spotify:
access_token = auth_response.json().get('access_token')

#here's the base URL for the spotify API:
base_url = 'https://api.spotify.com/v1/'

#next include our access token as a header 
headers = {
    'Authorization': 'Bearer {}'.format(access_token)
}

#now we can access spotify data.





        """ beautiful spotify attempt
       #using the requests module, we can return the contents of the desired url
        result = requests.get(album_url)
        doc = BeautifulSoup(result.text, "html.parser")
        #then we extract the artwork for the album

        artwork = doc.find([img], text="album cover")        
        print(artwork)
        print("hey")
        #title = doc.find("h1", {"class": "Type__TypeElement-goli3j-0 bcTfIx gj6rSoF7K4FohS2DJDEm"}) 
        #artist = doc.find("div", {"class": "RANLXG3qKB61Bh33I0r2 NO_VO3MRVl9z3z56d8Lg"} ) 
        #print(artwork)
        #print(title.string)
        #print(artist)


        """ spotify attempt
        #using bs, we can extract the html page from that
        doc = BeautifulSoup(result.text, "html.parser")
        #then we extract the artwork for the album
        artwork = doc.find("img", {"class": "mMx2LUixlnN_Fu45JpFB"} )        
        artwork = artwork["src"]
        #get the artist name and title from the url:
        title = doc.find("h1", {"class": "Type__TypeElement-goli3j-0 bcTfIx gj6rSoF7K4FohS2DJDEm"}) 
        artist = doc.find("div", {"class": "RANLXG3qKB61Bh33I0r2 NO_VO3MRVl9z3z56d8Lg"} ) 
        print(title.string)
        print(artist)
      
        print(doc.find("a", {"href": "artist"}))
        """