from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import UserViewSet

router_v1 = SimpleRouter()

router_v1.register('users', UserViewSet, basename='users')

urlpatterns = [
    path('api/', include(router_v1.urls)),
    path('api/auth/', include('djoser.urls.authtoken'))
]
