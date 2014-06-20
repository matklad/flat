from django.conf.urls import url, include
from rest_framework.routers import SimpleRouter

from blog.views import PostViewSet, CommentViewSet, index


router = SimpleRouter(trailing_slash=False)
router.register('posts', PostViewSet, base_name='post')
router.register('comments', CommentViewSet, base_name='comment')

urlpatterns = (
    url('^$', index),
    url('^api/', include(router.urls)),
)
