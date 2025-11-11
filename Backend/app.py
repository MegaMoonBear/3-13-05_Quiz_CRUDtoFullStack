#!/usr/bin/env python3
"""
Dog Management API Server
A Flask-based REST API server supporting CRUD operations for dog and diet information.

Endpoints:
- GET /api/dogs - Get all dog records
- GET /api/dogs/<user_id> - Get dog record by user ID
- POST /api/dogs - Create new dog record
- PUT /api/dogs/<user_id> - Update dog record
- DELETE /api/dogs/<user_id> - Delete dog record

- GET /api/diets - Get all diet records
- GET /api/diets/<user_id> - Get diet record by user ID
- POST /api/diets - Create new diet record
- PUT /api/diets/<user_id> - Update diet record
- DELETE /api/diets/<user_id> - Delete diet record

- GET /api/users/<user_id> - Get both dog and diet records for a user
- DELETE /api/users/<user_id> - Delete all records for a user
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
from datetime import datetime
import uuid

app = Flask(__name__)
# Enable CORS for all routes to allow frontend communication
CORS(app)

# Data storage file paths
DATA_DIR = 'data'
DOG_DATA_FILE = os.path.join(DATA_DIR, 'dogs.json')
DIET_DATA_FILE = os.path.join(DATA_DIR, 'diets.json')

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

def load_data(file_path):
    """Load data from JSON file, return empty list if file doesn't exist."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []

def save_data(file_path, data):
    """Save data to JSON file."""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving data to {file_path}: {str(e)}")
        return False

def generate_id():
    """Generate a unique ID."""
    return str(uuid.uuid4())

def get_current_timestamp():
    """Get current timestamp in ISO format."""
    return datetime.now().isoformat()

def validate_dog_data(data):
    """Validate dog data structure."""
    required_fields = ['userId', 'name', 'age', 'breeds', 'weight']
    
    for field in required_fields:
        if field not in data:
            return False, f"Missing required field: {field}"
    
    # Validate data types and ranges
    try:
        age = int(data['age'])
        if age < 0 or age > 30:
            return False, "Age must be between 0 and 30 years"
            
        weight = float(data['weight'])
        if weight < 1 or weight > 200:
            return False, "Weight must be between 1 and 200 lbs"
            
        if not isinstance(data['breeds'], list) or len(data['breeds']) == 0:
            return False, "Breeds must be a non-empty list"
            
        if not data['name'].strip():
            return False, "Dog name cannot be empty"
            
        if not data['userId'].strip():
            return False, "User ID cannot be empty"
            
    except (ValueError, TypeError):
        return False, "Invalid data types for age or weight"
    
    return True, "Valid"

def validate_diet_data(data):
    """Validate diet data structure."""
    required_fields = ['userId', 'foodType', 'brand', 'amount', 'feedingTimes']
    
    for field in required_fields:
        if field not in data:
            return False, f"Missing required field: {field}"
    
    # Validate data types and values
    try:
        feeding_times = int(data['feedingTimes'])
        if feeding_times < 1 or feeding_times > 6:
            return False, "Feeding times must be between 1 and 6 per day"
            
        if data['foodType'] not in ['dry', 'wet', 'both']:
            return False, "Food type must be 'dry', 'wet', or 'both'"
            
        if not data['brand'].strip():
            return False, "Brand cannot be empty"
            
        if not data['amount'].strip():
            return False, "Amount cannot be empty"
            
        if not data['userId'].strip():
            return False, "User ID cannot be empty"
            
    except (ValueError, TypeError):
        return False, "Invalid data type for feeding times"
    
    return True, "Valid"

# ==================== DOG ENDPOINTS ====================

@app.route('/api/dogs', methods=['GET'])
def get_all_dogs():
    """Get all dog records."""
    try:
        dogs = load_data(DOG_DATA_FILE)
        return jsonify({
            'success': True,
            'data': dogs,
            'count': len(dogs)
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/dogs/<user_id>', methods=['GET'])
def get_dog_by_user_id(user_id):
    """Get dog record by user ID."""
    try:
        dogs = load_data(DOG_DATA_FILE)
        dog = next((d for d in dogs if d['userId'] == user_id), None)
        
        if dog:
            return jsonify({
                'success': True,
                'data': dog
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Dog record not found for this user ID'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/dogs', methods=['POST'])
def create_dog():
    """Create a new dog record."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Validate data
        is_valid, message = validate_dog_data(data)
        if not is_valid:
            return jsonify({
                'success': False,
                'error': message
            }), 400
        
        # Load existing dogs
        dogs = load_data(DOG_DATA_FILE)
        
        # Check if user already has a dog record
        existing_dog = next((d for d in dogs if d['userId'] == data['userId']), None)
        if existing_dog:
            return jsonify({
                'success': False,
                'error': 'Dog record already exists for this user ID'
            }), 409
        
        # Create new dog record
        dog_record = {
            'id': generate_id(),
            'userId': data['userId'].strip(),
            'name': data['name'].strip(),
            'age': int(data['age']),
            'breeds': data['breeds'],
            'otherBreeds': data.get('otherBreeds', '').strip(),
            'weight': float(data['weight']),
            'createdAt': get_current_timestamp(),
            'updatedAt': get_current_timestamp()
        }
        
        # Add to list and save
        dogs.append(dog_record)
        if save_data(DOG_DATA_FILE, dogs):
            return jsonify({
                'success': True,
                'data': dog_record,
                'message': 'Dog record created successfully'
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to save dog record'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/dogs/<user_id>', methods=['PUT'])
def update_dog(user_id):
    """Update an existing dog record."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Validate data
        is_valid, message = validate_dog_data(data)
        if not is_valid:
            return jsonify({
                'success': False,
                'error': message
            }), 400
        
        # Load existing dogs
        dogs = load_data(DOG_DATA_FILE)
        
        # Find the dog to update
        dog_index = next((i for i, d in enumerate(dogs) if d['userId'] == user_id), None)
        
        if dog_index is None:
            return jsonify({
                'success': False,
                'error': 'Dog record not found for this user ID'
            }), 404
        
        # Update the record
        existing_dog = dogs[dog_index]
        dogs[dog_index] = {
            'id': existing_dog['id'],
            'userId': data['userId'].strip(),
            'name': data['name'].strip(),
            'age': int(data['age']),
            'breeds': data['breeds'],
            'otherBreeds': data.get('otherBreeds', '').strip(),
            'weight': float(data['weight']),
            'createdAt': existing_dog['createdAt'],
            'updatedAt': get_current_timestamp()
        }
        
        # Save updated data
        if save_data(DOG_DATA_FILE, dogs):
            return jsonify({
                'success': True,
                'data': dogs[dog_index],
                'message': 'Dog record updated successfully'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to update dog record'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/dogs/<user_id>', methods=['DELETE'])
def delete_dog(user_id):
    """Delete a dog record."""
    try:
        dogs = load_data(DOG_DATA_FILE)
        
        # Find and remove the dog
        original_length = len(dogs)
        dogs = [d for d in dogs if d['userId'] != user_id]
        
        if len(dogs) == original_length:
            return jsonify({
                'success': False,
                'error': 'Dog record not found for this user ID'
            }), 404
        
        # Save updated data
        if save_data(DOG_DATA_FILE, dogs):
            return jsonify({
                'success': True,
                'message': 'Dog record deleted successfully'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to delete dog record'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ==================== DIET ENDPOINTS ====================

@app.route('/api/diets', methods=['GET'])
def get_all_diets():
    """Get all diet records."""
    try:
        diets = load_data(DIET_DATA_FILE)
        return jsonify({
            'success': True,
            'data': diets,
            'count': len(diets)
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/diets/<user_id>', methods=['GET'])
def get_diet_by_user_id(user_id):
    """Get diet record by user ID."""
    try:
        diets = load_data(DIET_DATA_FILE)
        diet = next((d for d in diets if d['userId'] == user_id), None)
        
        if diet:
            return jsonify({
                'success': True,
                'data': diet
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Diet record not found for this user ID'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/diets', methods=['POST'])
def create_diet():
    """Create a new diet record."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Validate data
        is_valid, message = validate_diet_data(data)
        if not is_valid:
            return jsonify({
                'success': False,
                'error': message
            }), 400
        
        # Load existing diets
        diets = load_data(DIET_DATA_FILE)
        
        # Check if user already has a diet record
        existing_diet = next((d for d in diets if d['userId'] == data['userId']), None)
        if existing_diet:
            return jsonify({
                'success': False,
                'error': 'Diet record already exists for this user ID'
            }), 409
        
        # Create new diet record
        diet_record = {
            'id': generate_id(),
            'userId': data['userId'].strip(),
            'foodType': data['foodType'],
            'brand': data['brand'].strip(),
            'amount': data['amount'].strip(),
            'feedingTimes': int(data['feedingTimes']),
            'createdAt': get_current_timestamp(),
            'updatedAt': get_current_timestamp()
        }
        
        # Add to list and save
        diets.append(diet_record)
        if save_data(DIET_DATA_FILE, diets):
            return jsonify({
                'success': True,
                'data': diet_record,
                'message': 'Diet record created successfully'
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to save diet record'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/diets/<user_id>', methods=['PUT'])
def update_diet(user_id):
    """Update an existing diet record."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Validate data
        is_valid, message = validate_diet_data(data)
        if not is_valid:
            return jsonify({
                'success': False,
                'error': message
            }), 400
        
        # Load existing diets
        diets = load_data(DIET_DATA_FILE)
        
        # Find the diet to update
        diet_index = next((i for i, d in enumerate(diets) if d['userId'] == user_id), None)
        
        if diet_index is None:
            return jsonify({
                'success': False,
                'error': 'Diet record not found for this user ID'
            }), 404
        
        # Update the record
        existing_diet = diets[diet_index]
        diets[diet_index] = {
            'id': existing_diet['id'],
            'userId': data['userId'].strip(),
            'foodType': data['foodType'],
            'brand': data['brand'].strip(),
            'amount': data['amount'].strip(),
            'feedingTimes': int(data['feedingTimes']),
            'createdAt': existing_diet['createdAt'],
            'updatedAt': get_current_timestamp()
        }
        
        # Save updated data
        if save_data(DIET_DATA_FILE, diets):
            return jsonify({
                'success': True,
                'data': diets[diet_index],
                'message': 'Diet record updated successfully'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to update diet record'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/diets/<user_id>', methods=['DELETE'])
def delete_diet(user_id):
    """Delete a diet record."""
    try:
        diets = load_data(DIET_DATA_FILE)
        
        # Find and remove the diet
        original_length = len(diets)
        diets = [d for d in diets if d['userId'] != user_id]
        
        if len(diets) == original_length:
            return jsonify({
                'success': False,
                'error': 'Diet record not found for this user ID'
            }), 404
        
        # Save updated data
        if save_data(DIET_DATA_FILE, diets):
            return jsonify({
                'success': True,
                'message': 'Diet record deleted successfully'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to delete diet record'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ==================== USER ENDPOINTS ====================

@app.route('/api/users/<user_id>', methods=['GET'])
def get_user_records(user_id):
    """Get both dog and diet records for a specific user."""
    try:
        dogs = load_data(DOG_DATA_FILE)
        diets = load_data(DIET_DATA_FILE)
        
        dog_record = next((d for d in dogs if d['userId'] == user_id), None)
        diet_record = next((d for d in diets if d['userId'] == user_id), None)
        
        if not dog_record and not diet_record:
            return jsonify({
                'success': False,
                'error': 'No records found for this user ID'
            }), 404
        
        return jsonify({
            'success': True,
            'data': {
                'userId': user_id,
                'dogRecord': dog_record,
                'dietRecord': diet_record
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/users/<user_id>', methods=['DELETE'])
def delete_user_records(user_id):
    """Delete all records (dog and diet) for a specific user."""
    try:
        dogs = load_data(DOG_DATA_FILE)
        diets = load_data(DIET_DATA_FILE)
        
        # Count original records
        original_dog_count = len(dogs)
        original_diet_count = len(diets)
        
        # Remove records
        dogs = [d for d in dogs if d['userId'] != user_id]
        diets = [d for d in diets if d['userId'] != user_id]
        
        # Check if any records were deleted
        dog_deleted = len(dogs) < original_dog_count
        diet_deleted = len(diets) < original_diet_count
        
        if not dog_deleted and not diet_deleted:
            return jsonify({
                'success': False,
                'error': 'No records found for this user ID'
            }), 404
        
        # Save updated data
        dog_save_success = save_data(DOG_DATA_FILE, dogs)
        diet_save_success = save_data(DIET_DATA_FILE, diets)
        
        if dog_save_success and diet_save_success:
            deleted_types = []
            if dog_deleted:
                deleted_types.append('dog')
            if diet_deleted:
                deleted_types.append('diet')
                
            return jsonify({
                'success': True,
                'message': f"Deleted {', '.join(deleted_types)} record(s) for user {user_id}"
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to save updated records'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ==================== UTILITY ENDPOINTS ====================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'success': True,
        'message': 'Dog Management API is running',
        'timestamp': get_current_timestamp()
    }), 200

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get statistics about the stored data."""
    try:
        dogs = load_data(DOG_DATA_FILE)
        diets = load_data(DIET_DATA_FILE)
        
        return jsonify({
            'success': True,
            'data': {
                'totalDogRecords': len(dogs),
                'totalDietRecords': len(diets),
                'totalUsers': len(set([d['userId'] for d in dogs] + [d['userId'] for d in diets])),
                'lastUpdated': get_current_timestamp()
            }
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404

@app.errorhandler(405)
def method_not_allowed(error):
    """Handle 405 errors."""
    return jsonify({
        'success': False,
        'error': 'Method not allowed'
    }), 405

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500

# ==================== MAIN ====================

if __name__ == '__main__':
    print("=" * 60)
    print("🐕 Dog Management API Server Starting...")
    print("=" * 60)
    print(f"📁 Data directory: {os.path.abspath(DATA_DIR)}")
    print(f"🐕 Dog data file: {os.path.abspath(DOG_DATA_FILE)}")
    print(f"🍽️  Diet data file: {os.path.abspath(DIET_DATA_FILE)}")
    print("=" * 60)
    print("Available endpoints:")
    print("  GET    /api/health           - Health check")
    print("  GET    /api/stats            - Get statistics")
    print("  GET    /api/dogs             - Get all dogs")
    print("  POST   /api/dogs             - Create dog")
    print("  GET    /api/dogs/<user_id>   - Get dog by user ID")
    print("  PUT    /api/dogs/<user_id>   - Update dog")
    print("  DELETE /api/dogs/<user_id>   - Delete dog")
    print("  GET    /api/diets            - Get all diets")
    print("  POST   /api/diets            - Create diet")
    print("  GET    /api/diets/<user_id>  - Get diet by user ID")
    print("  PUT    /api/diets/<user_id>  - Update diet")
    print("  DELETE /api/diets/<user_id>  - Delete diet")
    print("  GET    /api/users/<user_id>  - Get user's records")
    print("  DELETE /api/users/<user_id>  - Delete user's records")
    print("=" * 60)
    
    # Run the Flask application
    app.run(debug=True, host='127.0.0.1', port=5000)