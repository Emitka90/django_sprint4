from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone

from blog.models import Comment, Post


class CommentMixin:
    model = Comment
    pk_url_kwarg = 'comment_id'
    template_name = 'blog/comment.html'

    def dispatch(self, request, *args, **kwargs):
        get_object_or_404(
            Comment,
            pk=self.kwargs['comment_id'],
            post_id=self.kwargs['post_id'],
            author__username=request.user.username
        )
        return super().dispatch(request, *args, **kwargs)


class PostDispatchMixin:

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(Post, pk=kwargs['post_id'])
        if instance.author != request.user:
            return redirect('blog:post_detail', kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)


class PostMixin:
    model = Post
    pk_url_kwarg = 'post_id'
    template_name = 'blog/create.html'


class PostsMixin:
    model = Post
    paginate_by = 10

    def get_queryset(self):
        return Post.objects.filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now()
        ).annotate(
            comment_count=Count('comments')
            ).order_by('-pub_date')
