from django.contrib import admin

# Register your models here.
from .models import Post


class PostModelAdmin(admin.ModelAdmin):
    """Customizing the PostModel administration"""
    list_display = ['__str__', 'timestamp', 'updated']
    search_fields = ['title', 'content']

    class Meta:
        """This is just a class container with some options (metadata) attached to the model.
        It defines such things as available permissions, associated database table name,
        whether the model is abstract or not, singular and plural versions of the name etc."""
        model = Post

admin.site.register(Post, PostModelAdmin)
