from django.db import models


class Post(models.Model):
    title = models.CharField(max_length=100)
    text = models.TextField()


class Comment(models.Model):
    post = models.ForeignKey('blog.Post', related_name='comments')
    text = models.TextField()
    n_likes = models.IntegerField(default=0)