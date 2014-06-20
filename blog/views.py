from django.shortcuts import render
from rest_framework import viewsets

import restframework_flat
from blog.models import Post, Comment
from blog.serializers import PostSerializer, CommentSerializer


def index(request):
    return render(request, 'blog/index.html')


class PostViewSet(restframework_flat.FlatViewSetMixin,
                  viewsets.ModelViewSet):
    serializer_class = PostSerializer
    queryset = Post.objects.all()
    sideload_relations = [
        ('comments', CommentSerializer)
    ]


class CommentViewSet(restframework_flat.FlatViewSetMixin,
                     viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    queryset = Comment.objects.all()
    paginate_by = 3
    sideload_relations = [
        ('post', PostSerializer)
    ]
