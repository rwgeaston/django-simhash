from rest_framework.routers import DefaultRouter

from .views import HashViewSet

router = DefaultRouter()
router.register(r'hashes', HashViewSet)

urlpatterns = router.urls
