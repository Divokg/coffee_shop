import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this function will add one
'''
db_drop_and_create_all()

# ROUTES


# GET DRINKS

@app.route('/drinks')
def get_drinks():
    
    try:
        drinks = Drink.query.all()
        drinks_short = [drink.short() for drink in drinks]
        
        if len(drinks_short) == 0:
            abort(404)
        
        return {
            'success': True,
            'drinks': drinks_short
        }, 200
    except:
        abort(422)
    

# GET DRINKS-DETAIL

@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_details(payload):
    
    try:
        drinks = Drink.query.all()
        drinks_long = [drink.long() for drink in drinks]
        
        if len(drinks_long) == 0:
            abort(404)
            
        return {
            'success': True,
            'drinks': drinks_long,
            
        }, 200
    except:
        abort(422)
        
# POST ENDPOINT

@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')  
def create_new_drink(payload):
    
    form = request.get_json()
    new_title = form.get('title',None)
    new_recipe = json.dumps(form.get("recipe",None))
    array_recipe = new_recipe
    
    
    
    
    try:
        print("1")
        new_drink = Drink(
        title=new_title,
        recipe = array_recipe
        )
        print('2')
        new_drink.insert()
       
        print("3")      
        all_drinks = Drink.query.all()
        print("4")
        formatted_drinks = [drink.long() for drink in all_drinks]
        print("5")
        if len(formatted_drinks) == 0:
            abort(404)
        print("6")    
        return {
            'success': True,
            'drinks': formatted_drinks,
        }, 200  
    except:
        abort(422)      

# PATCH ENDPOINT

@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(payload,id):
    
    form = request.get_json()
    updated_title = form.get('title')
    
    try:
        drink_to_update = Drink.query.filter(Drink.id == id).one_or_none()
        if drink_to_update is None:
            abort(404)
        drink_to_update.title = updated_title
       
        
        drink_to_update.update()
        drink_long = [drink_to_update.long()]
        
        if len(drink_long) == 0:
            abort(404)
        
        return{
            'success': True,
            'drinks': drink_long
            
        }, 200
    except:
        abort(422)

# DELETE ENDPOINT

@app.route('/drinks/<int:id>', methods = ['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload,id):
    try:
        drink_to_delete=Drink.query.get_or_404(id)
        drink_to_delete.delete()
        
        return{
            'success': True,
            'delete':id
        },200
    except:
        abort(422)    
    


# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422

@app.errorhandler(404)
def not_found(error):
    return {
      "success": False,
      "error": 404,
      "message": "resource not found"   
    }, 404
  
@app.errorhandler(400)
def bad_request(error):
    return {
      "success": False,
      "error": 400,
      "message": "bad request"   
    }, 400
    
@app.errorhandler(405)
def method_not_allowed(error):
    return {
      "success": False,
      "error": 405,
      "message": "method not allowed"   
    }, 405
    
@app.errorhandler(500)
def server_error(error):
    return {
      "success": False,
      "error": 500,
      "message": "server error"   
    }, 500

@app.errorhandler(403)
def server_error(error):
    return {
      "success": False,
      "error": 403,
      "message": "You don't have the permission to access the requested resource."  
    
    }, 403
    
if __name__ == "__main__":
    app.debug = True
    app.run()
