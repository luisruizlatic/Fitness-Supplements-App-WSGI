#!/usr/bin/env python3
# Author: Luis Ruiz
# Project: Fitness Supplements App                                                                                                                                                                                                                                                                   # Date: 08/27/2019
# Description: Fitness Supplements Catalog
from flask import Flask, render_template, make_response
from flask import request, redirect, jsonify, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from database_setup import Base, Supplement, Product, User
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests
import os

# ========FLASK INSTANCE========
app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///FitnessSupplements.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://luisr:999999@localhost/fitnesssupplements'
app.config['SECRET_KEY'] = 'k377AglooNex+932.asdjReajeIxane436'
# ========Database Connection========
db = SQLAlchemy(app)


# ========================= Login Section ================================
PROJECT_ROOT = os.path.realpath(os.path.dirname(__file__))
google_json_url = os.path.join(PROJECT_ROOT, 'client_secrets.json')
CLIENT_ID = json.loads(
    open(google_json_url).read())['web']['client_id']
'''CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']'''
APPLICATION_NAME = "Fitness Supplements Application"


# ========================= Access Login Web Page ========================
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


# ========================= Access Through Facebook =======================
@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data.decode()
    print("access token received %s " % access_token)

    app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = ('https://graph.facebook.com/oauth/access_token?grant_type=fb'
           '_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s'
           % (app_id, app_secret, access_token))
    h = httplib2.Http()
    result = (h.request(url, 'GET')[1]).decode()
    print('RESULT IS:  '+result)
    token = result.split(',')[0].split(':')[1].replace('"', '')
    print('TOKEN IS:  '+token)
    url = ('https://graph.facebook.com/v2.8/me?access_token'
           '=%s&fields=name,id,email' % token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result.decode())
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]
    # The token must be stored in the login_session in order to properly logout
    login_session['access_token'] = token
    # Get user picture
    url = ('https://graph.facebook.com/v2.8/me/picture?access_token='
           '%s&redirect=0&height=200&width=200' % token)
    h = httplib2.Http()
    result = (h.request(url, 'GET')[1]).decode()
    data = json.loads(result)
    login_session['picture'] = data["data"]["url"]
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id
    output = ''
    output += '<h4>Welcome, '
    output += login_session['username']
    output += '!</h4>'
    output += '<img src="'
    output += login_session['picture']
    output += (' " style = "width: 100px; height: 100px;border-radius: 150px;'
               '-webkit-border-radius: 150px;-moz-border-radius: 150px;"> ')
    flash("Now logged in as %s" % login_session['username'])
    return output


# ========================= Access Through Google =======================
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
    # result = json.loads(h.request(url, 'GET')[1])
    result = json.loads((h.request(url, 'GET')[1]).decode())
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
        print("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps(
                                 'Current user is already connected.'),
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
    login_session['provider'] = 'google'
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # see if user exisists, if it doesn't ma a newone
    user_id = getUserID(login_session['email'])
    if user_id is None:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h4>Welcome, '
    output += login_session['username']
    output += '!</h4>'
    output += '<img src="'
    output += login_session['picture']
    output += (' " style = "width: 100px; height: 100px;border-radius: 150px;'
               '-webkit-border-radius: 150px;-moz-border-radius: 150px;"> ')
    flash("you are now logged in as %s" % login_session['username'])
    return output


# ====================== Logout from Facebook & Google ====================
@app.route('/logout')
def logout():
    if 'user_id' not in login_session:
        return redirect('/login')
    if login_session['provider'] == 'facebook':
        facebook_id = login_session['facebook_id']
        access_token = login_session['access_token']
        url = ('https://graph.facebook.com/%s/permissions?'
               'access_token=%s' % (facebook_id, access_token))
        h = httplib2.Http()
        result = h.request(url, 'DELETE')[1]
        del login_session['access_token']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        del login_session['facebook_id']
        flash('You have logged out succesfully')
        return redirect(url_for('allSupplements'))
    elif login_session['provider'] == 'google':
        access_token = login_session.get('access_token')
        if access_token is None:
            print('Access Token is None')
            response = make_response(json.dumps(
                                     'Current user not connected.'),
                                     401)
            response.headers['Content-Type'] = 'application/json'
            return response
        print('In gdisconnect access token is %s', access_token)
        print('User name is: ')
        print(login_session['username'])
        url = ('https://accounts.google.com/o/oauth2/'
               'revoke?token=%s' % login_session['access_token'])
        h = httplib2.Http()
        result = h.request(url, 'GET')[0]
        print('result is ')
        print(result)
        if result['status'] == '200':
            del login_session['access_token']
            del login_session['gplus_id']
            del login_session['username']
            del login_session['email']
            del login_session['picture']
            del login_session['user_id']
            del login_session['provider']
            flash('You have logged out succesfully')
            return redirect(url_for('allSupplements'))
        else:
            response = make_response(json.dumps(
                                     'Failed to revoke token for given user.'),
                                     400)
            response.headers['Content-Type'] = 'application/json'
            return response


# ===================== Third Party Information DB Connection ===============
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    db.session.add(newUser)
    db.session.commit()
    user = db.session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = db.session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = db.session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None
# ========================= End Login Section ===================


# ========================= CRUD ================================
@app.route('/')
def allSupplements():
    allSupplements = db.session.query(
        Supplement).order_by(Supplement.name.desc()).all()
    lastProducts = db.session.query(Product).order_by(
        Product.id.desc()).limit(10).all()
    if 'user_id' not in login_session:
        loggedUserId = 0
    else:
        loggedUserId = login_session['user_id']
    return render_template('mainPage.html',
                           supplements=allSupplements,
                           products=lastProducts,
                           user_id=loggedUserId)


@app.route('/supplements/<int:supplement_id>/products/all')
def supplementProducts(supplement_id):
    allSupplements = db.session.query(
        Supplement).order_by(Supplement.name.desc()).all()
    supplement = db.session.query(Supplement).filter_by(id=supplement_id).one()
    supplementProducts = db.session.query(
        Product).filter_by(supplement_id=supplement.id)
    if 'user_id' not in login_session:
        loggedUserId = 0
    else:
        loggedUserId = login_session['user_id']
    return render_template('supplementProducts.html',
                           supplements=allSupplements,
                           products=supplementProducts,
                           selectedSupplement=supplement,
                           user_id=loggedUserId)


@app.route('/supplements/<int:supplement_id>/products/<int:product_id>/')
def productInformation(supplement_id, product_id):
    selectedProduct = db.session.query(
            Product).filter_by(id=product_id).one()
    if 'user_id' not in login_session:
        loggedUserId = 0
    else:
        loggedUserId = login_session['user_id']
    return render_template('productInformation.html',
                           product=selectedProduct,
                           user_id=loggedUserId)


@app.route('/supplements/<int:supplement_id>/products/new/',
           methods=['GET', 'POST'])
def newProduct(supplement_id):
    if 'user_id' not in login_session:
        return redirect('/login')
    else:
        user_id = login_session['user_id']
    if request.method == 'POST':
        if 'youtube' not in request.form['videoURL']:
            videoURL = None
        else:
            videoURL = request.form['videoURL']
            if 'embed' not in videoURL:
                videoURL = videoURL.replace("watch?v=", "embed/")
            if ('www' not in videoURL or 'http' not in videoURL or
               '.com' not in videoURL):
                    videoURL = None
        newProduct = Product(
            name=request.form['name'],
            price=request.form['price'],
            manufacturer=request.form['manufacturer'],
            videoURL=videoURL,
            description=request.form['description'],
            supplement_id=supplement_id,
            user_id=user_id,
        )
        db.session.add(newProduct)
        db.session.commit()
        flash('The product %s has bee added', newProduct.name)
        return redirect(url_for('supplementProducts',
                        supplement_id=supplement_id))
    else:
        return render_template('newProduct.html',
                               supplement_id=supplement_id,
                               user_id=user_id)


@app.route('/supplements/new/', methods=['GET', 'POST'])
def newSupplement():
    if 'user_id' not in login_session:
        return redirect('/login')
    else:
        user_id = login_session['user_id']
    if request.method == 'POST':
        newSupplement = Supplement(
            name=request.form['name'],
            user_id=user_id,
        )
        db.session.add(newSupplement)
        db.session.commit()
        flash('The supplement %s has been added', newSupplement.name)
        return redirect(url_for('allSupplements'))
    else:
        return render_template('newSupplement.html', user_id=user_id)


@app.route('/supplements/<int:supplement_id>/edit/', methods=['GET', 'POST'])
def editSupplement(supplement_id):
    if 'user_id' not in login_session:
        return redirect('/login')
    else:
        user_id = login_session['user_id']
    editedSupplement = db.session.query(
        Supplement).filter_by(id=supplement_id).one()
    if request.method == 'POST':
        if user_id == editedSupplement.user_id:
            editedSupplement.name = request.form['name']
            db.session.add(editedSupplement)
            db.session.commit()
            flash("The supplement " + editedSupplement.name +
                  " has been edited")
        else:
            flash("You are not authorized to edit this supplement")
        return redirect(url_for('allSupplements'))
    else:
        return render_template('editSupplement.html',
                               supplement_id=supplement_id,
                               supplement=editedSupplement,
                               user_id=user_id)


@app.route('/supplements/<int:supplement_id>/products/<int:product_id>/edit/',
           methods=['GET', 'POST'])
def editProduct(supplement_id, product_id):
    if 'user_id' not in login_session:
        return redirect('/login')
    else:
        user_id = login_session['user_id']
    editedProduct = db.session.query(Product).filter_by(id=product_id).one()
    if request.method == 'POST':
        if user_id == editedProduct.user_id:
            editedProduct.name = request.form['name']
            editedProduct.price = request.form['price']
            editedProduct.manufacturer = request.form['manufacturer']
            editedProduct.description = request.form['description']
            db.session.add(editedProduct)
            db.session.commit()
            flash("The product " + editedProduct.name + " has been edited")
        else:
            flash("You are not authorized to edit this product")
        return redirect(url_for('supplementProducts',
                        supplement_id=supplement_id))
    else:
        return render_template('editProduct.html',
                               supplement_id=supplement_id,
                               Product_id=product_id,
                               product=editedProduct,
                               user_id=user_id)


@app.route('/supplements/<int:supplement_id>/products/'
           '<int:product_id>/delete/', methods=['GET', 'POST'])
def deleteProduct(supplement_id, product_id):
    if 'user_id' not in login_session:
        return redirect('/login')
    else:
        user_id = login_session['user_id']
    productToDelete = db.session.query(Product).filter_by(id=product_id).one()
    if request.method == 'POST':
        if user_id == productToDelete.user_id:
            db.session.delete(productToDelete)
            db.session.commit()
            flash("The product " + productToDelete.name + " has been deleted")
        return redirect(url_for('supplementProducts',
                                supplement_id=supplement_id))
    else:
        return render_template('deleteProduct.html',
                               supplement_id=supplement_id,
                               product_id=product_id,
                               product=productToDelete,
                               user_id=user_id)
# ========================= END OF CRUD ================================


# ========================= API JSON EndPoints =========================
@app.route("/API/supplement/all/JSON", methods=['GET'])
def allSupplementsJSON():
    if request.method == 'GET':
        return getAllSupplementsJSON()


@app.route("/API/supplement/<int:supplement_id>/JSON", methods=['GET'])
def supplementJSON(supplement_id):
    if request.method == 'GET':
        return getSupplementJSON(supplement_id)


@app.route("/API/supplement/<int:supplement_id>/product/"
           "<int:product_id>/JSON", methods=['GET'])
def productJSON(supplement_id, product_id):
    if request.method == 'GET':
        return getProductJSON(supplement_id, product_id)


@app.route("/API/supplement/<int:supplement_id>/product/all/JSON",
           methods=['GET'])
def allSupplementProductsJSON(supplement_id):
    if request.method == 'GET':
        return getAllSupplementProductsJSON(supplement_id)


def getAllSupplementsJSON():
    allSupplements = db.session.query(
        Supplement).order_by(Supplement.name.desc()).all()
    return jsonify(supplements=[r.serialize for r in allSupplements])


def getProductJSON(supplement_id, product_id):
    supplementProduct = db.session.query(
        Product).filter_by(id=product_id).one()
    return jsonify(product=[supplementProduct.serialize])


def getSupplementJSON(supplement_id):
    supplement = db.session.query(
        Supplement).filter_by(id=supplement_id).one()
    return jsonify(supplement=[supplement.serialize])


def getAllSupplementProductsJSON(supplement_id):
    allSupplementProducts = db.session.query(
        Product).filter_by(supplement_id=supplement_id).all()
    return jsonify(products=[r.serialize for r in allSupplementProducts])
# ========================= EndPoints ================================


if __name__ == '__main__': 
    app.debug = True