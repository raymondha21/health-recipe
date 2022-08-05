"""Health Recipe"""
from multiprocessing.sharedctypes import Value
import os, requests, string
from typing import List

from flask import Flask, render_template, request, flash, redirect, session, g, abort, jsonify,json
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError

from forms import UserBioForm, UserEditForm, UserRegisterForm, LoginForm
from models import User, Recipe, db, connect_db
from secret import API_KEY

CURR_USER_KEY = "curr_user"

app = Flask(__name__)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'noonewillguessthis')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL', 'postgresql:///health-recipe')

toolbar = DebugToolbarExtension(app)

connect_db(app)

@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])
        

    else:
        g.user = None
        


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


@app.route('/signup', methods=["GET", "POST"])
def signup():
    """Handle user signup.

    Create new user and add to DB. Redirect to home page.

    If form not valid, present form.

    If the there already is a user with that username: flash message
    and re-present form.
    """

    form = UserRegisterForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                image_url=form.image_url.data or User.image_url.default.arg,
            )
            db.session.add(user)
            db.session.commit()

        except IntegrityError:
            flash("Username already taken", 'danger')
            return render_template('users/signup.html', form=form)

        do_login(user)

        return redirect("/")

    else:
        return render_template('users/signup.html', form=form)

@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login."""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                 form.password.data)

        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect("/")

        flash("Invalid credentials.", 'danger')

    return render_template('users/login.html', form=form)

@app.route('/logout')
def logout():
    """Handle logout of user."""

    do_logout()

    return redirect('/login')

@app.route('/bmr',methods=["GET","POST"])
def BMR_homepage():
    """Handle and show calculator"""

    if g.user:
        user = g.user
        form = UserBioForm(obj=user)
        try:
            if form.validate_on_submit():
                user.height = form.height.data
                user.weight = form.weight.data
                user.age = form.age.data
                user.gender = form.gender.data
                user.activity = form.activity.data
                db.session.add(g.user)
                db.session.commit()
                return redirect(f'/users/{user.id}')

            else:
                return render_template('/bmr/bmr_home.html',form=form)

        except ValueError as e:
            flash('Please enter all information','danger')
            return render_template('/bmr/bmr_home.html',form=form)
    else: 
        form = UserBioForm()
        
        return render_template('/bmr/bmr_home.html',form=form)

@app.route('/users/<int:user_id>',methods=["GET"])
def user_profile(user_id):
    """Show user profile"""

    user = User.query.get_or_404(user_id)
    
    ACTIVITY_LEVEL = [(1.2,"Sedentary (little to no exercise + work a desk job)"),
            (1.375,"Lightly Active (light exercise 1-3 days / week)"),
            (1.55,"Moderately Active (moderate exercise 3-5 days / week)"),
            (1.75,"Very Active (heavy exercise 6-7 days / week)"),
            (1.9,"Extremely Active (very heavy exercise, hard labor job, training 2x / day)")]

    for i in ACTIVITY_LEVEL:
        if i[0] == user.activity:
            activity = i[1]
    if user.gender == 'M':
        bmr = round(((10 * user.weight * 0.45359237) + (6.25 * user.height * 2.54) - (5 * user.age) + 5) * user.activity)
    else:
        bmr = round(((10 * user.weight * 0.45359237) + (6.25 * user.height * 2.54) - (5 * user.age) - 161) * user.activity)
    

    if user != g.user:
        flash("Access unauthorized.", "danger")
        return redirect('/')
        
    else: 
        return render_template('users/detail.html', user=user, activity=activity,bmr=bmr)

@app.route('/users/<int:user_id>/edit',methods=["GET","POST"])
def user_edit(user_id):
    """Edit User Info"""

    user = User.query.get_or_404(user_id)
    
    
    if user != g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    else:
        form = UserEditForm(obj=user)
        if form.validate_on_submit():
                user.height = form.height.data
                user.weight = form.weight.data
                user.age = form.age.data
                user.gender = form.gender.data
                user.activity = form.activity.data
                db.session.add(g.user)
                db.session.commit()
                return redirect(f'/users/{user.id}')
        return render_template('users/edit.html',user=user,form=form)
       
    


@app.route('/users/<int:user_id>/delete')
def delete_user(user_id):
    """Delete user profile"""

    user = User.query.get_or_404(user_id)

    if user == g.user:
        do_logout()

        db.session.delete(user)
        db.session.commit()
    
    return redirect('/')

@app.route('/recipes')
def recipes_home():
    """Recipes homepage"""
    if g.user:
        user_fav = [recipe.recipe_id for recipe in g.user.likes]
    else:
        user_fav = None

    return render_template('/recipes/recipe_home.html',user_fav=user_fav)

@app.route('/recipes/<int:recipe_id>')
def show_recipe(recipe_id):
    """Show recipe"""

    recipe = requests.get(f"https://api.spoonacular.com/recipes/{recipe_id}/information",params={'includeNutrition':'true','apiKey':API_KEY}).json()
    nutrients = recipe['nutrition']['nutrients']
    ingredients = recipe['extendedIngredients']
    user_fav = [recipe.recipe_id for recipe in g.user.likes]


    return render_template('/recipes/show_recipe.html',recipe=recipe,nutrients=nutrients,ingredients=ingredients, user_fav=user_fav)

@app.route('/users/favorites',methods=["GET"])
def user_favs():
    """Show user favorites"""

    recipe_ids = ",".join(map(str,[recipe.recipe_id for recipe in g.user.likes]))
    
    recipes = requests.get(f"https://api.spoonacular.com/recipes/informationBulk",params = {'apiKey':API_KEY,'ids':recipe_ids,'includeNutrition':'true'}).json()


    return render_template('/users/favorites.html',recipes=recipes)

@app.route('/users/favorites/add/<int:recipe_id>')
def add_fav(recipe_id):
    """Add recipe to favorites"""

    new_recipe = Recipe(recipe_id=recipe_id,user_id=g.user.id)
    db.session.add(new_recipe)
    db.session.commit()

    return jsonify(message="Recipe added")

@app.route('/users/favorites/delete/<int:recipe_id>',methods=["DELETE"])
def delete_fav(recipe_id):
    """Delete recipe from favorites"""

    recipe = Recipe.query.filter_by(recipe_id=recipe_id,user_id=g.user.id).first()
    db.session.delete(recipe)
    db.session.commit()

    return jsonify(message="deleted")

@app.route('/')
def homepage():
    """Show homepage:

    - anon users: Gives you links to calculate BMR, recipes, and sign up
    - logged in: Let's you see your user profile 
    """

    if g.user:
        return render_template('homepage.html')

    else:
        return render_template('home-anon.html')