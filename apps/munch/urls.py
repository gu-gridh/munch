"""API routes for the Edvard Munch annotation backend."""

from django.urls import include, path
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r"panel", views.ArtworkViewSet)
router.register(r"artists", views.ArtistViewSet)
router.register(r"materials", views.MaterialViewSet)
router.register(r"techniques", views.TechniqueViewSet)
router.register(r"painting-images", views.ImageViewSet)
router.register(r"meshes", views.MeshViewSet)
router.register(r"documents", views.PaintingDocumentViewSet)
router.register(r"annotation-categories", views.AnnotationCategoryViewSet)
router.register(r"tags", views.TagViewSet)
router.register(r"years", views.YearViewSet)
router.register(r"visual-annotations", views.VisualAnnotationViewSet)
router.register(r"annotation", views.AnnoationViewSet, basename="annotation")  # Alias for visual annotations       

urlpatterns = [
    path("api/", include(router.urls)),
]
