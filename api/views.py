"""
Django REST Framework views for the Social Media API.

This module contains view classes that handle HTTP requests and responses,
integrating with the service layer for business logic and repositories for data access.
"""

from rest_framework import generics, status
from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django.db.models import Count

from .models import User, Post, Comment
from .serializers import (
    UserSerializer, PostSerializer, CommentSerializer, 
    UserDetailSerializer, PostDetailExtendedSerializer, FollowUserSerializer
)
from .services import UserService, PostService, CommentService


class UserListCreateView(generics.ListCreateAPIView):
    """
    View for listing and creating users.
    
    Provides endpoints for:
    - GET: List all users with basic information
    - POST: Create a new user account
    """
    
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['username', 'email']
    ordering_fields = ['username', 'date_joined']
    ordering = ['username']

    def get_queryset(self):
        """
        Get the queryset for user listing.
        
        Returns:
            QuerySet of users with annotations for statistics
        """
        return User.objects.annotate(
            total_posts=Count('posts'),
            total_comments=Count('comments'),
        )

    def perform_create(self, serializer):
        """
        Create a new user using the service layer.
        
        Args:
            serializer: The validated serializer instance
        """
        user_service = UserService()
        try:
            user_data = serializer.validated_data
            user_service.create_user(user_data)
        except ValidationError as e:
            raise ValidationError(str(e))


class UserDetailView(generics.RetrieveAPIView):
    """
    View for retrieving detailed user information.
    
    Provides endpoint for:
    - GET: Retrieve detailed user information with followers/following lists
    """
    
    queryset = User.objects.annotate(
        total_posts=Count('posts'),
        total_comments=Count('comments'),
    ).prefetch_related('followers', 'following')
    serializer_class = UserDetailSerializer
    permission_classes = [IsAuthenticated]


class PostPagination(PageNumberPagination):
    """Custom pagination for posts."""
    
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class PostListCreateView(ListCreateAPIView):
    """
    View for listing and creating posts.
    
    Provides endpoints for:
    - GET: List posts with filtering and pagination
    - POST: Create a new post
    """
    
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['author_id', 'created_at']
    pagination_class = PostPagination
    ordering_fields = ['created_at', 'author__username']
    ordering = ['-created_at']

    def get_queryset(self):
        """
        Get filtered queryset for posts.
        
        Returns:
            QuerySet of posts with applied filters
        """
        queryset = Post.objects.select_related('author').prefetch_related('comments')
        
        # Apply custom filters
        author_id = self.request.query_params.get('author_id')
        from_date = self.request.query_params.get('from_date')
        to_date = self.request.query_params.get('to_date')

        if author_id:
            queryset = queryset.filter(author_id=author_id)
        if from_date:
            queryset = queryset.filter(created_at__gte=from_date)
        if to_date:
            queryset = queryset.filter(created_at__lte=to_date)

        return queryset

    def perform_create(self, serializer):
        """
        Create a new post using the service layer.
        
        Args:
            serializer: The validated serializer instance
        """
        post_service = PostService()
        try:
            content = serializer.validated_data['content']
            author_id = self.request.user.id
            post_service.create_post(author_id=author_id, content=content)
        except ValidationError as e:
            raise ValidationError(str(e))


class PostDetailView(generics.RetrieveAPIView):
    """
    View for retrieving detailed post information.
    
    Provides endpoint for:
    - GET: Retrieve post with recent comments
    """
    
    queryset = Post.objects.select_related('author').prefetch_related('comments')
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]


class PostDetailExtendedView(generics.RetrieveAPIView):
    """
    View for retrieving extended post information.
    
    Provides endpoint for:
    - GET: Retrieve post with all comments and detailed author info
    """
    
    queryset = Post.objects.select_related('author').prefetch_related('comments')
    serializer_class = PostDetailExtendedSerializer
    permission_classes = [IsAuthenticated]


class CommentListCreateView(generics.ListCreateAPIView):
    """
    View for listing and creating comments on a post.
    
    Provides endpoints for:
    - GET: List comments for a specific post
    - POST: Create a new comment on a post
    """
    
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [OrderingFilter]
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        """
        Get comments for a specific post.
        
        Returns:
            QuerySet of comments for the post
        """
        post_id = self.kwargs['pk']
        return Comment.objects.filter(post_id=post_id).select_related('author', 'post')

    def perform_create(self, serializer):
        """
        Create a new comment using the service layer.
        
        Args:
            serializer: The validated serializer instance
        """
        comment_service = CommentService()
        try:
            post_id = self.kwargs['pk']
            content = serializer.validated_data['content']
            author_id = self.request.user.id
            
            comment_service.create_comment(
                author_id=author_id,
                post_id=post_id,
                content=content
            )
        except ValidationError as e:
            raise ValidationError(str(e))


class CommentDetailView(generics.RetrieveAPIView):
    """
    View for retrieving comment details.
    
    Provides endpoint for:
    - GET: Retrieve specific comment information
    """
    
    queryset = Comment.objects.select_related('author', 'post')
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]


class FollowUserView(APIView):
    """
    View for following/unfollowing users.
    
    Provides endpoints for:
    - POST: Follow a user
    - DELETE: Unfollow a user
    """
    
    permission_classes = [IsAuthenticated]

    def post(self, request, id: int, follow_id: int):
        """
        Follow a user.
        
        Args:
            request: The HTTP request
            id: The ID of the user who wants to follow
            follow_id: The ID of the user to be followed
            
        Returns:
            Response with follow operation result
        """
        user_service = UserService()
        try:
            result = user_service.follow_user(
                follower_id=id,
                user_to_follow_id=follow_id
            )
            return Response(
                {"message": result['message']}, 
                status=status.HTTP_200_OK
            )
        except ValidationError as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"error": "An unexpected error occurred"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def delete(self, request, id: int, follow_id: int):
        """
        Unfollow a user.
        
        Args:
            request: The HTTP request
            id: The ID of the user who wants to unfollow
            follow_id: The ID of the user to be unfollowed
            
        Returns:
            Response with unfollow operation result
        """
        user_service = UserService()
        try:
            result = user_service.unfollow_user(
                follower_id=id,
                user_to_unfollow_id=follow_id
            )
            return Response(
                {"message": result['message']}, 
                status=status.HTTP_200_OK
            )
        except ValidationError as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"error": "An unexpected error occurred"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UserStatsView(APIView):
    """
    View for retrieving user statistics.
    
    Provides endpoint for:
    - GET: Retrieve comprehensive user statistics
    """
    
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id: int):
        """
        Get user statistics.
        
        Args:
            request: The HTTP request
            user_id: The ID of the user
            
        Returns:
            Response with user statistics
        """
        user_service = UserService()
        try:
            stats = user_service.get_user_with_stats(user_id)
            if not stats:
                return Response(
                    {"error": "User not found"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            return Response({
                "user_id": stats['user'].id,
                "username": stats['user'].username,
                "total_posts": stats['total_posts'],
                "total_comments": stats['total_comments'],
                "followers_count": stats['followers_count'],
                "following_count": stats['following_count']
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": "An unexpected error occurred"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )