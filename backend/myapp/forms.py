from django import forms
from .models import Blog

class BlogForm(forms.ModelForm):
    class Meta:
        model = Blog
        fields = ['title', 'excerpt', 'content', 'author', 'category', 'is_premium', 'price', 'image', 'status']