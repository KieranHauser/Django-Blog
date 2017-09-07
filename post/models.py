from django.db import models
from django.conf import settings
from django.core.urlresolvers import reverse
from django.db.models.signals import pre_save
from django.utils.safestring import mark_safe
from django.utils.text import slugify
from django.utils import timezone

from markdown_deux import markdown
# Create your models here.

class PostManager(models.Manager):
    # A way to control how models work
    # Post.objects.all()
    # Post.objects.create() are both types of model managers
    def active(self, *args, **kwargs):
        return super(PostManager, self).filter(draft=False).filter(publish__lte=timezone.now())


def upload_location(instance, filename):
    return "{}/{}".format(instance.id, filename)


class Post(models.Model):
    """Python class, each instance is an object for a post with title, content, updated and timestamp
    Attributes
    @:type title: CharField
    @:type content: TextField
    @:type updated: DateTimeField
    @:type timestamp: DateTimeField
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, default=1)
    title = models.CharField(max_length=120)
    slug = models.SlugField(unique=True)
    image = models.ImageField(upload_to=upload_location,
                              null=True,
                              blank=True,
                              width_field='width_field',
                              height_field='height_field')
    height_field = models.IntegerField(default=0)
    width_field = models.IntegerField(default=0)
    content = models.TextField()
    draft = models.BooleanField(default=False)
    publish = models.DateField(auto_now=False, auto_now_add=False)
    updated = models.DateTimeField(auto_now=True, auto_now_add=False)
    timestamp = models.DateTimeField(auto_now=False, auto_now_add=True)

    objects = PostManager()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        """Returns the URL for the detail view of the object
        :rtype: str
        """
        return reverse('blog:detail', kwargs={'id': self.id})
        # return "/blog/{}/".format(self.id)

    class Meta:
        ordering = ['-timestamp', '-updated']

    def get_markdown(self):
        content = self.content
        markdown_content = markdown(content)
        return mark_safe(markdown_content)

def create_slug(instance, new_slug=None):
    slug = slugify(instance.title)
    if new_slug:
        slug = new_slug
    qs = Post.objects.filter(slug=slug).order_by("-id")
    exists = qs.exists()
    if exists:
        new_slug = "{}-{}".format(slug, qs.first().id)
        return create_slug(instance, new_slug=new_slug)
    return slug

def pre_save_post_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = create_slug(instance)


pre_save.connect(pre_save_post_receiver, sender=Post)
