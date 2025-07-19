"""
Repository pattern implementation for data access abstraction.

This module provides repository interfaces and implementations to separate
data access logic from business logic, following the Dependency Inversion Principle.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, TypeVar, Generic
from django.db import models
from django.db.models import QuerySet
from django.core.exceptions import ObjectDoesNotExist

T = TypeVar('T', bound=models.Model)


class BaseRepository(ABC, Generic[T]):
    """
    Abstract base repository for data access operations.
    
    This abstract class defines the contract for all repository implementations,
    ensuring consistent data access patterns across the application.
    """
    
    def __init__(self, model: type[T]):
        """
        Initialize repository with the model class.
        
        Args:
            model: The Django model class this repository manages
        """
        self.model = model
    
    @abstractmethod
    def get_by_id(self, id: int) -> Optional[T]:
        """
        Retrieve an entity by its primary key.
        
        Args:
            id: The primary key of the entity
            
        Returns:
            The entity if found, None otherwise
        """
        pass
    
    @abstractmethod
    def get_all(self) -> QuerySet[T]:
        """
        Retrieve all entities.
        
        Returns:
            QuerySet containing all entities
        """
        pass
    
    @abstractmethod
    def create(self, **kwargs) -> T:
        """
        Create a new entity.
        
        Args:
            **kwargs: Entity attributes
            
        Returns:
            The created entity
        """
        pass
    
    @abstractmethod
    def update(self, id: int, **kwargs) -> Optional[T]:
        """
        Update an existing entity.
        
        Args:
            id: The primary key of the entity to update
            **kwargs: Updated attributes
            
        Returns:
            The updated entity if found, None otherwise
        """
        pass
    
    @abstractmethod
    def delete(self, id: int) -> bool:
        """
        Delete an entity by its primary key.
        
        Args:
            id: The primary key of the entity to delete
            
        Returns:
            True if deleted successfully, False otherwise
        """
        pass


class DjangoRepository(BaseRepository[T]):
    """
    Django-specific implementation of the repository pattern.
    
    This implementation uses Django ORM for data access operations.
    """
    
    def get_by_id(self, id: int) -> Optional[T]:
        """
        Retrieve an entity by its primary key using Django ORM.
        
        Args:
            id: The primary key of the entity
            
        Returns:
            The entity if found, None otherwise
        """
        try:
            return self.model.objects.get(pk=id)
        except ObjectDoesNotExist:
            return None
    
    def get_all(self) -> QuerySet[T]:
        """
        Retrieve all entities using Django ORM.
        
        Returns:
            QuerySet containing all entities
        """
        return self.model.objects.all()
    
    def create(self, **kwargs) -> T:
        """
        Create a new entity using Django ORM.
        
        Args:
            **kwargs: Entity attributes
            
        Returns:
            The created entity
        """
        return self.model.objects.create(**kwargs)
    
    def update(self, id: int, **kwargs) -> Optional[T]:
        """
        Update an existing entity using Django ORM.
        
        Args:
            id: The primary key of the entity to update
            **kwargs: Updated attributes
            
        Returns:
            The updated entity if found, None otherwise
        """
        try:
            instance = self.model.objects.get(pk=id)
            for key, value in kwargs.items():
                setattr(instance, key, value)
            instance.save()
            return instance
        except ObjectDoesNotExist:
            return None
    
    def delete(self, id: int) -> bool:
        """
        Delete an entity by its primary key using Django ORM.
        
        Args:
            id: The primary key of the entity to delete
            
        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            instance = self.model.objects.get(pk=id)
            instance.delete()
            return True
        except ObjectDoesNotExist:
            return False


class UserRepository(DjangoRepository):
    """
    Repository for User model operations.
    
    Provides specialized methods for user-related data access operations.
    """
    
    def __init__(self):
        """Initialize UserRepository with User model."""
        from .models import User
        super().__init__(User)
    
    def get_by_username(self, username: str) -> Optional['User']:
        """
        Retrieve a user by username.
        
        Args:
            username: The username to search for
            
        Returns:
            The user if found, None otherwise
        """
        try:
            return self.model.objects.get(username=username)
        except ObjectDoesNotExist:
            return None
    
    def get_by_email(self, email: str) -> Optional['User']:
        """
        Retrieve a user by email.
        
        Args:
            email: The email to search for
            
        Returns:
            The user if found, None otherwise
        """
        try:
            return self.model.objects.get(email=email)
        except ObjectDoesNotExist:
            return None
    
    def get_followers(self, user_id: int) -> QuerySet:
        """
        Get all followers of a user.
        
        Args:
            user_id: The ID of the user
            
        Returns:
            QuerySet of followers
        """
        user = self.get_by_id(user_id)
        if user:
            return user.followers.all()
        return self.model.objects.none()
    
    def get_following(self, user_id: int) -> QuerySet:
        """
        Get all users that a user is following.
        
        Args:
            user_id: The ID of the user
            
        Returns:
            QuerySet of following users
        """
        user = self.get_by_id(user_id)
        if user:
            return user.following.all()
        return self.model.objects.none()


class PostRepository(DjangoRepository):
    """
    Repository for Post model operations.
    
    Provides specialized methods for post-related data access operations.
    """
    
    def __init__(self):
        """Initialize PostRepository with Post model."""
        from .models import Post
        super().__init__(Post)
    
    def get_by_author(self, author_id: int) -> QuerySet:
        """
        Get all posts by a specific author.
        
        Args:
            author_id: The ID of the author
            
        Returns:
            QuerySet of posts by the author
        """
        return self.model.objects.filter(author_id=author_id).order_by('-created_at')
    
    def get_recent_posts(self, limit: int = 20) -> QuerySet:
        """
        Get the most recent posts.
        
        Args:
            limit: Maximum number of posts to return
            
        Returns:
            QuerySet of recent posts
        """
        return self.model.objects.all().order_by('-created_at')[:limit]


class CommentRepository(DjangoRepository):
    """
    Repository for Comment model operations.
    
    Provides specialized methods for comment-related data access operations.
    """
    
    def __init__(self):
        """Initialize CommentRepository with Comment model."""
        from .models import Comment
        super().__init__(Comment)
    
    def get_by_post(self, post_id: int) -> QuerySet:
        """
        Get all comments for a specific post.
        
        Args:
            post_id: The ID of the post
            
        Returns:
            QuerySet of comments for the post
        """
        return self.model.objects.filter(post_id=post_id).order_by('-created_at')
    
    def get_by_author(self, author_id: int) -> QuerySet:
        """
        Get all comments by a specific author.
        
        Args:
            author_id: The ID of the author
            
        Returns:
            QuerySet of comments by the author
        """
        return self.model.objects.filter(author_id=author_id).order_by('-created_at') 