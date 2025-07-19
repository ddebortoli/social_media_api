"""
Django REST Framework serializers for the Social Media API.

This module contains serializers for converting model instances to/from JSON,
providing data validation and transformation for the API endpoints.
"""

from rest_framework import serializers
from django.db.models import Prefetch
from django.core.exceptions import ValidationError

from .models import User, Post, Comment


class LimitedUserSerializer(serializers.ModelSerializer):
    """
    Limited user serializer for nested representations.
    
    This serializer provides a minimal user representation for use in
    other serializers to avoid circular dependencies and reduce payload size.
    """
    
    class Meta:
        """Meta configuration for LimitedUserSerializer."""
        model = User
        fields = ['id', 'username']


class CommentSerializer(serializers.ModelSerializer):
    """
    Serializer for Comment model.
    
    Provides full CRUD operations for comments with validation
    and proper relationship handling.
    """
    
    post = serializers.PrimaryKeyRelatedField(read_only=True)
    author = LimitedUserSerializer(read_only=True)

    class Meta:
        """Meta configuration for CommentSerializer."""
        model = Comment
        fields = ['id', 'author', 'post', 'content', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate_content(self, value: str) -> str:
        """
        Validate comment content.
        
        Args:
            value: The comment content to validate
            
        Returns:
            The validated content
            
        Raises:
            ValidationError: If content is empty or too long
        """
        if not value or not value.strip():
            raise ValidationError("Comment content cannot be empty")
        
        if len(value) > 1000:
            raise ValidationError("Comment content cannot exceed 1000 characters")
        
        return value.strip()


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model with basic statistics.
    
    Provides user information along with calculated statistics
    like total posts, comments, and follower counts.
    """
    
    total_posts = serializers.IntegerField(read_only=True)
    total_comments = serializers.IntegerField(read_only=True)
    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()

    class Meta:
        """Meta configuration for UserSerializer."""
        model = User
        fields = [
            'id', 'username', 'email', 'total_posts', 
            'total_comments', 'followers_count', 'following_count'
        ]
        read_only_fields = ['id', 'total_posts', 'total_comments', 
                           'followers_count', 'following_count']

    def get_followers_count(self, obj: User) -> int:
        """
        Get the number of followers for the user.
        
        Args:
            obj: The user instance
            
        Returns:
            Number of followers
        """
        return obj.get_followers_count()

    def get_following_count(self, obj: User) -> int:
        """
        Get the number of users the user is following.
        
        Args:
            obj: The user instance
            
        Returns:
            Number of users being followed
        """
        return obj.get_following_count()

    def validate_username(self, value: str) -> str:
        """
        Validate username.
        
        Args:
            value: The username to validate
            
        Returns:
            The validated username
            
        Raises:
            ValidationError: If username is invalid
        """
        if not value or not value.strip():
            raise ValidationError("Username cannot be empty")
        
        if len(value) < 3:
            raise ValidationError("Username must be at least 3 characters long")
        
        if len(value) > 30:
            raise ValidationError("Username cannot exceed 30 characters")
        
        return value.strip()

    def validate_email(self, value: str) -> str:
        """
        Validate email address.
        
        Args:
            value: The email to validate
            
        Returns:
            The validated email
            
        Raises:
            ValidationError: If email is invalid
        """
        if not value or not value.strip():
            raise ValidationError("Email cannot be empty")
        
        return value.strip().lower()


class UserDetailSerializer(UserSerializer):
    """
    Detailed user serializer with full relationship data.
    
    Extends UserSerializer to include followers and following lists
    for detailed user profile views.
    """
    
    followers = LimitedUserSerializer(many=True, read_only=True)
    following = LimitedUserSerializer(many=True, read_only=True)

    class Meta(UserSerializer.Meta):
        """Meta configuration for UserDetailSerializer."""
        fields = UserSerializer.Meta.fields + ['followers', 'following']


class PostSerializer(serializers.ModelSerializer):
    """
    Serializer for Post model with recent comments.
    
    Provides post information along with the three most recent comments
    and basic author information.
    """
    
    last_three_comments = CommentSerializer(many=True, read_only=True)
    creator_info = LimitedUserSerializer(read_only=True, source='author')
    comments_count = serializers.SerializerMethodField()

    class Meta:
        """Meta configuration for PostSerializer."""
        model = Post
        fields = [
            'id', 'author', 'content', 'created_at', 
            'last_three_comments', 'creator_info', 'comments_count'
        ]
        read_only_fields = ['id', 'created_at', 'last_three_comments', 
                           'creator_info', 'comments_count']

    def get_comments_count(self, obj: Post) -> int:
        """
        Get the number of comments on the post.
        
        Args:
            obj: The post instance
            
        Returns:
            Number of comments
        """
        return obj.get_comments_count()

    def validate_content(self, value: str) -> str:
        """
        Validate post content.
        
        Args:
            value: The post content to validate
            
        Returns:
            The validated content
            
        Raises:
            ValidationError: If content is empty or too long
        """
        if not value or not value.strip():
            raise ValidationError("Post content cannot be empty")
        
        if len(value) > 5000:
            raise ValidationError("Post content cannot exceed 5000 characters")
        
        return value.strip()

    def to_representation(self, instance: Post) -> dict:
        """
        Customize the serialized representation.
        
        Args:
            instance: The post instance to serialize
            
        Returns:
            Dictionary representation with recent comments
        """
        representation = super().to_representation(instance)
        
        # Add recent comments to the representation
        recent_comments = instance.get_recent_comments(limit=3)
        representation['last_three_comments'] = CommentSerializer(
            recent_comments, many=True
        ).data
        
        return representation


class PostDetailExtendedSerializer(PostSerializer):
    """
    Extended post serializer for detailed views.
    
    Provides comprehensive post information including all comments
    and detailed author information.
    """
    
    comments = CommentSerializer(many=True, read_only=True, source='comment_set')
    author_detail = UserSerializer(read_only=True, source='author')

    class Meta(PostSerializer.Meta):
        """Meta configuration for PostDetailExtendedSerializer."""
        fields = PostSerializer.Meta.fields + ['comments', 'author_detail']

    def to_representation(self, instance: Post) -> dict:
        """
        Customize the serialized representation for detailed view.
        
        Args:
            instance: The post instance to serialize
            
        Returns:
            Dictionary representation with all comments
        """
        representation = super().to_representation(instance)
        
        # Add all comments to the representation
        all_comments = instance.comments.order_by('-created_at')
        representation['comments'] = CommentSerializer(
            all_comments, many=True
        ).data
        
        return representation


class FollowUserSerializer(serializers.Serializer):
    """
    Serializer for follow/unfollow operations.
    
    Provides validation and serialization for user following operations.
    """
    
    follower_id = serializers.IntegerField()
    user_to_follow_id = serializers.IntegerField()

    def validate(self, data: dict) -> dict:
        """
        Validate follow operation data.
        
        Args:
            data: The data to validate
            
        Returns:
            The validated data
            
        Raises:
            ValidationError: If the follow operation is invalid
        """
        follower_id = data.get('follower_id')
        user_to_follow_id = data.get('user_to_follow_id')
        
        if follower_id == user_to_follow_id:
            raise ValidationError("Users cannot follow themselves")
        
        # Check if users exist
        try:
            follower = User.objects.get(id=follower_id)
            user_to_follow = User.objects.get(id=user_to_follow_id)
        except User.DoesNotExist:
            raise ValidationError("One or both users not found")
        
        # Check if already following
        if follower.is_following(user_to_follow):
            raise ValidationError("Already following this user")
        
        return data