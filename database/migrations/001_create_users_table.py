"""
Migration: Create users table and seed initial users

Run this script to create the users table in your database.
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Load environment variables
load_dotenv()

# Import models
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from database.models.user import User, Base
from logic.auth import AuthManager


def create_tables(engine):
    """
    Create all database tables

    Args:
        engine: SQLAlchemy engine
    """
    print("Creating database tables...")
    Base.metadata.create_all(engine)
    print("Tables created successfully!")


def seed_initial_users(db_session, auth_manager):
    """
    Seed initial admin users (Bruno and Rafael)

    Args:
        db_session: SQLAlchemy database session
        auth_manager: AuthManager instance
    """
    print("\nSeeding initial users...")

    # Get user names from environment or use defaults
    socio_1_name = os.getenv('SOCIO_1_NOME', 'Bruno Amaral')
    socio_2_name = os.getenv('SOCIO_2_NOME', 'Rafael Reigota')

    # Check if users already exist
    existing_users = db_session.query(User).count()
    if existing_users > 0:
        print(f"Users already exist in database ({existing_users} users found). Skipping seed.")
        return

    # Create initial users
    users_to_create = [
        {
            'email': 'bruno@agoramedia.pt',
            'password': 'changeme123',  # IMPORTANT: Change this password after first login!
            'name': socio_1_name,
            'role': 'socio'
        },
        {
            'email': 'rafael@agoramedia.pt',
            'password': 'changeme123',  # IMPORTANT: Change this password after first login!
            'name': socio_2_name,
            'role': 'socio'
        }
    ]

    created_count = 0
    for user_data in users_to_create:
        success, user = auth_manager.create_user(
            email=user_data['email'],
            password=user_data['password'],
            name=user_data['name'],
            role=user_data['role']
        )

        if success:
            print(f"  ✓ Created user: {user_data['name']} ({user_data['email']})")
            created_count += 1
        else:
            print(f"  ✗ Failed to create user: {user_data['name']}")

    print(f"\nSeeded {created_count} users successfully!")
    print("\n⚠️  IMPORTANT: Default password is 'changeme123' - Please change it after first login!")


def run_migration():
    """Run the migration"""
    print("=" * 60)
    print("Migration: Create Users Table")
    print("=" * 60)

    # Get database URL
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        print("\n⚠️  WARNING: DATABASE_URL not set in .env file")
        print("Using SQLite database as fallback: ./agora_media.db")
        database_url = "sqlite:///./agora_media.db"

    print(f"\nDatabase: {database_url.split('@')[-1] if '@' in database_url else database_url}")

    try:
        # Create engine and session
        engine = create_engine(database_url)
        Session = sessionmaker(bind=engine)
        db_session = Session()

        # Create tables
        create_tables(engine)

        # Create auth manager
        auth_manager = AuthManager(db_session)

        # Seed initial users
        should_seed = input("\nDo you want to seed initial users? (y/n): ").lower().strip()
        if should_seed == 'y':
            seed_initial_users(db_session, auth_manager)

        # Close session
        db_session.close()

        print("\n" + "=" * 60)
        print("Migration completed successfully!")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Migration failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_migration()
