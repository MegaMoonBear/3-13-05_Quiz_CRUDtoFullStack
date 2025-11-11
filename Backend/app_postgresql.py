#!/usr/bin/env python3
"""
Dog Management API Server with PostgreSQL
A Flask-based REST API server supporting CRUD operations with PostgreSQL backend.

This version replaces the JSON file storage with PostgreSQL database.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
import psycopg2.extras
import psycopg2.pool
import os
from datetime import datetime
import uuid
import logging

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 5432)),
    'database': os.getenv('DB_NAME', 'dog_management'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'password'),
    'minconn': 1,
    'maxconn': 20
}

# Database connection pool
db_pool = None

def init_db_pool():
    """Initialize database connection pool."""
    global db_pool
    try:
        db_pool = psycopg2.pool.ThreadedConnectionPool(**DB_CONFIG)
        logger.info("✅ Database connection pool initialized")
        return True
    except Exception as e:
        logger.error(f"❌ Error initializing database pool: {e}")
        return False

def get_db_connection():
    """Get a database connection from the pool."""
    try:
        return db_pool.getconn()
    except Exception as e:
        logger.error(f"Error getting database connection: {e}")
        return None

def return_db_connection(conn):
    """Return a database connection to the pool."""
    try:
        db_pool.putconn(conn)
    except Exception as e:
        logger.error(f"Error returning database connection: {e}")

def execute_query(query, params=None, fetch=False, fetch_one=False):
    """Execute a database query and return results."""
    conn = get_db_connection()
    if not conn:
        return None, "Database connection error"
    
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute(query, params)
        
        if fetch_one:
            result = cursor.fetchone()
        elif fetch:
            result = cursor.fetchall()
        else:
            result = cursor.rowcount
        
        conn.commit()
        cursor.close()
        return result, None
    
    except Exception as e:
        conn.rollback()
        logger.error(f"Database query error: {e}")
        return None, str(e)
    
    finally:
        return_db_connection(conn)

def get_current_timestamp():
    """Get current timestamp in ISO format."""
    return datetime.now().isoformat()

def validate_dog_data(data):
    """Validate dog data structure."""
    required_fields = ['userId', 'name', 'age', 'breeds', 'weight']
    
    for field in required_fields:
        if field not in data:
            return False, f"Missing required field: {field}"
    
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

def ensure_user_exists(user_id):
    """Ensure user exists in the database."""
    query = "SELECT user_id FROM users WHERE user_id = %s"
    result, error = execute_query(query, (user_id,), fetch_one=True)
    
    if error:
        return False, error
    
    if not result:
        # Create user if doesn't exist
        insert_query = "INSERT INTO users (user_id) VALUES (%s)"
        _, error = execute_query(insert_query, (user_id,))
        if error:
            return False, error
    
    return True, None

def get_breed_ids(breed_codes):
    """Get breed IDs from breed codes."""
    if not breed_codes:
        return []
    
    placeholders = ','.join(['%s'] * len(breed_codes))
    query = f"SELECT breed_id, breed_code FROM breeds WHERE breed_code IN ({placeholders})"
    result, error = execute_query(query, breed_codes, fetch=True)
    
    if error:
        return []
    
    return {row['breed_code']: row['breed_id'] for row in result}

# ==================== DOG ENDPOINTS ====================

@app.route('/api/dogs', methods=['GET'])
def get_all_dogs():
    """Get all dog records with breed information."""
    try:
        query = """
            SELECT 
                d.dog_id::text,
                d.user_id,
                d.name,
                d.age,
                d.weight,
                d.other_breeds,
                d.created_at,
                d.updated_at,
                COALESCE(ARRAY_AGG(b.breed_code) FILTER (WHERE b.breed_code IS NOT NULL), '{}') as breeds
            FROM dogs d
            LEFT JOIN dog_breeds db ON d.dog_id = db.dog_id
            LEFT JOIN breeds b ON db.breed_id = b.breed_id
            GROUP BY d.dog_id, d.user_id, d.name, d.age, d.weight, d.other_breeds, d.created_at, d.updated_at
            ORDER BY d.created_at DESC
        """
        
        dogs, error = execute_query(query, fetch=True)
        
        if error:
            return jsonify({
                'success': False,
                'error': error
            }), 500
        
        # Convert to expected format
        dog_list = []
        for dog in dogs:
            dog_dict = dict(dog)
            dog_dict['id'] = dog_dict.pop('dog_id')
            dog_dict['createdAt'] = dog_dict.pop('created_at').isoformat() if dog_dict['created_at'] else None
            dog_dict['updatedAt'] = dog_dict.pop('updated_at').isoformat() if dog_dict['updated_at'] else None
            dog_dict['otherBreeds'] = dog_dict.pop('other_breeds') or ''
            dog_list.append(dog_dict)
        
        return jsonify({
            'success': True,
            'data': dog_list,
            'count': len(dog_list)
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
        query = """
            SELECT 
                d.dog_id::text,
                d.user_id,
                d.name,
                d.age,
                d.weight,
                d.other_breeds,
                d.created_at,
                d.updated_at,
                COALESCE(ARRAY_AGG(b.breed_code) FILTER (WHERE b.breed_code IS NOT NULL), '{}') as breeds
            FROM dogs d
            LEFT JOIN dog_breeds db ON d.dog_id = db.dog_id
            LEFT JOIN breeds b ON db.breed_id = b.breed_id
            WHERE d.user_id = %s
            GROUP BY d.dog_id, d.user_id, d.name, d.age, d.weight, d.other_breeds, d.created_at, d.updated_at
        """
        
        dog, error = execute_query(query, (user_id,), fetch_one=True)
        
        if error:
            return jsonify({
                'success': False,
                'error': error
            }), 500
        
        if not dog:
            return jsonify({
                'success': False,
                'error': 'Dog record not found for this user ID'
            }), 404
        
        # Convert to expected format
        dog_dict = dict(dog)
        dog_dict['id'] = dog_dict.pop('dog_id')
        dog_dict['createdAt'] = dog_dict.pop('created_at').isoformat() if dog_dict['created_at'] else None
        dog_dict['updatedAt'] = dog_dict.pop('updated_at').isoformat() if dog_dict['updated_at'] else None
        dog_dict['otherBreeds'] = dog_dict.pop('other_breeds') or ''
        
        return jsonify({
            'success': True,
            'data': dog_dict
        }), 200
        
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
        
        # Ensure user exists
        user_exists, error = ensure_user_exists(data['userId'])
        if not user_exists:
            return jsonify({
                'success': False,
                'error': f"Error creating user: {error}"
            }), 500
        
        # Check if user already has a dog record
        existing_query = "SELECT dog_id FROM dogs WHERE user_id = %s"
        existing, error = execute_query(existing_query, (data['userId'],), fetch_one=True)
        
        if error:
            return jsonify({
                'success': False,
                'error': error
            }), 500
        
        if existing:
            return jsonify({
                'success': False,
                'error': 'Dog record already exists for this user ID'
            }), 409
        
        # Create dog record
        dog_id = str(uuid.uuid4())
        insert_query = """
            INSERT INTO dogs (dog_id, user_id, name, age, weight, other_breeds)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        _, error = execute_query(insert_query, (
            dog_id,
            data['userId'].strip(),
            data['name'].strip(),
            int(data['age']),
            float(data['weight']),
            data.get('otherBreeds', '').strip()
        ))
        
        if error:
            return jsonify({
                'success': False,
                'error': f"Failed to create dog record: {error}"
            }), 500
        
        # Add breed associations
        breed_ids = get_breed_ids(data['breeds'])
        for breed_code in data['breeds']:
            if breed_code in breed_ids:
                breed_query = "INSERT INTO dog_breeds (dog_id, breed_id) VALUES (%s, %s)"
                execute_query(breed_query, (dog_id, breed_ids[breed_code]))
        
        # Get the created record
        return get_dog_by_user_id(data['userId'])
        
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
        
        # Check if dog exists
        dog_query = "SELECT dog_id FROM dogs WHERE user_id = %s"
        dog, error = execute_query(dog_query, (user_id,), fetch_one=True)
        
        if error:
            return jsonify({
                'success': False,
                'error': error
            }), 500
        
        if not dog:
            return jsonify({
                'success': False,
                'error': 'Dog record not found for this user ID'
            }), 404
        
        dog_id = dog['dog_id']
        
        # Update dog record
        update_query = """
            UPDATE dogs 
            SET user_id = %s, name = %s, age = %s, weight = %s, other_breeds = %s, updated_at = CURRENT_TIMESTAMP
            WHERE dog_id = %s
        """
        
        _, error = execute_query(update_query, (
            data['userId'].strip(),
            data['name'].strip(),
            int(data['age']),
            float(data['weight']),
            data.get('otherBreeds', '').strip(),
            dog_id
        ))
        
        if error:
            return jsonify({
                'success': False,
                'error': f"Failed to update dog record: {error}"
            }), 500
        
        # Update breed associations
        # First, delete existing associations
        delete_breeds_query = "DELETE FROM dog_breeds WHERE dog_id = %s"
        execute_query(delete_breeds_query, (dog_id,))
        
        # Add new breed associations
        breed_ids = get_breed_ids(data['breeds'])
        for breed_code in data['breeds']:
            if breed_code in breed_ids:
                breed_query = "INSERT INTO dog_breeds (dog_id, breed_id) VALUES (%s, %s)"
                execute_query(breed_query, (dog_id, breed_ids[breed_code]))
        
        # Get the updated record
        return get_dog_by_user_id(data['userId'])
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/dogs/<user_id>', methods=['DELETE'])
def delete_dog(user_id):
    """Delete a dog record."""
    try:
        # Check if dog exists
        dog_query = "SELECT dog_id FROM dogs WHERE user_id = %s"
        dog, error = execute_query(dog_query, (user_id,), fetch_one=True)
        
        if error:
            return jsonify({
                'success': False,
                'error': error
            }), 500
        
        if not dog:
            return jsonify({
                'success': False,
                'error': 'Dog record not found for this user ID'
            }), 404
        
        # Delete dog record (cascade will handle breed associations)
        delete_query = "DELETE FROM dogs WHERE user_id = %s"
        rows_affected, error = execute_query(delete_query, (user_id,))
        
        if error:
            return jsonify({
                'success': False,
                'error': f"Failed to delete dog record: {error}"
            }), 500
        
        return jsonify({
            'success': True,
            'message': 'Dog record deleted successfully'
        }), 200
        
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
        query = """
            SELECT 
                diet_id::text as id,
                user_id as "userId",
                food_type as "foodType",
                brand,
                amount,
                feeding_times as "feedingTimes",
                notes,
                created_at as "createdAt",
                updated_at as "updatedAt"
            FROM diets
            ORDER BY created_at DESC
        """
        
        diets, error = execute_query(query, fetch=True)
        
        if error:
            return jsonify({
                'success': False,
                'error': error
            }), 500
        
        # Convert timestamps
        diet_list = []
        for diet in diets:
            diet_dict = dict(diet)
            diet_dict['createdAt'] = diet_dict['createdAt'].isoformat() if diet_dict['createdAt'] else None
            diet_dict['updatedAt'] = diet_dict['updatedAt'].isoformat() if diet_dict['updatedAt'] else None
            diet_list.append(diet_dict)
        
        return jsonify({
            'success': True,
            'data': diet_list,
            'count': len(diet_list)
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
        query = """
            SELECT 
                diet_id::text as id,
                user_id as "userId",
                food_type as "foodType",
                brand,
                amount,
                feeding_times as "feedingTimes",
                notes,
                created_at as "createdAt",
                updated_at as "updatedAt"
            FROM diets
            WHERE user_id = %s
        """
        
        diet, error = execute_query(query, (user_id,), fetch_one=True)
        
        if error:
            return jsonify({
                'success': False,
                'error': error
            }), 500
        
        if not diet:
            return jsonify({
                'success': False,
                'error': 'Diet record not found for this user ID'
            }), 404
        
        # Convert timestamps
        diet_dict = dict(diet)
        diet_dict['createdAt'] = diet_dict['createdAt'].isoformat() if diet_dict['createdAt'] else None
        diet_dict['updatedAt'] = diet_dict['updatedAt'].isoformat() if diet_dict['updatedAt'] else None
        
        return jsonify({
            'success': True,
            'data': diet_dict
        }), 200
        
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
        
        # Ensure user exists
        user_exists, error = ensure_user_exists(data['userId'])
        if not user_exists:
            return jsonify({
                'success': False,
                'error': f"Error creating user: {error}"
            }), 500
        
        # Check if user already has a diet record
        existing_query = "SELECT diet_id FROM diets WHERE user_id = %s"
        existing, error = execute_query(existing_query, (data['userId'],), fetch_one=True)
        
        if error:
            return jsonify({
                'success': False,
                'error': error
            }), 500
        
        if existing:
            return jsonify({
                'success': False,
                'error': 'Diet record already exists for this user ID'
            }), 409
        
        # Create diet record
        insert_query = """
            INSERT INTO diets (user_id, food_type, brand, amount, feeding_times, notes)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        _, error = execute_query(insert_query, (
            data['userId'].strip(),
            data['foodType'],
            data['brand'].strip(),
            data['amount'].strip(),
            int(data['feedingTimes']),
            data.get('notes', '').strip()
        ))
        
        if error:
            return jsonify({
                'success': False,
                'error': f"Failed to create diet record: {error}"
            }), 500
        
        # Get the created record
        return get_diet_by_user_id(data['userId'])
        
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
        
        # Check if diet exists
        diet_query = "SELECT diet_id FROM diets WHERE user_id = %s"
        diet, error = execute_query(diet_query, (user_id,), fetch_one=True)
        
        if error:
            return jsonify({
                'success': False,
                'error': error
            }), 500
        
        if not diet:
            return jsonify({
                'success': False,
                'error': 'Diet record not found for this user ID'
            }), 404
        
        # Update diet record
        update_query = """
            UPDATE diets 
            SET user_id = %s, food_type = %s, brand = %s, amount = %s, 
                feeding_times = %s, notes = %s, updated_at = CURRENT_TIMESTAMP
            WHERE user_id = %s
        """
        
        _, error = execute_query(update_query, (
            data['userId'].strip(),
            data['foodType'],
            data['brand'].strip(),
            data['amount'].strip(),
            int(data['feedingTimes']),
            data.get('notes', '').strip(),
            user_id
        ))
        
        if error:
            return jsonify({
                'success': False,
                'error': f"Failed to update diet record: {error}"
            }), 500
        
        # Get the updated record
        return get_diet_by_user_id(data['userId'])
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/diets/<user_id>', methods=['DELETE'])
def delete_diet(user_id):
    """Delete a diet record."""
    try:
        # Check if diet exists
        diet_query = "SELECT diet_id FROM diets WHERE user_id = %s"
        diet, error = execute_query(diet_query, (user_id,), fetch_one=True)
        
        if error:
            return jsonify({
                'success': False,
                'error': error
            }), 500
        
        if not diet:
            return jsonify({
                'success': False,
                'error': 'Diet record not found for this user ID'
            }), 404
        
        # Delete diet record
        delete_query = "DELETE FROM diets WHERE user_id = %s"
        rows_affected, error = execute_query(delete_query, (user_id,))
        
        if error:
            return jsonify({
                'success': False,
                'error': f"Failed to delete diet record: {error}"
            }), 500
        
        return jsonify({
            'success': True,
            'message': 'Diet record deleted successfully'
        }), 200
        
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
        # Get dog record
        dog_response = get_dog_by_user_id(user_id)
        dog_record = None
        if dog_response[1] == 200:  # Success
            dog_record = dog_response[0].get_json()['data']
        
        # Get diet record
        diet_response = get_diet_by_user_id(user_id)
        diet_record = None
        if diet_response[1] == 200:  # Success
            diet_record = diet_response[0].get_json()['data']
        
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
        deleted_types = []
        
        # Delete dog record
        dog_query = "DELETE FROM dogs WHERE user_id = %s"
        dog_rows, error = execute_query(dog_query, (user_id,))
        if error:
            return jsonify({
                'success': False,
                'error': f"Failed to delete dog records: {error}"
            }), 500
        if dog_rows > 0:
            deleted_types.append('dog')
        
        # Delete diet record
        diet_query = "DELETE FROM diets WHERE user_id = %s"
        diet_rows, error = execute_query(diet_query, (user_id,))
        if error:
            return jsonify({
                'success': False,
                'error': f"Failed to delete diet records: {error}"
            }), 500
        if diet_rows > 0:
            deleted_types.append('diet')
        
        if not deleted_types:
            return jsonify({
                'success': False,
                'error': 'No records found for this user ID'
            }), 404
        
        return jsonify({
            'success': True,
            'message': f"Deleted {', '.join(deleted_types)} record(s) for user {user_id}"
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ==================== UTILITY ENDPOINTS ====================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    try:
        # Test database connection
        test_query = "SELECT 1"
        result, error = execute_query(test_query, fetch_one=True)
        
        if error:
            return jsonify({
                'success': False,
                'message': 'Database connection failed',
                'error': error,
                'timestamp': get_current_timestamp()
            }), 503
        
        return jsonify({
            'success': True,
            'message': 'Dog Management API with PostgreSQL is running',
            'database': 'Connected',
            'timestamp': get_current_timestamp()
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Health check failed',
            'error': str(e),
            'timestamp': get_current_timestamp()
        }), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get statistics about the stored data."""
    try:
        stats_query = """
            SELECT 
                (SELECT COUNT(*) FROM dogs) as dog_count,
                (SELECT COUNT(*) FROM diets) as diet_count,
                (SELECT COUNT(DISTINCT user_id) FROM (
                    SELECT user_id FROM dogs UNION SELECT user_id FROM diets
                ) u) as user_count,
                (SELECT COUNT(*) FROM breeds) as breed_count
        """
        
        stats, error = execute_query(stats_query, fetch_one=True)
        
        if error:
            return jsonify({
                'success': False,
                'error': error
            }), 500
        
        return jsonify({
            'success': True,
            'data': {
                'totalDogRecords': stats['dog_count'],
                'totalDietRecords': stats['diet_count'],
                'totalUsers': stats['user_count'],
                'totalBreeds': stats['breed_count'],
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
    print("🐕 Dog Management API Server with PostgreSQL Starting...")
    print("=" * 60)
    print(f"🗄️  Database: {DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}")
    print(f"👤 User: {DB_CONFIG['user']}")
    
    # Initialize database connection pool
    if not init_db_pool():
        print("❌ Failed to initialize database connection pool")
        exit(1)
    
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
    try:
        app.run(debug=True, host='127.0.0.1', port=5000)
    finally:
        if db_pool:
            db_pool.closeall()
            print("🔌 Database connection pool closed")