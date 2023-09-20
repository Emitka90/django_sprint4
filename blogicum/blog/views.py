from django.views.generic import (
    ListView, CreateView, UpdateView, DeleteView, DetailView
)
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.utils import timezone
from django.db.models import Q

from .models import Post, Category, User, Comment
from .forms import CommentForm, PostForm


class PostDispatchMixin:
    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(Post, pk=kwargs['post_id'])
        if instance.author != request.user:
            return redirect('blog:post_detail', kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)


class PostPaginateMixin:
    model = Post
    paginate_by = 10


class PostMixin:
    model = Post
    pk_url_kwarg = 'post_id'
    template_name = 'blog/create.html'


class CommentMixin:
    model = Comment
    pk_url_kwarg = 'comment_id'
    template_name = 'blog/comment.html'


class IndexListView(PostPaginateMixin, ListView):
    template_name = 'blog/index.html'

    def get_queryset(self):
        return Post.objects.filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now()
        )


class CategoryListView(PostPaginateMixin, ListView):
    ''' Список постов по категориям '''
    template_name = 'blog/category.html'

    def get_queryset(self):
        return Post.objects.filter(
            category__slug=self.kwargs['category_slug'],
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now()
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True
        )
        return context


class ProfileListView(PostPaginateMixin, ListView):
    ''' Страница профиля '''
    template_name = 'blog/profile.html'

    def get_queryset(self):
        # Проверяет кто просматривает страницу пользователя.
        # Если зашел сам автор, то выводятся все публикации, опубликованные им.
        if self.request.user.username == self.kwargs['username']:
            return Post.objects.filter(
                author__username=self.kwargs['username'],
            )
        else:
            return Post.objects.filter(
                author__username=self.kwargs['username'],
                is_published=True,
                category__is_published=True,
                pub_date__lte=timezone.now()
            )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = get_object_or_404(
            User, username=self.kwargs['username']
        )
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    ''' Редактирование профиля '''
    model = User
    template_name = 'blog/user.html'
    slug_field = 'username'
    slug_url_kwarg = 'username'
    fields = ('username', 'last_name', 'first_name', 'email')

    def get_success_url(self):
        return reverse('blog:profile', kwargs={'username': self.request.user})


class PostCreateView(LoginRequiredMixin, PostMixin, CreateView):
    ''' Добавление новой публикации '''
    form_class = PostForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostDetailView(PostMixin, DetailView):
    ''' Страница отдельной публикации '''
    template_name = 'blog/detail.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            get_object_or_404(Post.objects.filter(
                Q(Q(Q(pub_date__lte=timezone.now())
                    & Q(is_published=True)
                    & Q(category__is_published=True))
                    & ~Q(author=request.user))
                | Q(author=request.user)
                ), pk=kwargs['post_id'])
        else:
            get_object_or_404(Post.objects.filter(
                Q(pub_date__lte=timezone.now())
                & Q(is_published=True)
                & Q(category__is_published=True)), pk=kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = Comment.objects.filter(
            post_id=self.kwargs['post_id']
        )
        return context


class PostUpdateView(
    LoginRequiredMixin, PostMixin, PostDispatchMixin, UpdateView
):
    ''' Редактирование публикации '''
    form_class = PostForm

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'post_id': self.object.pk})


class PostDeleteView(
    LoginRequiredMixin, PostMixin, PostDispatchMixin, DeleteView
):
    ''' Удаление публикации '''

    def get_success_url(self):
        return reverse('blog:profile', kwargs={'username': self.request.user})


class CommentCreateView(LoginRequiredMixin, CreateView):
    ''' Добавление комментария '''

    model = Comment
    form_class = CommentForm
    template_name = 'includes/comments.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        return super().form_valid(form)


class CommentUpdateView(LoginRequiredMixin, CommentMixin, UpdateView):
    ''' Редактирование комментария '''
    form_class = CommentForm

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(
            Comment,
            pk=self.kwargs['comment_id'],
            post_id=self.kwargs['post_id'],
        )
        if instance.author != request.user:
            raise Http404
        return super().dispatch(request, *args, **kwargs)


class CommentDeleteView(LoginRequiredMixin, CommentMixin, DeleteView):
    ''' Удаление комментария '''

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(
            Comment,
            pk=self.kwargs['comment_id'],
            post_id=self.kwargs['post_id'],
        )
        if instance.author != request.user:
            raise Http404
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )
