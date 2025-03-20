from django import forms
from django.contrib.auth.models import User
from .models import Post, Profile
from ckeditor_uploader.widgets import CKEditorUploadingWidget

class PostForm(forms.ModelForm):
    # The content field will automatically use CKEditor because of the model field type,
    # but you can override it if you want a custom configuration
    content = forms.CharField(widget=CKEditorUploadingWidget(config_name='awesome_ckeditor'))
    
    class Meta:
        model = Post
        fields = ['title', 'content', 'featured_image', 'tags', 'status']

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

class ProfileForm(forms.ModelForm):
    birth_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    
    class Meta:
        model = Profile
        fields = ['bio', 'location', 'birth_date', 'profile_picture', 
                 'website', 'twitter', 'github', 'linkedin']
