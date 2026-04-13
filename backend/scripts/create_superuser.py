#!/usr/bin/env python3
"""
Create an admin user for the application.

Usage:
    uv run python scripts/create_superuser.py --email admin@example.com --name "Admin User" --password "changeme"

This script is intended to be run once after deployment to create the first user.
"""
import argparse
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.features.auth.utils import get_password_hash, set_user_password
from app.core.features.users.models import User, UserRole
from app.database import Base, SessionLocal, engine


def create_superuser(email: str, name: str, password: str) -> None:
    """Create an admin user if it doesn't already exist."""
    db = SessionLocal()
    try:
        # Check if user already exists
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            print(f"User with email '{email}' already exists (id={existing.id}).")
            return

        # Create user
        user = User(
            email=email,
            name=name,
            role=UserRole.ADMIN,
            is_active=True,
        )
        db.add(user)
        db.flush()

        # Set password
        set_user_password(db, user.id, password)

        db.commit()
        print(f"Admin user created successfully:")
        print(f"  Email: {email}")
        print(f"  Name:  {name}")
        print(f"  Role:  {user.role}")
        print(f"  ID:    {user.id}")
        print()
        print("You can now log in at the login page.")
        print("Remember to change the default password after your first login.")
    except Exception as e:
        db.rollback()
        print(f"Error creating user: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        db.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Create an admin user for the application.")
    parser.add_argument("--email", required=True, help="Email address for the admin user")
    parser.add_argument("--name", required=True, help="Display name for the admin user")
    parser.add_argument("--password", required=True, help="Initial password for the admin user")
    args = parser.parse_args()

    if len(args.password) < 8:
        print("Error: Password must be at least 8 characters.", file=sys.stderr)
        sys.exit(1)

    create_superuser(args.email, args.name, args.password)


if __name__ == "__main__":
    main()
