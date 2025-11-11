# Dog Management API Server

A Flask-based REST API server that provides CRUD operations for dog and diet information management.

## Features

- **Complete CRUD Operations**: Create, Read, Update, Delete for both dog and diet records
- **User-based Organization**: Records are organized by User ID
- **Data Validation**: Comprehensive validation for all input data
- **JSON Data Storage**: Simple file-based storage using JSON
- **CORS Enabled**: Frontend integration ready
- **Error Handling**: Comprehensive error responses
- **Health Check**: API status monitoring

## Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

## Installation

1. **Navigate to the Backend directory:**
   ```bash
   cd Backend
   ```

2. **Install required dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Running the Server

1. **Start the Flask server:**
   ```bash
   python app.py
   ```

2. **The server will start on:**
   ```
   http://127.0.0.1:5000
   ```

## API Endpoints

### Health & Stats
- `GET /api/health` - Health check
- `GET /api/stats` - Get database statistics

### Dog Records
- `GET /api/dogs` - Get all dog records
- `POST /api/dogs` - Create new dog record
- `GET /api/dogs/<user_id>` - Get dog record by user ID
- `PUT /api/dogs/<user_id>` - Update dog record
- `DELETE /api/dogs/<user_id>` - Delete dog record

### Diet Records
- `GET /api/diets` - Get all diet records
- `POST /api/diets` - Create new diet record
- `GET /api/diets/<user_id>` - Get diet record by user ID
- `PUT /api/diets/<user_id>` - Update diet record
- `DELETE /api/diets/<user_id>` - Delete diet record

### User Records
- `GET /api/users/<user_id>` - Get both dog and diet records for a user
- `DELETE /api/users/<user_id>` - Delete all records for a user

## Request/Response Examples

### Create Dog Record (POST /api/dogs)
```json
{
  "userId": "user123",
  "name": "Buddy",
  "age": 3,
  "breeds": ["golden_retriever", "mixed"],
  "otherBreeds": "Some Lab mix",
  "weight": 65.5
}
```

### Create Diet Record (POST /api/diets)
```json
{
  "userId": "user123",
  "foodType": "both",
  "brand": "Blue Buffalo",
  "amount": "2 cups",
  "feedingTimes": 2
}
```

### Successful Response
```json
{
  "success": true,
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "userId": "user123",
    "name": "Buddy",
    "age": 3,
    "breeds": ["golden_retriever", "mixed"],
    "otherBreeds": "Some Lab mix",
    "weight": 65.5,
    "createdAt": "2025-11-10T15:30:45.123456",
    "updatedAt": "2025-11-10T15:30:45.123456"
  },
  "message": "Dog record created successfully"
}
```

### Error Response
```json
{
  "success": false,
  "error": "Missing required field: name"
}
```

## Data Validation

### Dog Records
- **userId**: Required, non-empty string
- **name**: Required, non-empty string
- **age**: Required, integer between 0 and 30
- **breeds**: Required, non-empty list of strings
- **otherBreeds**: Optional string
- **weight**: Required, float between 1 and 200

### Diet Records
- **userId**: Required, non-empty string
- **foodType**: Required, must be "dry", "wet", or "both"
- **brand**: Required, non-empty string
- **amount**: Required, non-empty string
- **feedingTimes**: Required, integer between 1 and 6

## Data Storage

Data is stored in JSON files in the `data/` directory:
- `data/dogs.json` - Dog records
- `data/diets.json` - Diet records

## Error Codes

- `200` - Success
- `201` - Created successfully
- `400` - Bad request (validation errors)
- `404` - Record not found
- `405` - Method not allowed
- `409` - Conflict (record already exists)
- `500` - Internal server error

## Testing the API

You can test the API using tools like:
- **curl** (command line)
- **Postman** (GUI application)
- **Thunder Client** (VS Code extension)
- **Browser** (for GET requests)

### Example curl commands:

```bash
# Health check
curl http://127.0.0.1:5000/api/health

# Get all dogs
curl http://127.0.0.1:5000/api/dogs

# Create a dog record
curl -X POST http://127.0.0.1:5000/api/dogs \
  -H "Content-Type: application/json" \
  -d '{"userId":"test123","name":"Buddy","age":3,"breeds":["golden_retriever"],"weight":65.5}'

# Get dog by user ID
curl http://127.0.0.1:5000/api/dogs/test123

# Update dog record
curl -X PUT http://127.0.0.1:5000/api/dogs/test123 \
  -H "Content-Type: application/json" \
  -d '{"userId":"test123","name":"Buddy Updated","age":4,"breeds":["golden_retriever"],"weight":70.0}'

# Delete dog record
curl -X DELETE http://127.0.0.1:5000/api/dogs/test123
```

## Development Notes

- The server runs in debug mode for development
- Data files are created automatically if they don't exist
- CORS is enabled for frontend integration
- All endpoints return JSON responses
- Timestamps are stored in ISO format

## Frontend Integration

This API is designed to work with the frontend HTML/CSS/JavaScript application. To connect:

1. Update frontend JavaScript to use API endpoints instead of localStorage
2. Replace CRUD operations with HTTP requests
3. Handle API responses and errors appropriately

## Future Enhancements

- Add authentication and authorization
- Implement database backend (PostgreSQL, SQLite, etc.)
- Add data pagination for large datasets
- Implement search and filtering capabilities
- Add file upload for dog photos
- Add logging and monitoring