from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

class Restaurant(db.Model):
    __tablename__ = 'restaurants'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    address = db.Column(db.String)
        
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'address': self.address,
            'restaurant_pizzas': [pizza.to_dict() for pizza in self.restaurant_pizzas]
        }
    
    def __repr__(self):
        return f'<Restaurant {self.name}>'

class Pizza(db.Model):
    __tablename__ = 'pizzas'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    ingredients = db.Column(db.String)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'ingredients': self.ingredients,
        }
    
    def __repr__(self):
        return f'<Pizza {self.name}>'

class RestaurantPizza(db.Model):
    __tablename__ = 'restaurant_pizzas'
    
    id = db.Column(db.Integer, primary_key=True)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'))
    pizza_id = db.Column(db.Integer, db.ForeignKey('pizzas.id'))
    _price = db.Column('price', db.Integer, nullable=False)
    
    restaurant = db.relationship('Restaurant', backref=db.backref('restaurant_pizzas', cascade='all, delete-orphan'))
    pizza = db.relationship('Pizza', backref=db.backref('restaurant_pizzas', cascade='all, delete-orphan'))
    
    def __init__(self, restaurant_id, pizza_id, price):
        self.restaurant_id = restaurant_id
        self.pizza_id = pizza_id
        self.price = price  # Use the property setter for validation

    @property
    def price(self):
        return self._price
    
    @price.setter
    def price(self, value):
        self.validate_price_range(value)
        self._price = value
    
    @staticmethod
    def validate_price_range(price):
        if not (1 <= price <= 30):
            raise ValueError("Price must be between 1 and 30")

    def to_dict(self):
        return {
            'id': self.id,
            'price': self.price,
            'restaurant': {
                'id': self.restaurant.id,
                'name': self.restaurant.name,
                'address': self.restaurant.address
            },
            'pizza': {
                'id': self.pizza.id,
                'name': self.pizza.name,
                'ingredients': self.pizza.ingredients
            }
        }
    
    def __repr__(self):
        return f'<RestaurantPizza {self.restaurant.name} - {self.pizza.name} (${self.price})>'

# SQLAlchemy event listener to validate price range before insert and update
@event.listens_for(RestaurantPizza, 'before_insert')
@event.listens_for(RestaurantPizza, 'before_update')
def validate_price_range(mapper, connection, target):
    if not (1 <= target.price <= 30):
        raise IntegrityError("Price must be between 1 and 30")

# Routes
@app.route('/restaurants/<int:restaurant_id>/pizzas/<int:pizza_id>/restaurant_pizzas', methods=['POST'])
def create_restaurant_pizza(restaurant_id, pizza_id):
    data = request.get_json()
    price = data.get('price')

    if not price:
        return jsonify({'error': 'Price is required'}), 400

    try:
        restaurant_pizza = RestaurantPizza(restaurant_id=restaurant_id, pizza_id=pizza_id, price=price)
        db.session.add(restaurant_pizza)
        db.session.commit()
        return jsonify(restaurant_pizza.to_dict()), 201
    except ValueError as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)
