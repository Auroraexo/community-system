import os
import sys
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))

# Add src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable not set.")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Define association table for User-Role many-to-many relationship
user_roles_association = Table(
    'user_roles', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('role_id', Integer, ForeignKey('roles.id'))
)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(100), unique=True, index=True)
    name = Column(String(100))
    password_hash = Column(String(255))
    is_active = Column(Integer, default=1) # Use Integer for boolean in SQLite
    phone = Column(String(20))

    roles = relationship("Role", secondary=user_roles_association, back_populates="users")

class Role(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True)
    description = Column(String(255))

    users = relationship("User", secondary=user_roles_association, back_populates="roles")
    permissions = relationship("Permission", secondary="role_permissions", back_populates="roles")

class Permission(Base):
    __tablename__ = "permissions"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True)
    description = Column(String(255))

    roles = relationship("Role", secondary="role_permissions", back_populates="permissions")

role_permissions_association = Table(
    'role_permissions', Base.metadata,
    Column('role_id', Integer, ForeignKey('roles.id')),
    Column('permission_id', Integer, ForeignKey('permissions.id'))
)

def check_users_and_roles():
    db = SessionLocal()
    try:
        users = db.query(User).all()
        if not users:
            print("No users found in the database.")
            return

        print("--- Users and their Roles ---")
        for user in users:
            role_names = [role.name for role in user.roles]
            print(f"Username: {user.username}, Roles: {', '.join(role_names) if role_names else 'No roles assigned'}")
    except Exception as e:
        print(f"Error checking database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_users_and_roles()