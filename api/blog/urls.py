from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.blog_home, name='home'),
    path('<int:post_id>/', views.blog_detail, name='detail'),
]