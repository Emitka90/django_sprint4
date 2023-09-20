from django.contrib import admin

from .models import Category, Location, Post, Comment


class PostInline(admin.StackedInline):
    model = Post
    extra = 0


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


admin.site.register(Category, CategoryAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.empty_value_display = 'Не задано'
