from django import forms
from .models import Post

#Form for post
class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["image", "description"]
