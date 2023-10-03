from django import forms

from blog.models import Comment, Post


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        widgets = {
            'pub_date': forms.DateTimeInput(
                format='%Y-%m-%d %H:%M:%S', attrs={'type': "datetime-local"}
            ),
        }
        fields = (
            'title', 'text', 'pub_date', 'location', 'category', 'image',
        )


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('text',)
        widgets = {
            'text': forms.Textarea(attrs={'rows': 4, 'cols': 15},),
        }
