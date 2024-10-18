from django.contrib import admin
from MainApp.models import Snippet, Comment

# 1 variant
# admin.site.register([Snippet, Comment])


# 2 variant
@admin.register(Snippet)
class SnippetAdmin(admin.ModelAdmin):
    list_display = ["name", "lang", "creation_date", "public", "code"]
    list_filter = ["lang", "creation_date"]
    ordering = ["creation_date"]
    search_fields = ["name", "code"]
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ["text"]
    search_fields = ["text"]