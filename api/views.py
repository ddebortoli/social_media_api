from rest_framework import generics
from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter

from .models import User, Post, Comment
from .serializers import UserSerializer, PostSerializer, CommentSerializer, UserDetailSerializer, PostDetailExtendedSerializer

class UserListCreate(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = UserSerializer

class UserDetail(generics.RetrieveAPIView):
    queryset = User.objects.annotate(
        total_posts=Count('post'),
        total_comments=Count('comment'),
    ).prefetch_related('followers', 'following')
    serializer_class = UserDetailSerializer
    permission_classes = [IsAuthenticated]

class PostPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

class PostListCreate(ListCreateAPIView):
    queryset = Post.objects.all().order_by('-created_at')
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['author_id', 'created_at']
    pagination_class = PostPagination
    ordering_fields = ['created_at']

    def get_queryset(self):
        queryset = super().get_queryset()
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

class PostDetail(generics.RetrieveAPIView):
    queryset = Post.objects.all()  
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

class PostDetailExtended(generics.RetrieveAPIView):
    queryset = Post.objects.all()
    serializer_class = PostDetailExtendedSerializer
    permission_classes = [IsAuthenticated]

class CommentListCreate(generics.ListCreateAPIView):
    queryset = Comment.objects.select_related('author', 'post')
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        post_id = self.kwargs['pk']
        post = get_object_or_404(Post, pk=post_id)
        serializer.save(author_id=self.request.user.id, post=post)

class CommentDetail(generics.RetrieveAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

class FollowUser(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id, follow_id):
        try:
            user = User.objects.get(id=id)
            user_to_follow = User.objects.get(id=follow_id)
            user.followers.add(user_to_follow)
            return Response({"message": f"{user.username} is now following {user_to_follow.username}"}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)