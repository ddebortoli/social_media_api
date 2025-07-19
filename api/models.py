"""
Django models for the Social Media API.

This module contains the data models for users, posts, and comments,
implementing a social media platform's core functionality.
"""

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator
from django.utils import timezone


class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.
    
    This model represents users in the social media platform with additional
    fields for email and following relationships.
    
    Attributes:
        email: User's email address (unique)
        followers: Many-to-many relationship with other users (who follows this user)
        following: Many-to-many relationship with other users (who this user follows)
    """
    
    email = models.EmailField(
        unique=True,
        help_text="User's email address (must be unique)"
    )
    followers = models.ManyToManyField(
        'self',
        symmetrical=False,
        related_name='following',
        blank=True,
        help_text="Users who follow this user"
    )
    
    # Override default groups and permissions to avoid conflicts
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    class Meta:
        """Meta options for User model."""
        verbose_name = "User"
        verbose_name_plural = "Users"
        db_table = 'api_user'

    def __str__(self) -> str:
        """Return string representation of the user."""
        return self.username

    def get_followers_count(self) -> int:
        """
        Get the number of followers for this user.
        
        Returns:
            Number of followers
        """
        return self.followers.count()

    def get_following_count(self) -> int:
        """
        Get the number of users this user is following.
        
        Returns:
            Number of users being followed
        """
        return self.following.count()

    def is_following(self, user: 'User') -> bool:
        """
        Check if this user is following another user.
        
        Args:
            user: The user to check if being followed
            
        Returns:
            True if following, False otherwise
        """
        return user in self.following.all()


class Post(models.Model):
    """
    Post model representing user posts in the social media platform.
    
    This model stores posts created by users with content and metadata.
    
    Attributes:
        author: Foreign key to User who created the post
        content: The post content text
        created_at: Timestamp when the post was created
    """
    
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        db_index=True,
        related_name='posts',
        help_text="User who created this post"
    )
    content = models.TextField(
        validators=[MinLengthValidator(1, "Post content cannot be empty")],
        help_text="The content of the post"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text="Timestamp when the post was created"
    )

    class Meta:
        """Meta options for Post model."""
        verbose_name = "Post"
        verbose_name_plural = "Posts"
        db_table = 'api_post'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['author', 'created_at']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self) -> str:
        """Return string representation of the post."""
        return f"Post by {self.author.username} at {self.created_at}"

    def get_comments_count(self) -> int:
        """
        Get the number of comments on this post.
        
        Returns:
            Number of comments
        """
        return self.comments.count()

    def get_recent_comments(self, limit: int = 3):
        """
        Get the most recent comments for this post.
        
        Args:
            limit: Maximum number of comments to return
            
        Returns:
            QuerySet of recent comments
        """
        return self.comments.order_by('-created_at')[:limit]


class Comment(models.Model):
    """
    Comment model representing comments on posts.
    
    This model stores comments made by users on posts with content and metadata.
    
    Attributes:
        author: Foreign key to User who created the comment
        post: Foreign key to Post being commented on
        content: The comment content text
        created_at: Timestamp when the comment was created
    """
    
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        db_index=True,
        related_name='comments',
        help_text="User who created this comment"
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        db_index=True,
        related_name='comments',
        help_text="Post this comment belongs to"
    )
    content = models.TextField(
        validators=[MinLengthValidator(1, "Comment content cannot be empty")],
        help_text="The content of the comment"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text="Timestamp when the comment was created"
    )

    class Meta:
        """Meta options for Comment model."""
        verbose_name = "Comment"
        verbose_name_plural = "Comments"
        db_table = 'api_comment'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['author', 'post', 'created_at']),
            models.Index(fields=['post', 'created_at']),
        ]

    def __str__(self) -> str:
        """Return string representation of the comment."""
        return f"Comment by {self.author.username} on {self.post.id} at {self.created_at}"

    def clean(self):
        """
        Validate the comment model.
        
        Raises:
            ValidationError: If the comment is invalid
        """
        from django.core.exceptions import ValidationError
        
        if not self.content or not self.content.strip():
            raise ValidationError("Comment content cannot be empty")
        
        super().clean()

    def save(self, *args, **kwargs):
        """Save the comment with validation."""
        self.clean()
        super().save(*args, **kwargs)
