"""
User model for authentication and authorization
"""

from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, ENUM
import uuid

from app.core.database import Base


class UserRole(str, Enum):
    """User roles"""
    ADMIN = "admin"
    CREATOR = "creator"
    REVIEWER = "reviewer"
    VIEWER = "viewer"


class User(Base):
    """User model"""
    
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    
    role = Column(ENUM(UserRole), default=UserRole.CREATOR, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    
    # Profile information
    bio = Column(Text)
    avatar_url = Column(String(500))
    company = Column(String(255))
    website = Column(String(500))
    
    # Preferences
    preferred_languages = Column(String(500))  # JSON string of language codes
    notification_preferences = Column(Text)  # JSON string
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime)
    
    # Relationships
    projects = relationship("Project", back_populates="owner", cascade="all, delete-orphan")
    jobs = relationship("Job", back_populates="user", cascade="all, delete-orphan")
    consent_records = relationship("ConsentRecord", back_populates="user")
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"
    
    @property
    def is_admin(self) -> bool:
        """Check if user is admin"""
        return self.role == UserRole.ADMIN
    
    @property
    def can_create_projects(self) -> bool:
        """Check if user can create projects"""
        return self.role in [UserRole.ADMIN, UserRole.CREATOR]
    
    @property
    def can_review_translations(self) -> bool:
        """Check if user can review translations"""
        return self.role in [UserRole.ADMIN, UserRole.REVIEWER]