# blog/views.py
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
# Robust import for DjangoFilterBackend: different django-filter versions expose
# the backend in different module paths. Import the package dynamically to
# avoid static import issues in environments where django_filters may not be
# available to the linter.
import importlib

django_filters = importlib.import_module('django_filters')
for sub in ('rest_framework', 'backends'):
    mod = getattr(django_filters, sub, None)
    if mod is not None and hasattr(mod, 'DjangoFilterBackend'):
        DjangoFilterBackend = getattr(mod, 'DjangoFilterBackend')
        break
else:
    raise ImportError('DjangoFilterBackend could not be imported from django_filters')

from blog_project.accounts import models
from blog.models import Post, Category, Comment
from blog.serializers import (
    PostSerializer, PostListSerializer,
    CategorySerializer, CommentSerializer
)
from .permissions import IsAuthorOrReadOnly

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.filter(status='published')
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'author', 'status']
    search_fields = ['title', 'content', 'excerpt']
    ordering_fields = ['created_at', 'published_at', 'title']
    lookup_field = 'slug'
    
    def get_serializer_class(self):
        if self.action == 'list':
            return PostListSerializer
        return PostSerializer
    
    def get_queryset(self):
        # Allow authors to see their own drafts
        if self.request.user.is_authenticated:
            return Post.objects.filter(
                models.Q(status='published') | 
                models.Q(author=self.request.user)
            )
        return Post.objects.filter(status='published')
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_posts(self, request):
        posts = Post.objects.filter(author=request.user)
        serializer = self.get_serializer(posts, many=True)
        return Response(serializer.data)

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.filter(is_approved=True)
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        queryset = Comment.objects.all()
        post_id = self.request.query_params.get('post', None)
        if post_id:
            queryset = queryset.filter(post_id=post_id)
        
        # Only show approved comments to non-staff
        if not self.request.user.is_staff:
            queryset = queryset.filter(is_approved=True)
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)