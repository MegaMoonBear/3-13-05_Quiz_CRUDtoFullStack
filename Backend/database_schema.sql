-- Dog Management Database Schema
-- PostgreSQL Database Setup Script
-- 
-- This script creates the necessary tables for the Dog Management application
-- Run this script after creating your PostgreSQL database

-- Create the database (run this separately if needed)
-- CREATE DATABASE dog_management;
-- \c dog_management;

-- Enable UUID extension for generating unique IDs
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create Users table to store user information
CREATE TABLE users (
    user_id VARCHAR(50) PRIMARY KEY,
    email VARCHAR(255) UNIQUE,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    phone VARCHAR(20),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create Breeds table for breed reference data
CREATE TABLE breeds (
    breed_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    breed_name VARCHAR(100) NOT NULL UNIQUE,
    breed_code VARCHAR(50) NOT NULL UNIQUE,
    breed_group VARCHAR(50),
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create Dogs table to store dog information
CREATE TABLE dogs (
    dog_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(50) NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    age INTEGER NOT NULL CHECK (age >= 0 AND age <= 30),
    weight DECIMAL(5,2) NOT NULL CHECK (weight > 0 AND weight <= 200),
    other_breeds TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create Dog_Breeds junction table for many-to-many relationship
CREATE TABLE dog_breeds (
    dog_id UUID REFERENCES dogs(dog_id) ON DELETE CASCADE,
    breed_id UUID REFERENCES breeds(breed_id) ON DELETE CASCADE,
    percentage DECIMAL(5,2) CHECK (percentage >= 0 AND percentage <= 100),
    PRIMARY KEY (dog_id, breed_id)
);

-- Create Diets table to store diet information
CREATE TABLE diets (
    diet_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(50) NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    food_type VARCHAR(20) NOT NULL CHECK (food_type IN ('dry', 'wet', 'both')),
    brand VARCHAR(100) NOT NULL,
    amount VARCHAR(100) NOT NULL,
    feeding_times INTEGER NOT NULL CHECK (feeding_times >= 1 AND feeding_times <= 6),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id) -- One diet record per user
);

-- Create indexes for better performance
CREATE INDEX idx_dogs_user_id ON dogs(user_id);
CREATE INDEX idx_diets_user_id ON diets(user_id);
CREATE INDEX idx_dogs_created_at ON dogs(created_at);
CREATE INDEX idx_diets_created_at ON diets(created_at);
CREATE INDEX idx_breeds_code ON breeds(breed_code);

-- Create trigger function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updating timestamps
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_dogs_updated_at BEFORE UPDATE ON dogs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_diets_updated_at BEFORE UPDATE ON diets
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert breed data that matches the frontend options
INSERT INTO breeds (breed_name, breed_code, breed_group) VALUES
    ('Super Mutt', 'super_mutt', 'Mixed'),
    ('Unknown - No Genetic Lab Results', 'unknown', 'Unknown'),
    ('Mixed', 'mixed', 'Mixed'),
    ('American Pit Bull Terrier', 'american_pit_bull_terrier', 'Terrier'),
    ('Beagle', 'beagle', 'Hound'),
    ('Catahoula Leopard Dog', 'catahoula_leopard_dog', 'Herding'),
    ('Chihuahua', 'chihuahua', 'Toy'),
    ('French Bulldog', 'french_bulldog', 'Non-Sporting'),
    ('Golden Retriever', 'golden_retriever', 'Sporting'),
    ('Labrador Retriever', 'labrador_retriever', 'Sporting'),
    ('Shih Tzu', 'shih_tzu', 'Toy'),
    ('Yorkshire Terrier', 'yorkshire_terrier', 'Toy'),
    ('Other', 'other', 'Other');

-- Create views for easier data access

-- View to get complete dog information with breeds
CREATE VIEW dog_details AS
SELECT 
    d.dog_id,
    d.user_id,
    d.name,
    d.age,
    d.weight,
    d.other_breeds,
    d.created_at,
    d.updated_at,
    ARRAY_AGG(b.breed_name ORDER BY db.percentage DESC) as breeds,
    ARRAY_AGG(b.breed_code ORDER BY db.percentage DESC) as breed_codes,
    ARRAY_AGG(db.percentage ORDER BY db.percentage DESC) as breed_percentages
FROM dogs d
LEFT JOIN dog_breeds db ON d.dog_id = db.dog_id
LEFT JOIN breeds b ON db.breed_id = b.breed_id
GROUP BY d.dog_id, d.user_id, d.name, d.age, d.weight, d.other_breeds, d.created_at, d.updated_at;

-- View to get complete user information with dogs and diets
CREATE VIEW user_summary AS
SELECT 
    u.user_id,
    u.email,
    u.first_name,
    u.last_name,
    u.phone,
    COUNT(DISTINCT d.dog_id) as dog_count,
    COUNT(DISTINCT dt.diet_id) as diet_count,
    u.created_at,
    u.updated_at
FROM users u
LEFT JOIN dogs d ON u.user_id = d.user_id
LEFT JOIN diets dt ON u.user_id = dt.user_id
GROUP BY u.user_id, u.email, u.first_name, u.last_name, u.phone, u.created_at, u.updated_at;

-- Create sample data (optional - uncomment to add test data)
/*
-- Insert sample users
INSERT INTO users (user_id, email, first_name, last_name, phone) VALUES
    ('user123', 'john.doe@email.com', 'John', 'Doe', '555-0123'),
    ('user456', 'jane.smith@email.com', 'Jane', 'Smith', '555-0456');

-- Insert sample dogs
INSERT INTO dogs (user_id, name, age, weight, other_breeds) VALUES
    ('user123', 'Buddy', 3, 65.5, 'Some Labrador mix'),
    ('user456', 'Luna', 2, 45.0, NULL);

-- Get the dog IDs for breed associations
DO $$
DECLARE
    buddy_id UUID;
    luna_id UUID;
    golden_retriever_id UUID;
    beagle_id UUID;
    mixed_id UUID;
BEGIN
    -- Get dog IDs
    SELECT dog_id INTO buddy_id FROM dogs WHERE name = 'Buddy' AND user_id = 'user123';
    SELECT dog_id INTO luna_id FROM dogs WHERE name = 'Luna' AND user_id = 'user456';
    
    -- Get breed IDs
    SELECT breed_id INTO golden_retriever_id FROM breeds WHERE breed_code = 'golden_retriever';
    SELECT breed_id INTO beagle_id FROM breeds WHERE breed_code = 'beagle';
    SELECT breed_id INTO mixed_id FROM breeds WHERE breed_code = 'mixed';
    
    -- Associate breeds with dogs
    INSERT INTO dog_breeds (dog_id, breed_id, percentage) VALUES
        (buddy_id, golden_retriever_id, 60.0),
        (buddy_id, mixed_id, 40.0),
        (luna_id, beagle_id, 80.0),
        (luna_id, mixed_id, 20.0);
END $$;

-- Insert sample diets
INSERT INTO diets (user_id, food_type, brand, amount, feeding_times, notes) VALUES
    ('user123', 'both', 'Blue Buffalo', '2 cups dry, 1 can wet', 2, 'Morning dry food, evening wet food'),
    ('user456', 'dry', 'Purina Pro Plan', '1.5 cups', 2, 'High energy formula');
*/

-- Grant permissions (adjust as needed)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO your_app_user;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO your_app_user;

COMMENT ON TABLE users IS 'Stores user/owner information';
COMMENT ON TABLE dogs IS 'Stores individual dog information';
COMMENT ON TABLE breeds IS 'Reference table for dog breeds';
COMMENT ON TABLE dog_breeds IS 'Many-to-many relationship between dogs and breeds with percentages';
COMMENT ON TABLE diets IS 'Stores diet information for each user/dog owner';

-- Display table information
SELECT 'Database schema created successfully!' as status;

-- Show table structure
\d+ users;
\d+ dogs;
\d+ breeds;
\d+ dog_breeds;
\d+ diets;