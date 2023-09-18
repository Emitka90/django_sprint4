from django import forms

from .models import Comment, Post


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        widgets = {
            'pub_date': forms.DateTimeInput(attrs={'type': "datetime-local"})
        }
        fields = (
            'title', 'text', 'pub_date', 'location', 'category', 'image',
        )


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('text',)
