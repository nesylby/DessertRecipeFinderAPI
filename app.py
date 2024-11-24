from flask import Flask, jsonify, request
from flask_restx import Api, Resource
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
from pymongo import MongoClient
from datetime import timedelta
import yaml


# Initialize Flask app
app = Flask(__name__)

client = MongoClient("mongodb://localhost:27017/")  
db = client['RecAPI']  
recipes_collection = db['Recipes']
ingredients_collection = db['Ingredients']
dietarybenefits_collection = db['Dietarybenefits']
nutritioninfo_collection = db['Nutritioninfo']
author_collection = db['Author']
users_collection = db['Users']
video_collection = db['Video']
picture_collection = db['Picture']

# JWT Setup
app.config['JWT_SECRET_KEY'] = 'DessertRecipeFinderAPI-KKB-GROUP'  
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)  
jwt = JWTManager(app)

# Flask-RESTX API setup with Swagger
api = Api(app, version='1.0', title='Recipe API', description='API for managing dessert recipes')

# Load OpenAPI (Swagger) specification from YAML file
with open('openAPI.yaml', 'r') as file:
    openapi_spec = yaml.safe_load(file)
api.specs = openapi_spec 


# ------------------------------ Recipe Endpoints ------------------------------

@api.route('/Recipes')
class RecipeList(Resource):
    def get(self):
        """Retrieve recipes with filters"""
        filters = {}
        if 'category' in request.args:
            filters['category'] = request.args['category']
        if 'origin' in request.args:
            filters['origin'] = request.args['origin']
        if 'type' in request.args:
            filters['type'] = request.args['type']
        if 'serve_size' in request.args:
            filters['serve_size'] = int(request.args['serve_size'])
        if 'main_ingredient' in request.args:
            filters['main_ingredient'] = request.args['main_ingredient']
        if 'allergen' in request.args:
            filters['allergen'] = request.args['allergen']
        if 'dietary_benefits' in request.args:
            filters['dietary_benefits'] = request.args['dietary_benefits']
        if 'calories' in request.args:
            filters['calories'] = {'$lte': int(request.args['calories'])}
        if 'difficulty' in request.args:
            filters['difficulty'] = request.args['difficulty']
        if 'Vegan' in request.args:
            filters['Vegan'] = request.args['Vegan']
        if 'Author' in request.args:
            filters['Author'] = request.args['Author']

        recipes = list(recipes_collection.find(filters))
        for recipe in recipes:
            recipe['_id'] = str(recipe['_id'])  
        return jsonify(recipes)

    def post(self):
        """Add a new recipe"""
        data = request.get_json()  
        if not data:
            return jsonify({"error": "Invalid input"}), 400
        
       
        recipe_id = recipes_collection.insert_one(data).inserted_id
        return jsonify({"message": "Recipe created successfully", "id": str(recipe_id)}), 201

if __name__ == '__main__':
    app.run(debug=True)