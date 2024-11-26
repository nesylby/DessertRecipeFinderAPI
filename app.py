from flask import Flask, jsonify, request
from flask_restx import Api, Resource, fields, reqparse
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
from pymongo import MongoClient
from datetime import timedelta
import yaml

# Initialize Flask app
app = Flask(__name__)

# MongoDB connection setup
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

# Define request model (for post/put requests)
recipe_model = api.model('Recipe', {
    'name': fields.String(required=True, description='The name of the recipe'),
    'category': fields.String(description='The category of the recipe'),
    'origin': fields.String(description='The country of origin'),
    'type': fields.String(description='Type of dessert'),
    'ingredients': fields.List(fields.String, description='Ingredients used in the recipe'),
    'calories': fields.Integer(description='Calories per serving'),
    'difficulty': fields.String(description='Difficulty of the recipe'),
    'Vegan': fields.String(description='Is the recipe vegan?'),
    'author': fields.String(description='Author of the recipe'),
})

# ------------------------------ Recipe Endpoints ------------------------------

@api.route('/Recipes')
class RecipeList(Resource):
    def get(self):
        """Retrieve recipes with filters"""
        filters = {}

        # Define query parameters for filtering recipes
        parser = reqparse.RequestParser()
        parser.add_argument('category', type=str, help='Category of the recipe')
        parser.add_argument('origin', type=str, help='Origin of the recipe')
        parser.add_argument('type', type=str, help='Type of the recipe')
        parser.add_argument('serve_size', type=int, help='Serving size')
        parser.add_argument('main_ingredient', type=str, help='Main ingredient')
        parser.add_argument('allergen', type=str, help='Allergen information')
        parser.add_argument('dietary_benefits', type=str, help='Dietary benefits')
        parser.add_argument('calories', type=int, help='Maximum calories')
        parser.add_argument('difficulty', type=str, help='Difficulty of the recipe')
        parser.add_argument('Vegan', type=str, help='Vegan option (YES/NO)')
        parser.add_argument('Author', type=str, help='Author of the recipe')

        args = parser.parse_args()

        if args['category']:
            filters['category'] = args['category']
        if args['origin']:
            filters['origin'] = args['origin']
        if args['type']:
            filters['type'] = args['type']
        if args['serve_size']:
            filters['serve_size'] = args['serve_size']
        if args['main_ingredient']:
            filters['main_ingredient'] = args['main_ingredient']
        if args['allergen']:
            filters['allergen'] = args['allergen']
        if args['dietary_benefits']:
            filters['dietary_benefits'] = args['dietary_benefits']
        if args['calories']:
            filters['calories'] = {'$lte': args['calories']}
        if args['difficulty']:
            filters['difficulty'] = args['difficulty']
        if args['Vegan']:
            filters['Vegan'] = args['Vegan']
        if args['Author']:
            filters['Author'] = args['Author']

        recipes = list(recipes_collection.find(filters))
        for recipe in recipes:
            recipe['_id'] = str(recipe['_id'])  # Convert ObjectId to string for JSON response

        return jsonify(recipes)

    @api.expect(recipe_model)  # Expect data matching the 'Recipe' model for POST
    def post(self):
        """
        Add a new recipe with all related data.
        Expects a JSON body containing the entire model.
        """
        data = request.get_json()

        # Validate main recipe fields
        if 'Recipe' not in data or not isinstance(data['Recipe'], list) or not data['Recipe']:
            return jsonify({"error": "Recipe section is missing or invalid"}), 400

        recipe = data['Recipe'][0]
        required_fields = [
            "recipeID", "name", "description", "origin", "type", 
            "servings", "prep_time", "cook_time", "difficulty", 
            "majorIngredient", "instructions"
        ]
        missing_fields = [field for field in required_fields if field not in recipe]
        if missing_fields:
            return jsonify({
                "error": "Missing required fields in Recipe",
                "missing_fields": missing_fields
            }), 400

        # Insert Recipe
        if recipes_collection.find_one({"recipeID": recipe["recipeID"]}):
            return jsonify({"error": "Recipe with this recipeID already exists"}), 409
        recipes_collection.insert_one(recipe)

        # Insert related data
        for section_name, collection in [
            ("Ingredients", ingredients_collection),
            ("NutritionInfo", nutritioninfo_collection),
            ("DietaryBenefits", dietarybenefits_collection),
            ("Picture", picture_collection),
            ("Video", video_collection),
            ("Author", author_collection)
        ]:
            if section_name in data:
                section_data = data[section_name]
                if isinstance(section_data, list):
                    for item in section_data:
                        # Ensure all items include the `recipeID`
                        if "recipeID" not in item:
                            return jsonify({
                                "error": f"Each entry in {section_name} must include a recipeID"
                            }), 400
                        collection.insert_one(item)

        return jsonify({"message": "Recipe and related data added successfully"}), 201
    
# ------------------------------ User Authentication Endpoints ------------------------------

@api.route('/users/login')
class UserLogin(Resource):
 def post(self):
        """
        Add a new recipe with all related data.
        Expects a JSON body containing the entire model.
        """
        data = request.get_json()

        # Validate main recipe fields
        if 'Recipe' not in data or not isinstance(data['Recipe'], list) or not data['Recipe']:
            return jsonify({"error": "Recipe section is missing or invalid"}), 400

        recipe = data['Recipe'][0]
        required_fields = [
            "recipeID", "name", "description", "origin", "type", 
            "servings", "prep_time", "cook_time", "difficulty", 
            "majorIngredient", "instructions"
        ]
        missing_fields = [field for field in required_fields if field not in recipe]
        if missing_fields:
            return jsonify({
                "error": "Missing required fields in Recipe",
                "missing_fields": missing_fields
            }), 400

        # Insert Recipe
        if recipes_collection.find_one({"recipeID": recipe["recipeID"]}):
            return jsonify({"error": "Recipe with this recipeID already exists"}), 409
        recipes_collection.insert_one(recipe)

        # Insert related data
        for section_name, collection in [
            ("Ingredients", ingredients_collection),
            ("NutritionInfo", nutritioninfo_collection),
            ("DietaryBenefits", dietarybenefits_collection),
            ("Picture", picture_collection),
            ("Video", video_collection),
            ("Author", author_collection)
        ]:
            if section_name in data:
                section_data = data[section_name]
                if isinstance(section_data, list):
                    for item in section_data:
                        # Ensure all items include the `recipeID`
                        if "recipeID" not in item:
                            return jsonify({
                                "error": f"Each entry in {section_name} must include a recipeID"
                            }), 400
                        collection.insert_one(item)

        return jsonify({"message": "Recipe and related data added successfully"}), 201

# ------------------------------ Recipe Specific Endpoints ------------------------------

@api.route('/Recipes/<string:name>')
class RecipeDetail(Resource):
    def get(self, recipeID):
        """
        Retrieve a detailed recipe response with associated data.
        """
        # Fetch main recipe details
        recipe = recipes_collection.find_one({"recipeID": recipeID}, {"_id": 0})
        if not recipe:
            return jsonify({"error": "Recipe not found"}), 404

        # Fetch related data from other collections
        ingredients = list(ingredients_collection.find({"recipeID": recipeID}, {"_id": 0}))
        nutrition_info = list(nutritioninfo_collection.find({"recipeID": recipeID}, {"_id": 0}))
        dietary_benefits = list(dietarybenefits_collection.find({"recipeID": recipeID}, {"_id": 0}))
        pictures = list(picture_collection.find({"recipeID": recipeID}, {"_id": 0}))
        videos = list(video_collection.find({"recipeID": recipeID}, {"_id": 0}))
        author = list(author_collection.find({"recipeID": recipeID}, {"_id": 0}))

        # Combine all data into a single response model
        response = {
            "Recipe": [recipe],
            "Ingredients": ingredients,
            "NutritionInfo": nutrition_info,
            "DietaryBenefits": dietary_benefits,
            "Picture": pictures,
            "Video": videos,
            "Author": author
        }

        return jsonify(response)

    @jwt_required()  # Protect this endpoint by requiring a valid JWT token
    @api.expect(recipe_model)  # Expect data matching the 'Recipe' model for PUT
    def put(self, name):
        """Update a recipe by name"""
        data = request.get_json()
        result = recipes_collection.update_one({"name": name}, {"$set": data})
        if result.modified_count > 0:
            return jsonify({"message": "Recipe updated successfully"})
        return jsonify({"error": "Recipe not found"}), 404

    @jwt_required()  # Protect this endpoint by requiring a valid JWT token
    def delete(self, name):
        """Delete a specific recipe by name"""
        result = recipes_collection.delete_one({"name": name})
        if result.deleted_count > 0:
            return jsonify({"message": "Recipe deleted successfully"})
        return jsonify({"error": "Recipe not found"}), 404

# ------------------------------ Main Section ------------------------------

if __name__ == '__main__':
    app.run(debug=True)
