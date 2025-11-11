#!/usr/bin/env python3
"""
Database setup script for Dog Management Application
This script creates the PostgreSQL database and tables programmatically.

Prerequisites:
- PostgreSQL server running locally
- psycopg2 package installed (pip install psycopg2-binary)
- Database and user credentials configured
"""

import psycopg2
import psycopg2.extras
import os
from datetime import datetime

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'dog_management',  # Change this if your database has a different name
    'user': 'postgres',            # Change this to your PostgreSQL username
    'password': 'YOUR_ACTUAL_PASSWORD_HERE'  # ⚠️ CHANGE THIS to your PostgreSQL password
}

# Alternative configuration using environment variables
# Uncomment and set these environment variables if preferred:
# DB_CONFIG = {
#     'host': os.getenv('DB_HOST', 'localhost'),
#     'port': os.getenv('DB_PORT', 5432),
#     'database': os.getenv('DB_NAME', 'dog_management'),
#     'user': os.getenv('DB_USER', 'postgres'),
#     'password': os.getenv('DB_PASSWORD', 'password')
# }

def create_connection():
    """Create a connection to PostgreSQL database."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = True
        print(f"✅ Connected to PostgreSQL database: {DB_CONFIG['database']}")
        return conn
    except psycopg2.OperationalError as e:
        print(f"❌ Error connecting to database: {e}")
        print("\n💡 Make sure:")
        print("  1. PostgreSQL server is running")
        print("  2. Database exists (create it first if needed)")
        print("  3. Username and password are correct")
        print("  4. Host and port are correct")
        return None

def execute_sql_file(conn, file_path):
    """Execute SQL commands from a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            sql_commands = file.read()
        
        cursor = conn.cursor()
        cursor.execute(sql_commands)
        cursor.close()
        print(f"✅ Successfully executed SQL from: {file_path}")
        return True
    except Exception as e:
        print(f"❌ Error executing SQL file: {e}")
        return False

def create_tables_manually(conn):
    """Create tables using individual SQL commands."""
    cursor = conn.cursor()
    
    try:
        print("🏗️  Creating database schema...")
        
        # Enable UUID extension
        cursor.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";')
        print("  ✅ UUID extension enabled")
        
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id VARCHAR(50) PRIMARY KEY,
                email VARCHAR(255) UNIQUE,
                first_name VARCHAR(100),
                last_name VARCHAR(100),
                phone VARCHAR(20),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        ''')
        print("  ✅ Users table created")
        
        # Create breeds table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS breeds (
                breed_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                breed_name VARCHAR(100) NOT NULL UNIQUE,
                breed_code VARCHAR(50) NOT NULL UNIQUE,
                breed_group VARCHAR(50),
                description TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        ''')
        print("  ✅ Breeds table created")
        
        # Create dogs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS dogs (
                dog_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                user_id VARCHAR(50) NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
                name VARCHAR(100) NOT NULL,
                age INTEGER NOT NULL CHECK (age >= 0 AND age <= 30),
                weight DECIMAL(5,2) NOT NULL CHECK (weight > 0 AND weight <= 200),
                other_breeds TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        ''')
        print("  ✅ Dogs table created")
        
        # Create dog_breeds junction table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS dog_breeds (
                dog_id UUID REFERENCES dogs(dog_id) ON DELETE CASCADE,
                breed_id UUID REFERENCES breeds(breed_id) ON DELETE CASCADE,
                percentage DECIMAL(5,2) CHECK (percentage >= 0 AND percentage <= 100),
                PRIMARY KEY (dog_id, breed_id)
            );
        ''')
        print("  ✅ Dog_breeds junction table created")
        
        # Create diets table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS diets (
                diet_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                user_id VARCHAR(50) NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
                food_type VARCHAR(20) NOT NULL CHECK (food_type IN ('dry', 'wet', 'both')),
                brand VARCHAR(100) NOT NULL,
                amount VARCHAR(100) NOT NULL,
                feeding_times INTEGER NOT NULL CHECK (feeding_times >= 1 AND feeding_times <= 6),
                notes TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id)
            );
        ''')
        print("  ✅ Diets table created")
        
        # Create indexes
        indexes = [
            'CREATE INDEX IF NOT EXISTS idx_dogs_user_id ON dogs(user_id);',
            'CREATE INDEX IF NOT EXISTS idx_diets_user_id ON diets(user_id);',
            'CREATE INDEX IF NOT EXISTS idx_dogs_created_at ON dogs(created_at);',
            'CREATE INDEX IF NOT EXISTS idx_diets_created_at ON diets(created_at);',
            'CREATE INDEX IF NOT EXISTS idx_breeds_code ON breeds(breed_code);'
        ]
        
        for index_sql in indexes:
            cursor.execute(index_sql)
        print("  ✅ Indexes created")
        
        # Create trigger function
        cursor.execute('''
            CREATE OR REPLACE FUNCTION update_updated_at_column()
            RETURNS TRIGGER AS $$
            BEGIN
                NEW.updated_at = CURRENT_TIMESTAMP;
                RETURN NEW;
            END;
            $$ language 'plpgsql';
        ''')
        print("  ✅ Update trigger function created")
        
        # Create triggers
        triggers = [
            'CREATE TRIGGER IF NOT EXISTS update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();',
            'CREATE TRIGGER IF NOT EXISTS update_dogs_updated_at BEFORE UPDATE ON dogs FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();',
            'CREATE TRIGGER IF NOT EXISTS update_diets_updated_at BEFORE UPDATE ON diets FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();'
        ]
        
        for trigger_sql in triggers:
            cursor.execute(trigger_sql)
        print("  ✅ Update triggers created")
        
        cursor.close()
        return True
        
    except Exception as e:
        print(f"  ❌ Error creating tables: {e}")
        cursor.close()
        return False

def insert_breed_data(conn):
    """Insert the breed reference data."""
    cursor = conn.cursor()
    
    try:
        print("🐕 Inserting breed data...")
        
        # Check if breeds already exist
        cursor.execute("SELECT COUNT(*) FROM breeds;")
        breed_count = cursor.fetchone()[0]
        
        if breed_count > 0:
            print(f"  ℹ️  Breeds table already has {breed_count} records, skipping insert")
            cursor.close()
            return True
        
        # Insert breed data
        breed_data = [
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
            ('Other', 'other', 'Other')
        ]
        
        insert_sql = '''
            INSERT INTO breeds (breed_name, breed_code, breed_group) 
            VALUES (%s, %s, %s)
        '''
        
        cursor.executemany(insert_sql, breed_data)
        print(f"  ✅ Inserted {len(breed_data)} breed records")
        
        cursor.close()
        return True
        
    except Exception as e:
        print(f"  ❌ Error inserting breed data: {e}")
        cursor.close()
        return False

def create_views(conn):
    """Create database views for easier data access."""
    cursor = conn.cursor()
    
    try:
        print("📊 Creating database views...")
        
        # Dog details view
        cursor.execute('''
            CREATE OR REPLACE VIEW dog_details AS
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
        ''')
        print("  ✅ Dog details view created")
        
        # User summary view
        cursor.execute('''
            CREATE OR REPLACE VIEW user_summary AS
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
        ''')
        print("  ✅ User summary view created")
        
        cursor.close()
        return True
        
    except Exception as e:
        print(f"  ❌ Error creating views: {e}")
        cursor.close()
        return False

def verify_setup(conn):
    """Verify that all tables were created successfully."""
    cursor = conn.cursor()
    
    try:
        print("🔍 Verifying database setup...")
        
        # Check tables
        cursor.execute('''
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name;
        ''')
        
        tables = [row[0] for row in cursor.fetchall()]
        expected_tables = ['users', 'dogs', 'breeds', 'dog_breeds', 'diets']
        
        print(f"  📋 Tables found: {', '.join(tables)}")
        
        missing_tables = [t for t in expected_tables if t not in tables]
        if missing_tables:
            print(f"  ⚠️  Missing tables: {', '.join(missing_tables)}")
            return False
        
        # Check views
        cursor.execute('''
            SELECT table_name 
            FROM information_schema.views 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        ''')
        
        views = [row[0] for row in cursor.fetchall()]
        print(f"  📊 Views found: {', '.join(views) if views else 'None'}")
        
        # Check breed data
        cursor.execute("SELECT COUNT(*) FROM breeds;")
        breed_count = cursor.fetchone()[0]
        print(f"  🐕 Breed records: {breed_count}")
        
        cursor.close()
        print("  ✅ Database verification completed successfully!")
        return True
        
    except Exception as e:
        print(f"  ❌ Error verifying setup: {e}")
        cursor.close()
        return False

def main():
    """Main function to set up the database."""
    print("🚀 Dog Management Database Setup")
    print("=" * 40)
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 Connecting to: {DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}")
    print("=" * 40)
    
    # Create connection
    conn = create_connection()
    if not conn:
        print("\n❌ Setup failed - could not connect to database")
        return False
    
    try:
        # Create tables
        if not create_tables_manually(conn):
            print("\n❌ Setup failed - could not create tables")
            return False
        
        # Insert breed data
        if not insert_breed_data(conn):
            print("\n❌ Setup failed - could not insert breed data")
            return False
        
        # Create views
        if not create_views(conn):
            print("\n❌ Setup failed - could not create views")
            return False
        
        # Verify setup
        if not verify_setup(conn):
            print("\n❌ Setup verification failed")
            return False
        
        print("\n" + "=" * 40)
        print("🎉 Database setup completed successfully!")
        print("=" * 40)
        print("\n📋 Next steps:")
        print("1. Update your Flask app to use PostgreSQL instead of JSON files")
        print("2. Install psycopg2-binary: pip install psycopg2-binary")
        print("3. Update database connection settings in your app")
        print("4. Test the API endpoints with the new database")
        
        return True
        
    finally:
        conn.close()
        print("🔌 Database connection closed")

if __name__ == "__main__":
    success = main()
    if not success:
        exit(1)