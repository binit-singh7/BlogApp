from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.text import slugify
from ckeditor_uploader.fields import RichTextUploadingField  # Import the rich text field
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.management.base import BaseCommand

class Post(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published')
    )

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_posts')
    content = RichTextUploadingField()  # Replace TextField with RichTextUploadingField
    featured_image = models.ImageField(upload_to='blog_images/', blank=True, null=True)
    created_date = models.DateTimeField(default=timezone.now)
    published_date = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    views = models.PositiveIntegerField(default=0)
    likes = models.ManyToManyField(User, related_name='blog_likes', blank=True)
    tags = models.CharField(max_length=100, blank=True, help_text='Comma-separated tags')

    class Meta:
        ordering = ['-published_date']

    def publish(self):
        self.published_date = timezone.now()
        self.status = 'published'
        self.save()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post_detail', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        
        # Check if slug exists and make it unique if needed
        original_slug = self.slug
        counter = 1
        while Post.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
            self.slug = f"{original_slug}-{counter}"
            counter += 1
        
        super().save(*args, **kwargs)

    def total_likes(self):
        return self.likes.count()

# Add this Profile model to your existing models
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=100, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    website = models.URLField(max_length=200, blank=True)
    twitter = models.CharField(max_length=100, blank=True)
    github = models.CharField(max_length=100, blank=True)
    linkedin = models.CharField(max_length=100, blank=True)
    joined_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username}'s profile"

# Signal to create/update profile when a user is created/updated
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        # Ensure the profile exists even for existing users
        Profile.objects.get_or_create(user=instance)

class Command(BaseCommand):
    help = 'Creates profile objects for all users without one'

    def handle(self, *args, **options):
        users_without_profile = []
        
        for user in User.objects.all():
            try:
                # Check if profile exists
                profile = user.profile
            except Profile.DoesNotExist:
                # Create profile if it doesn't exist
                users_without_profile.append(user)
                Profile.objects.create(user=user)
        
        if users_without_profile:
            self.stdout.write(self.style.SUCCESS(f'Created profiles for {len(users_without_profile)} users'))
        else:
            self.stdout.write(self.style.SUCCESS('All users already have profiles'))