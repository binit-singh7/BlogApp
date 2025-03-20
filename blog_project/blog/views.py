from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Count
from .models import Post, Profile
from .forms import PostForm, UserForm, ProfileForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate

# List of blog posts
def post_list(request):
    posts = Post.objects.all()
    return render(request, 'blog/post_list.html', {'posts': posts})

# Detail of a single post
def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug)
    # Increment view count
    post.views += 1
    post.save()
    
    # You might want to add related posts or comments here
    context = {
        'post': post,
    }
    return render(request, 'blog/post_detail.html', context)

# Create a new post
@login_required
def post_create(request):
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.created_date = timezone.now()
            if post.status == 'published':
                post.published_date = timezone.now()
            post.save()
            return redirect('post_detail', slug=post.slug)  # Use slug instead of pk
    else:
        form = PostForm()
    return render(request, 'blog/post_create.html', {'form': form})

# Update an existing post
@login_required
def post_edit(request, slug):
    post = get_object_or_404(Post, slug=slug)
    # Check if the user is the author
    if post.author != request.user and not request.user.is_staff:
        return redirect('post_detail', slug=post.slug)
        
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            if post.status == 'published' and not post.published_date:
                post.published_date = timezone.now()
            post.save()
            return redirect('post_detail', slug=post.slug)
    else:
        form = PostForm(instance=post)
    return render(request, 'blog/post_create.html', {'form': form})

# Delete a post
@login_required
def post_delete(request, slug):
    post = get_object_or_404(Post, slug=slug)
    # Check if the user is the author
    if post.author != request.user and not request.user.is_staff:
        return redirect('post_detail', slug=post.slug)
        
    if request.method == "POST":
        post.delete()
        return redirect('post_list')
    return render(request, 'blog/post_confirm_delete.html', {'post': post})

# Register a new user
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('post_list')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

# Add these profile views to your existing views
@login_required
def profile_view(request, username=None):
    if username:
        user = get_object_or_404(User, username=username)
    else:
        user = request.user
    
    # Ensure the user has a profile
    profile, created = Profile.objects.get_or_create(user=user)
    
    # Get user's posts
    posts = Post.objects.filter(author=user).order_by('-created_date')
    
    # Get user's likes
    liked_posts = Post.objects.filter(likes=user).order_by('-created_date')
    
    # Get post statistics
    post_count = posts.count()
    published_count = posts.filter(status='published').count()
    draft_count = posts.filter(status='draft').count()
    total_views = sum(post.views for post in posts)
    total_likes = sum(post.likes.count() for post in posts)
    
    context = {
        'profile_user': user,
        'posts': posts,
        'liked_posts': liked_posts,
        'post_count': post_count,
        'published_count': published_count,
        'draft_count': draft_count,
        'total_views': total_views,
        'total_likes': total_likes,
        'is_own_profile': user == request.user,
    }
    
    return render(request, 'blog/profile.html', context)

@login_required
def edit_profile(request):
    # Ensure the user has a profile
    profile, created = Profile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile was successfully updated!')
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = ProfileForm(instance=profile)
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }
    
    return render(request, 'blog/profile_edit.html', context)