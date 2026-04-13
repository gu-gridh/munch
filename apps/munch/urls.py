"""API routes for the Edvard Munch annotation backend."""

from django.urls import include, path
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r"paintings", views.PaintingObjectViewSet)
router.register(r"painting-images", views.ImageViewSet)
router.register(r"meshes", views.MeshViewSet)
router.register(r"painting-documents", views.PaintingDocumentViewSet)
router.register(r"annotation-categories", views.AnnotationCategoryViewSet)
router.register(r"tags", views.TagViewSet)
router.register(r"visual-annotations", views.VisualAnnotationViewSet)

urlpatterns = [
    path("api/munch/", include(router.urls)),
]
