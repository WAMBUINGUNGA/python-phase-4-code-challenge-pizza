#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response,jsonify
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"


# FETCH ALL RESTAURANTS
@app.route('/restaurants', methods=['GET'])
def get_restaurants():
    restaurants = Restaurant.query.all()
    restaurant_list = [{
        "address": restaurant.address,
        "id": restaurant.id,
        "name": restaurant.name,
        # "pizzas": [pizza.to_dict() for pizza in restaurant.pizzas]
    } for restaurant in restaurants]
    return jsonify(restaurant_list), 200








#FETCH RESTAURANT BY ID




@app.route('/restaurants/<int:id>', methods=['GET', 'DELETE'])
def restaurant_by_id(id):
    restaurant = db.session.get(Restaurant, id)
    if not restaurant:
        return jsonify({"error": "Restaurant not found"}), 404
    
    if request.method == 'GET':
        return jsonify(restaurant.to_dict())
    elif request.method == 'DELETE':
        db.session.delete(restaurant)
        db.session.commit()
        return '', 204




#DELETE RESTAURANT BT ID
# @app.route('/restaurants/<int:id>', methods=['DELETE'])
# def delete_restaurant(id):
#     restaurant = Restaurant.query.get(id)
#     if restaurant is None:
#         return jsonify({"error": "Restaurant not found"}), 404

#     db.session.delete(restaurant)
#     db.session.commit()
#     return jsonify({"success": "restaurant deleted successfully"}), 200






# FETCH ALL PIZZAS
@app.route('/pizzas', methods=['GET'])
def get_pizzas():
    pizzas = Pizza.query.all()
    pizza_list = [{
        "id": pizza.id,
        "ingredients": pizza.ingredients,
        "name": pizza.name,
    } for pizza in pizzas]
    return jsonify(pizza_list), 200






# Route to create a new RestaurantPizza
@app.route('/restaurant_pizzas', methods=['POST'])
def create_restaurant_pizza():
    data = request.json
    try:
        new_restaurant_pizza = RestaurantPizza(
            price=data['price'],
            pizza_id=data['pizza_id'],
            restaurant_id=data['restaurant_id']
        )
        db.session.add(new_restaurant_pizza)
        db.session.commit()
        
        pizza = db.session.get(Pizza, data['pizza_id'])
        restaurant = db.session.get(Restaurant, data['restaurant_id'])
        
        return jsonify({
            "id": new_restaurant_pizza.id,
            "price": new_restaurant_pizza.price,
            "pizza_id": new_restaurant_pizza.pizza_id,
            "restaurant_id": new_restaurant_pizza.restaurant_id,
            "pizza": {
                "id": pizza.id,
                "name": pizza.name,
                "ingredients": pizza.ingredients
            },
            "restaurant": {
                "id": restaurant.id,
                "name": restaurant.name,
                "address": restaurant.address
            }
        }), 201
    except ValueError:
        return jsonify({"errors": ["validation errors"]}), 400
    except Exception as e:
        return jsonify({"errors": [str(e)]}), 400
    
    
if __name__ == "__main__":
    app.run(port=5000, debug=True)