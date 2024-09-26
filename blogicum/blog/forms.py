from django import forms
from .models import Post, Comment


class PostCreateForm(forms.ModelForm):
    class Meta:
        model = Post
        # Exclude the author field as it will be set programmatically
        exclude = ['author']
        # Use a datetime-local input for the publication date
        widgets = {
            'pub_date': forms.DateTimeInput(attrs={'class': 'form-control',
                                                   'type': 'datetime-local'})
        }


class CommentCreateForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']  # only the text field will be used in the form
