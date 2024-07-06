from rest_framework import serializers
from .models import User, Post, Comment
from django.db.models import Prefetch

class LimitedUserSerializer(serializers.ModelSerializer):  
    class Meta:
        model = User
        fields = ['id', 'username']

class CommentSerializer(serializers.ModelSerializer):
    post = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'author', 'post', 'content', 'created_at']

class UserSerializer(serializers.ModelSerializer):
    total_posts = serializers.IntegerField(read_only=True)
    total_comments = serializers.IntegerField(read_only=True)
    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'total_posts', 'total_comments', 'followers_count', 'following_count']


    def get_followers_count(self, obj):
        return obj.followers.count()

    def get_following_count(self, obj):
        return obj.following.count()

class UserDetailSerializer(serializers.ModelSerializer):
    total_posts = serializers.IntegerField(read_only=True)
    total_comments = serializers.IntegerField(read_only=True)
    followers = LimitedUserSerializer(many=True, read_only=True)
    following = LimitedUserSerializer(many=True, read_only=True)
    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'total_posts', 'total_comments', 'followers', 'following', 'followers_count', 'following_count']

    def get_followers_count(self, obj):
        return obj.followers.count()

    def get_following_count(self, obj):
        return obj.following.count()

class PostSerializer(serializers.ModelSerializer):
    last_three_comments = CommentSerializer(many=True, read_only=True)
    creator_info = LimitedUserSerializer(read_only=True) 

    class Meta:
        model = Post
        fields = ['id', 'author', 'content', 'created_at', 'last_three_comments', 'creator_info']

    def get_queryset(self):
        comments_prefetch = Prefetch(
            'comments', 
            queryset=Comment.objects.order_by('-created_at')[:3], 
            to_attr='last_three_comments'
        )
        return Post.objects.prefetch_related(comments_prefetch, 'author')

class PostDetailExtendedSerializer(serializers.ModelSerializer):
    last_three_comments = CommentSerializer(many=True, read_only=True, source='comment_set')  
    creator_info = UserSerializer(read_only=True, source='author') 

    class Meta:
        model = Post
        fields = ['id', 'author', 'content', 'created_at', 'last_three_comments', 'creator_info']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Filtrar y ordenar los comentarios en la representación
        representation['last_three_comments'] = CommentSerializer(
            instance.comment_set.order_by('-created_at')[:3], many=True
        ).data
        return representation