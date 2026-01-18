from django.urls import path, include
from rest_framework import routers
from .views import TemplateTrainViewSet, DocumentCreateViewSet, TemplateMetadataViewSet


router = routers.DefaultRouter()
router.register(r'template-train', TemplateTrainViewSet, basename='template-train')
router.register(r'get-template-metadata', TemplateMetadataViewSet, basename='get-template-metadata')
router.register(r'create-document', DocumentCreateViewSet, basename='create-document')


urlpatterns = [
    path('', include(router.urls)),
]