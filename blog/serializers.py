from rest_framework import serializers

import restframework_flat
from blog.models import Post, Comment


class PostSerializer(restframework_flat.FlatSerializerMixin,
                     serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ('id', 'title', 'text', 'comments')


class CommentSerializer(restframework_flat.FlatSerializerMixin,
                        serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('id', 'text', 'n_likes', 'post')