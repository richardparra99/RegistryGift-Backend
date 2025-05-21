from rest_framework.routers import DefaultRouter
from registry.api import UserViewSet, EventViewSet, CommentViewSet, GiftViewSet


router = DefaultRouter()
router.register(r'auth', UserViewSet, basename='auth')
router.register(r'events', EventViewSet, basename='event')
router.register(r'comments', CommentViewSet, basename='comment')
router.register(r'gifts', GiftViewSet, basename='gift')

urlpatterns = router.urls