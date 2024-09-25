from django import forms
from .models import Post, Comment


class PostCreateForm(forms.ModelForm):
    class Meta:
        model = Post
        exclude = ['author']
        widgets = {
            'pub_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'})
        }

class CommentCreateForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']