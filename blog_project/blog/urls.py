from django.urls import path
from . import views

urlpatterns = [
    path('', views.post_list, name='post_list'),
    path('post/new/', views.post_create, name='post_create'),
    path('post/<slug:slug>/', views.post_detail, name='post_detail'),
    path('post/<slug:slug>/edit/', views.post_edit, name='post_edit'),
    path('post/<slug:slug>/delete/', views.post_delete, name='post_delete'),
    
    # Profile URLs - make sure they're in the correct order
    path('profile/edit/', views.edit_profile, name='edit_profile'),  # This should come before the profile/<str:username>/ pattern
    path('profile/', views.profile_view, name='profile'),
    path('profile/<str:username>/', views.profile_view, name='user_profile'),
]