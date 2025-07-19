"""
URL configuration for the Social Media API.

This module defines the URL patterns for all API endpoints,
including authentication, user management, posts, and comments.
"""

from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    UserListCreateView, UserDetailView, PostListCreateView, 
    CommentListCreateView, FollowUserView, PostDetailExtendedView,
    PostDetailView, CommentDetailView, UserStatsView
)

app_name = 'api'

urlpatterns = [
    # Authentication endpoints
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # User management endpoints
    path('users/', UserListCreateView.as_view(), name='user-list'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='user-detail'),
    path('users/<int:pk>/stats/', UserStatsView.as_view(), name='user-stats'),
    path('users/<int:id>/follow/<int:follow_id>/', FollowUserView.as_view(), name='user-follow'),
    
    # Post management endpoints
    path('posts/', PostListCreateView.as_view(), name='post-list'),
    path('posts/<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('posts/<int:pk>/extended/', PostDetailExtendedView.as_view(), name='post-detail-extended'),
    path('posts/<int:pk>/comments/', CommentListCreateView.as_view(), name='comment-list'),
    
    # Comment management endpoints
    path('comments/<int:pk>/', CommentDetailView.as_view(), name='comment-detail'),
]
