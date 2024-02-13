from flask import Flask, render_template, request, url_for

import os

import json

import utils as util

from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView


from models import db
from models.category import Category
from models.recipe import Recipe

# loads default recipe data
from default_data import create_default_data



app = Flask(__name__)


app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'default_secret_key')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///recipes.db'
db.init_app(app)


@app.route('/')
def index():
  title = "Home"
  return render_template("index.html", title=title)



@app.route('/about')
def about():
  title = "About"
  return render_template("about.html", title=title)

@app.route("/recipes")
def recipes():
    all_recipes = Recipe.query.all()
    title = "Recipes"
    context = {
      "title": title,
      "recipes": all_recipes
    }
    return render_template("recipes.html", **context)

@app.route("/recipe/<int:recipe_id>")
def recipe(recipe_id):
    this_recipe = Recipe.query.get(recipe_id)
    title = "Recipe"
    context = {
      "title": "Recipe",
      "recipe": this_recipe
    }
    if this_recipe:
        return render_template('recipe.html', **context)
    else:
        return render_template("404.html",title="404"), 404


@app.route('/users')
def users():
  
  # Read project data from JSON file
  with open('test.json') as json_file:
      user_data = json.load(json_file)
      print(user_data)

  context = {
      "title": "Users",
      "users": user_data
  }
  return render_template("users.html", **context)

@app.route('/user/<int:user_number>')
def show_user(user_number):
    this_user = load_user_data(user_number)
    if this_user:
        title = "User"
        context = {
          "title": title,
          "user":  this_user
        }
        return render_template("user.html", **context)
    else:
        return 'User not found', 404

def load_user_data(user_number):
    # Read project data from JSON file
    with open('test.json') as json_file:
        user_data = json.load(json_file)
        user = next((u for u in user_data if u['id'] == user_number), None)
        return user




@app.route('/register', methods=['GET', 'POST'])
def register():
      title = "Register"
      feedback = None
      if request.method == 'POST':
          feedback = register_data(request.form)

      context = {
          "title": title,
          "feedback": feedback
      }
      return render_template('register.html', **context)


def register_data(form_data):
  feedback = []
  for key, value in form_data.items():
    # checkboxes have [] for special handling
    if key.endswith('[]'):
      # Use getlist to get all values for the checkbox
      checkbox = request.form.getlist(key)
      key = key.replace('_', ' ').replace('[]', '')
      feedback.append(f"{key}: {', '.join(map(str, checkbox))}")
    else:
      # Handle other form elements
      key = key.replace('_', ' ')
      match key: 
        case "First Name" | "Last Name"| "Address"| "City":
          value=value.title()
      feedback.append(f"{key}: {value}")
  return feedback



@app.route('/contact')
def contact():
  title = "Contact"
  return render_template("contact.html", title=title)

@app.route('/gallery')
def gallery():
  title = "Gallery"
  return render_template("gallery.html", title=title)

movie_dict = [
  {"title":"Prisoners", "genre":"Thiller/Suspense", "rating":5},
  {"title":"Green Room", "genre":"Thiller", "rating":4.5},
  {"title":"Scott Pilgrim", "genre":"Action/Comedy", "rating":5}
]


movie_dict = util.movie_stars(movie_dict)

@app.route('/movies')
def movies():

  context = {
    "title": "Movies",
    "movies": movie_dict
  }
  
  return render_template("movies.html",**context)


class RecipeView(ModelView):
  column_searchable_list = ['name', 'author']

admin = Admin(app)
admin.url = '/admin/' #would not work on repl w/o this!
admin.add_view(RecipeView(Recipe, db.session))
admin.add_view(ModelView(Category, db.session))


with app.app_context():
  db.create_all()
  #removes all data and loads defaults:
  create_default_data(db,Recipe,Category)


app.run(host='0.0.0.0', port=81)



