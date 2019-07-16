from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Campground, SiteReview, Base, User

app = Flask(__name__)

#Imports to create anti-forgery session tokens
from flask import session as login_session
import random, string

#New Imports for This Step --- GConnect
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

engine = create_engine('sqlite:///campreviewwithusers.db', connect_args={'check_same_thread': False})
Base.metadata.bind = engine

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Campground App"

#Database connection and creation of database session
DBSession = sessionmaker(bind=engine)
session = DBSession()

#Making an API Endpoint (Get Request) to view Campground information
@app.route('/campground/<int:campground_id>/review/JSON')
def campgroundSiteReviewJSON(campground_id):
     campground = session.query(Campground).filter_by(id=campground_id).one()
     items = session.query(SiteReview).filter_by(campground_id=campground_id).all()
     return jsonify(SiteReviews=[i.serialize for i in items])

@app.route('/campground/<int:campground_id>/review/<int:site_id>/JSON')
def siteReviewJSON(campground_id, site_id):
    Site_Review = session.query(SiteReview).filter_by(id=site_id).one()
    return jsonify(Site_Review=Site_Review.serialize)  

@app.route('/campground/JSON')
def campgroundsJSON():
    campgrounds = session.query(Campground).all()
    return jsonify(campgrounds=[c.serialize for c in campgrounds])    



# User Helper Functions

def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
    'email'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id

def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user

def getUserId(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None     

#Login route
#Anit=forgery session token
#Create state to store login session 
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)for x in range(32))
    login_session['state'] = state
    #return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)

@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

   
# See if a user exists, if it doesn't make a new one
    user_id = getUserId(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("Welcome Back %s" % login_session['username'])
    print "done!"
    return output
  




@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        #return response
        flash("You are now logged out.  Thanks for stopping by")
        return redirect(url_for('showCampgrounds'))
    else:
        response = make_response(json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response

#Show All Campgrounds
@app.route('/')
@app.route('/campground/')
def showCampgrounds():
    campgrounds = session.query(Campground).all()
    if 'username' not in login_session:
        return render_template('publiccampgrounds.html', campgrounds=campgrounds)
    else:
        return render_template('campgrounds.html', campgrounds=campgrounds)
   
#Create A New Campground
@app.route('/campground/new/',methods=['GET', 'POST'])
def createCampground():
       if 'username' not in login_session:
           return redirect('/login')         
       if request.method == 'POST':
              createCampground = Campground(name=request.form['name'], user_id = login_session['user_id'])
              session.add(createCampground)
              flash('You have just added  %s ' % createCampground.name)
              session.commit()
              return redirect(url_for('showCampgrounds'))
       else:
              return  render_template('newCampground.html')

#Edit A Campground
@app.route('/campground/<int:campground_id>/edit/', methods=['GET', 'POST'])
def editCampground(campground_id):
    editedCampground = session.query(
        Campground).filter_by(id=campground_id).one()
    if 'username' not in login_session:
           return redirect('/login') 
    if  editedCampground.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized to edit this campground. Please create your own campground in order to edit.');}</script><body onload='myFunction()'>"   
    if request.method == 'POST':
        if request.form['name']:
            editedCampground.name = request.form['name']
            session.add(editedCampground)
            flash('You just edited a campground')
            session.commit()
            return redirect(url_for('showCampgrounds'))
    else:
        return render_template(
            'editCampground.html', campground=editedCampground)

#Delete A Campground
@app.route('/campground/<int:campground_id>/delete/', methods=['GET', 'POST'])
def deleteCampground(campground_id):
       campgroundToBeDeleted = session.query(Campground).filter_by(id=campground_id).one()
       if 'username' not in login_session:
           return redirect('/login')  
       if campgroundToBeDeleted.user_id != login_session['user_id']:
            return "<script>function myFunction() {alert('You are not authorized to delete this campground. Please create your own campground in order to edit.');}</script><body onload='myFunction()'>"  
       if request.method == 'POST':
              session.delete(campgroundToBeDeleted)
              flash('You just deleted a campground')
              session.commit()
              return redirect(url_for('showCampgrounds', campground_id=campground_id))
       else:
              return render_template('deleteCampground.html', campground=campgroundToBeDeleted)              

             
#Show A Site Review
@app.route('/campground/<int:campground_id>/')
@app.route('/campground/<int:campground_id>/review/')
def showSiteReview(campground_id):
       campground = session.query(Campground).filter_by(id=campground_id).one()
       creator =  getUserInfo(campground.user_id)
       items = session.query(SiteReview).filter_by(campground_id=campground_id).all()
       if 'username' not in login_session or creator.id != login_session['user_id']:
            return render_template('publicsitereview.html', items=items, campground=campground, creator=creator)
       else: 
           return render_template('siteReview.html', campground=campground, items=items)

#Create A Site Review
@app.route('/campground/<int:campground_id>/review/new-review/', methods=['GET', 'POST'])
def newSiteReview(campground_id):
       if 'username' not in login_session:
               return redirect('/login')
       campground = session.query(Campground).filter_by(id=campground_id).one()
      #if login_session['user_id'] != campground.user_id:
          # return "<script>function myFunction() {alert('You are not authorized to create campground review. Please create your own campground in order to edit a review.');}</script><body onload='myFunction()'>" 

       if request.method == 'POST':
              newSiteReview = SiteReview(experience=request.form['experience'], description=request.form['description'], 
              category=request.form['category'], campground_id=campground_id, user_id = campground.user_id)
              session.add(newSiteReview)
              flash('You just wrote a review')
              session.commit()
              return redirect(url_for('showSiteReview', campground_id=campground_id))
       else:
              return render_template('newSiteReview.html', campground_id=campground_id)


#Edit A Site Review
@app.route('/campground/<int:campground_id>/review/<int:site_id>/edit/', methods=['GET', 'POST'])
def editSiteReview(campground_id, site_id):
    if 'username' not in login_session:
        return redirect('/login')
    editedSiteReview = session.query(SiteReview).filter_by(id=site_id).one()           
    campground = session.query(Campground).filter_by(id=campground_id).one()
    if campground.user_id != login_session['user_id']:
            return "<script>function myFunction() {alert('You are not authorized to edit this campground review. Please create your own campground in order to edit a review.');}</script><body onload='myFunction()'>" 
    if request.method =='POST':
              if request.form['experience']:
                     editedSiteReview.experience = request.form['experience']
              if request.form['description']:
                     editedSiteReview.description = request.form['description']   
              if request.form['category']:
                     editedSiteReview.category = request.form['category'] 
              session.add(editedSiteReview)
              flash('You just edited a review')
              session.commit()
              return redirect(url_for('showSiteReview', campground_id=campground_id))    
    else:
              return render_template('editSiteReview.html', campground_id=campground_id, site_id=site_id, item=editedSiteReview)  

#Delete A Site Review 
@app.route('/campground/<int:campground_id>/review/<int:site_id>/delete/', methods=['GET', 'POST'])
def deleteSiteReview(campground_id, site_id):
    if 'username' not in login_session:
               return redirect('/login')
    campground = session.query(Campground).filter_by(id=campground_id).one()          
    siteReviewToBeDeleted = session.query(SiteReview).filter_by(id=site_id).one()
    if campground.user_id != login_session['user_id']:
            return "<script>function myFunction() {alert('You are not authorized to delete this campground review. Please create your own campground in order to delete a review.');}</script><body onload='myFunction()'>" 
    if request.method == 'POST':
              session.delete(siteReviewToBeDeleted)
              flash('You just deleted a review')
              session.commit()
              return redirect(url_for('showSiteReview', campground_id=campground_id))
    else:
              return render_template('deleteSiteReview.html', item=siteReviewToBeDeleted)       
            
   
if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.run(host='0.0.0.0', port=5000)    