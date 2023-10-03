from django.contrib import admin

from blog.models import Category, Comment, Location, Post


class PostInline(admin.StackedInline):
    model = Post
    extra = 0


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    inlines = (
        PostInline,
    )
    list_display = (
        'title',
        'description',
        'slug',
        'is_published'
    )
    list_editable = (
        'is_published',
    )
    search_fields = (
        'title',
        'slug'
    )
    list_display_links = ('title',)
    list_per_page = 10


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    inlines = (
        PostInline,
    )
    list_display = (
        'name',
        'is_published'
    )
    list_editable = (
        'is_published',
    )
    search_fields = (
        'name',
    )
    list_display_links = ('name',)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'author',
        'category',
        'location',
        'is_published',
        'pub_date'
    )
    list_editable = (
        'category',
        'location',
        'is_published',
    )
    search_fields = ('title',)
    list_filter = (
        'author',
        'category',
        'location'
    )
    list_display_links = ('title',)
    list_per_page = 10


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'text',
        'author',
        'post'
    )
    list_filter = (
        'author',
        'post',
    )
    search_fields = (
        'text',
    )
    list_per_page = 10


admin.site.empty_value_display = 'Не задано'
