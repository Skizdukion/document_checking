import os
import json
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Get the database URL from environment variables
DATABASE_URL = os.environ.get('DATABASE_URL')

# Create a database engine
if DATABASE_URL:
    engine = create_engine(DATABASE_URL)
else:
    # Fallback to SQLite for local development
    engine = create_engine('sqlite:///validation_data.db')

# Create a base class for our models
Base = declarative_base()

# Create a session factory
Session = sessionmaker(bind=engine)

# Define our database models


class ValidationRecord(Base):
    """Model to store validation records."""
    __tablename__ = 'validation_records'

    id = Column(Integer, primary_key=True)
    email = Column(String(255), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    personal_data = Column(Text)  # JSON string
    academic_data = Column(Text)  # JSON string
    validation_results = Column(Text)  # JSON string
    status = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        """Convert record to dictionary."""
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'personal_data': json.loads(self.personal_data) if isinstance(self.personal_data, str) else {},
            'academic_data': json.loads(self.academic_data) if isinstance(self.academic_data, str) else {},
            'validation_results': json.loads(self.validation_results) if isinstance(self.validation_results, str) else {},
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


# Function to initialize the database
def init_db():
    """Create database tables if they don't exist."""
    try:
        Base.metadata.create_all(engine)
        print("Database tables created successfully")
        return True
    except Exception as e:
        print(f"Error creating database tables: {e}")
        return False


# Function to save validation data
def save_validation_data(personal_data, academic_data, validation_results):
    """
    Save validation data to database.

    Args:
        personal_data (dict): Personal information
        academic_data (dict): Academic information
        validation_results (dict): Validation results

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Create a new session
        session = Session()

        # Create a new validation record
        record = ValidationRecord(
            email=personal_data.get('email', 'unknown'),
            name=personal_data.get('name', 'Unknown User'),
            personal_data=json.dumps(personal_data),
            academic_data=json.dumps(academic_data),
            validation_results=json.dumps(validation_results),
            status=validation_results.get('overall_status', 'Unknown')
        )

        # Add and commit the record
        session.add(record)
        session.commit()

        # Close the session
        session.close()

        return True
    except Exception as e:
        print(f"Error saving validation data: {e}")
        return False


# Function to get validation history for a user
def get_user_validation_history(email):
    """
    Get validation history for a user.

    Args:
        email (str): User's email

    Returns:
        list: List of validation records
    """
    try:
        # Create a new session
        session = Session()

        # Query records for the user
        records = session.query(ValidationRecord).filter_by(
            email=email).order_by(ValidationRecord.created_at.desc()).all()

        # Convert records to dictionaries
        result = [record.to_dict() for record in records]

        # Close the session
        session.close()

        return result
    except Exception as e:
        print(f"Error getting validation history: {e}")
        return []


# Initialize the database when this module is imported
if DATABASE_URL:
    init_db()
