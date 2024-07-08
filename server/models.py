from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

#A Restaurant has many Pizzas through RestaurantPizza
#A Pizza has many Restaurants through RestaurantPizza
#A RestaurantPizza belongs to a Restaurant and belongs to a Pizza

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
    price = db.Column(db.Integer, nullable=False)
    
    restaurant = db.relationship('Restaurant', backref=db.backref('restaurant_pizzas', cascade='all, delete-orphan'))
    pizza = db.relationship('Pizza', backref=db.backref('restaurant_pizzas', cascade='all, delete-orphan'))
    
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
