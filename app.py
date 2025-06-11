from flask import Flask, render_template, request, redirect, url_for
import datetime
import requests

app = Flask(__name__)

# Temporary in-memory store
inventory = []

# Estimate expiration (simplified by category)
EXPIRY_DAYS = {
    'tomato': 7,
    'spinach': 7,
    'chicken': 3,
    'milk': 5,
    'eggs': 14,
    'potatoes': 9,
    'cheese': 10,
    'rice': 180,
    'onion': 30,
    'garlic': 60,
    'broccoli': 6,
    'carrot': 10
}


API_KEY = '6f1d20be74784bb7b3e5bd73ef4fb218'  # Replace with your actual key


def calculate_expiry(purchase_date_str, ingredient):
    purchase_date = datetime.datetime.strptime(purchase_date_str, '%Y-%m-%d').date()
    days = EXPIRY_DAYS.get(ingredient.lower(), 7)
    expiry_date = purchase_date + datetime.timedelta(days=days)
    today = datetime.date.today()

    if expiry_date < today:
        status = 'expired'
    elif (expiry_date - today).days <= 2:
        status = 'warning'
    else:
        status = 'fresh'
    return expiry_date.isoformat(), status


@app.route('/')
def index():
    ingredients = list(EXPIRY_DAYS.keys())  # ['tomato', 'spinach', 'chicken', ...]
    return render_template('index.html', ingredients=ingredients)



@app.route('/add', methods=['POST'])
def add_ingredient():
    ingredient_list = request.form.getlist('ingredients')
    date = request.form['date']
    for ingredient in ingredient_list:
        expiry, status = calculate_expiry(date, ingredient)
        inventory.append({
            'name': ingredient,
            'date': date,
            'expiry': expiry,
            'status': status
        })
    return redirect(url_for('show_inventory'))



@app.route('/inventory')
def show_inventory():
    return render_template('inventory.html', inventory=inventory)


@app.route('/recipes', methods=['POST'])
def get_recipes():
    selected = request.form.getlist('selected')
    query = ','.join(selected)
    url = f"https://api.spoonacular.com/recipes/findByIngredients?ingredients={query}&number=3&apiKey={API_KEY}"
    response = requests.get(url)
    recipes = response.json()
    return render_template('recipes.html', recipes=recipes)


if __name__ == '__main__':
    app.run(debug=True)
