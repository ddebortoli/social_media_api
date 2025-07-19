"""
Service layer implementation for business logic.

This module contains service classes that encapsulate business logic,
separating it from the presentation layer (views) and data access layer (repositories).
"""

from typing import Optional, List, Dict, Any
from django.db.models import Count
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.response import Response

from .repositories import UserRepository, PostRepository, CommentRepository
from .models import User, Post, Comment

User = get_user_model()


class UserService:
    """
    Service class for user-related business logic.
    
    This class encapsulates all business logic related to user operations,
    including user creation, following/unfollowing, and user statistics.
    """
    
    def __init__(self):
        """Initialize UserService with UserRepository."""
        self.user_repository = UserRepository()
    
    def create_user(self, user_data: Dict[str, Any]) -> User:
        """
        Create a new user with validation.
        
        Args:
            user_data: Dictionary containing user data (username, email, password)
            
        Returns:
            The created user
            
        Raises:
            ValidationError: If user data is invalid or user already exists
        """
        username = user_data.get('username')
        email = user_data.get('email')
        password = user_data.get('password')
        
        # Validate required fields
        if not all([username, email, password]):
            raise ValidationError("Username, email, and password are required")
        
        # Check if user already exists
        if self.user_repository.get_by_username(username):
            raise ValidationError("Username already exists")
        
        if self.user_repository.get_by_email(email):
            raise ValidationError("Email already exists")
        
        # Create user
        return self.user_repository.create(
            username=username,
            email=email,
            password=password
        )
    
    def get_user_with_stats(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get user with statistics (posts, comments, followers count).
        
        Args:
            user_id: The ID of the user
            
        Returns:
            Dictionary containing user data with statistics, or None if user not found
        """
        user = self.user_repository.get_by_id(user_id)
        if not user:
            return None
        
        # Get user statistics
        total_posts = Post.objects.filter(author=user).count()
        total_comments = Comment.objects.filter(author=user).count()
        followers_count = user.followers.count()
        following_count = user.following.count()
        
        return {
            'user': user,
            'total_posts': total_posts,
            'total_comments': total_comments,
            'followers_count': followers_count,
            'following_count': following_count
        }
    
    def follow_user(self, follower_id: int, user_to_follow_id: int) -> Dict[str, Any]:
        """
        Follow a user.
        
        Args:
            follower_id: The ID of the user who wants to follow
            user_to_follow_id: The ID of the user to be followed
            
        Returns:
            Dictionary with result information
            
        Raises:
            ValidationError: If users don't exist or already following
        """
        follower = self.user_repository.get_by_id(follower_id)
        user_to_follow = self.user_repository.get_by_id(user_to_follow_id)
        
        if not follower or not user_to_follow:
            raise ValidationError("One or both users not found")
        
        if follower == user_to_follow:
            raise ValidationError("Users cannot follow themselves")
        
        if user_to_follow in follower.following.all():
            raise ValidationError("Already following this user")
        
        follower.following.add(user_to_follow)
        
        return {
            'message': f"{follower.username} is now following {user_to_follow.username}",
            'follower': follower,
            'following': user_to_follow
        }
    
    def unfollow_user(self, follower_id: int, user_to_unfollow_id: int) -> Dict[str, Any]:
        """
        Unfollow a user.
        
        Args:
            follower_id: The ID of the user who wants to unfollow
            user_to_unfollow_id: The ID of the user to be unfollowed
            
        Returns:
            Dictionary with result information
            
        Raises:
            ValidationError: If users don't exist or not following
        """
        follower = self.user_repository.get_by_id(follower_id)
        user_to_unfollow = self.user_repository.get_by_id(user_to_unfollow_id)
        
        if not follower or not user_to_unfollow:
            raise ValidationError("One or both users not found")
        
        if user_to_unfollow not in follower.following.all():
            raise ValidationError("Not following this user")
        
        follower.following.remove(user_to_unfollow)
        
        return {
            'message': f"{follower.username} unfollowed {user_to_unfollow.username}",
            'follower': follower,
            'unfollowed': user_to_unfollow
        }


class PostService:
    """
    Service class for post-related business logic.
    
    This class encapsulates all business logic related to post operations,
    including post creation, retrieval, and filtering.
    """
    
    def __init__(self):
        """Initialize PostService with PostRepository."""
        self.post_repository = PostRepository()
        self.user_repository = UserRepository()
    
    def create_post(self, author_id: int, content: str) -> Post:
        """
        Create a new post.
        
        Args:
            author_id: The ID of the post author
            content: The post content
            
        Returns:
            The created post
            
        Raises:
            ValidationError: If author doesn't exist or content is invalid
        """
        author = self.user_repository.get_by_id(author_id)
        if not author:
            raise ValidationError("Author not found")
        
        if not content or len(content.strip()) == 0:
            raise ValidationError("Post content cannot be empty")
        
        return self.post_repository.create(
            author=author,
            content=content
        )
    
    def get_posts_with_filters(self, filters: Dict[str, Any]) -> List[Post]:
        """
        Get posts with optional filters.
        
        Args:
            filters: Dictionary containing filter parameters
                - author_id: Filter by author
                - from_date: Filter posts from this date
                - to_date: Filter posts until this date
                - limit: Maximum number of posts to return
                
        Returns:
            List of filtered posts
        """
        queryset = self.post_repository.get_all().order_by('-created_at')
        
        # Apply filters
        if filters.get('author_id'):
            queryset = queryset.filter(author_id=filters['author_id'])
        
        if filters.get('from_date'):
            queryset = queryset.filter(created_at__gte=filters['from_date'])
        
        if filters.get('to_date'):
            queryset = queryset.filter(created_at__lte=filters['to_date'])
        
        limit = filters.get('limit', 20)
        return list(queryset[:limit])
    
    def get_post_with_comments(self, post_id: int, comments_limit: int = 3) -> Optional[Dict[str, Any]]:
        """
        Get a post with its recent comments.
        
        Args:
            post_id: The ID of the post
            comments_limit: Maximum number of comments to include
            
        Returns:
            Dictionary containing post data with comments, or None if post not found
        """
        post = self.post_repository.get_by_id(post_id)
        if not post:
            return None
        
        # Get recent comments
        recent_comments = Comment.objects.filter(post=post).order_by('-created_at')[:comments_limit]
        
        return {
            'post': post,
            'recent_comments': recent_comments,
            'total_comments': Comment.objects.filter(post=post).count()
        }


class CommentService:
    """
    Service class for comment-related business logic.
    
    This class encapsulates all business logic related to comment operations,
    including comment creation and retrieval.
    """
    
    def __init__(self):
        """Initialize CommentService with CommentRepository."""
        self.comment_repository = CommentRepository()
        self.user_repository = UserRepository()
        self.post_repository = PostRepository()
    
    def create_comment(self, author_id: int, post_id: int, content: str) -> Comment:
        """
        Create a new comment.
        
        Args:
            author_id: The ID of the comment author
            post_id: The ID of the post being commented on
            content: The comment content
            
        Returns:
            The created comment
            
        Raises:
            ValidationError: If author/post doesn't exist or content is invalid
        """
        author = self.user_repository.get_by_id(author_id)
        if not author:
            raise ValidationError("Author not found")
        
        post = self.post_repository.get_by_id(post_id)
        if not post:
            raise ValidationError("Post not found")
        
        if not content or len(content.strip()) == 0:
            raise ValidationError("Comment content cannot be empty")
        
        return self.comment_repository.create(
            author=author,
            post=post,
            content=content
        )
    
    def get_comments_for_post(self, post_id: int) -> List[Comment]:
        """
        Get all comments for a specific post.
        
        Args:
            post_id: The ID of the post
            
        Returns:
            List of comments for the post
        """
        return list(self.comment_repository.get_by_post(post_id)) 