from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)

from blog.forms import CommentForm, PostForm
from blog.mixin import CommentMixin, PostDispatchMixin, PostMixin, PostsMixin
from blog.models import Category, Comment, Post, User


class IndexListView(PostsMixin, ListView):
    ''' Главная страница '''
    template_name = 'blog/index.html'


class CategoryListView(PostsMixin, ListView):
    ''' Список постов по категориям '''
    template_name = 'blog/category.html'

    def get_queryset(self):
        return super().get_queryset().filter(
            category__slug=self.kwargs['category_slug']
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True
        )
        return context


class ProfileListView(PostsMixin, ListView):
    ''' Страница профиля '''
    template_name = 'blog/profile.html'

    def get_queryset(self):
        ''' Проверяет кто просматривает страницу пользователя. '''
        if self.request.user.username == self.kwargs['username']:
            return Post.objects.filter(
                author__username=self.kwargs['username'],
            ).annotate(
                comment_count=Count('comments')
            ).order_by('-pub_date')
        else:
            return super().get_queryset().filter(
                author__username=self.kwargs['username']
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
    fields = ('username', 'last_name', 'first_name', 'email')

    def get_object(self, queryset=None):
        return self.request.user

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
        get_object_or_404(Post.objects.filter(
            Q(pub_date__lte=timezone.now(),
              is_published=True,
              category__is_published=True)
            | Q(author__username=request.user.username)), pk=kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.get_object().comments.all()
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
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        return super().form_valid(form)


class CommentUpdateView(LoginRequiredMixin, CommentMixin, UpdateView):
    ''' Редактирование комментария '''
    form_class = CommentForm


class CommentDeleteView(LoginRequiredMixin, CommentMixin, DeleteView):
    ''' Удаление комментария '''

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )
