# blog/serializers.py
from rest_framework import serializers
from .models import Post, Category, Comment
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'created_at']

class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    
    class Meta:
        model = Comment
        fields = ['id', 'post', 'author', 'content', 'created_at', 'is_approved']
        read_only_fields = ['author', 'created_at']

class PostSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True, required=False)
    comments = CommentSerializer(many=True, read_only=True)
    comment_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = [
            'id', 'title', 'slug', 'author', 'category', 'category_id',
            'content', 'excerpt', 'featured_image', 'status',
            'created_at', 'updated_at', 'published_at',
            'comments', 'comment_count'
        ]
        read_only_fields = ['author', 'created_at', 'updated_at', 'published_at']
    
    def get_comment_count(self, obj):
        return obj.comments.filter(is_approved=True).count()

class PostListSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    comment_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = [
            'id', 'title', 'slug', 'author', 'category',
            'excerpt', 'featured_image', 'status',
            'created_at', 'published_at', 'comment_count'
        ]
    
    def get_comment_count(self, obj):
        return obj.comments.filter(is_approved=True).count()