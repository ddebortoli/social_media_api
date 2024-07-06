from django.urls import path
from .views import UserListCreate, UserDetail, PostListCreate, CommentListCreate, FollowUser, PostDetailExtended
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('users/', UserListCreate.as_view(), name='user-list'),
    path('users/<int:pk>/', UserDetail.as_view(), name='user-detail'),
    path('users/<int:id>/follow/<int:follow_id>/', FollowUser.as_view(), name='user-follow'),
    path('posts/', PostListCreate.as_view(), name='post-list'),
    path('posts/<int:pk>/', PostDetailExtended.as_view(), name='post-detail'),
    path('posts/<int:pk>/comments/', CommentListCreate.as_view(), name='comment-list'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh')
]
