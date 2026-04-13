"""Viewsets for the Edvard Munch annotation backend."""

from rest_framework import filters
from rest_framework.decorators import action
from rest_framework.response import Response

from munch.abstract.views import DynamicDepthViewSet

from .models import (
    AnnotationCategory,
    Mesh,
    PaintingDocument,
    PaintingImage,
    PaintingObject,
    Tag,
    VisualAnnotation,
)
from .serializers import (
    AnnotationCategorySerializer,
    MeshSerializer,
    PaintingDocumentSerializer,
    PaintingImageSerializer,
    PaintingObjectSerializer,
    TagSerializer,
    VisualAnnotationSerializer,
)


SEARCH_AND_FILTER = DynamicDepthViewSet.filter_backends + [
    filters.SearchFilter,
    filters.OrderingFilter,
]


class PaintingObjectViewSet(DynamicDepthViewSet):
    """API endpoint for painting metadata and nested annotation resources."""

    queryset = PaintingObject.objects.filter(published=True).prefetch_related(
        "images",
        "meshes",
        "documents",
        "annotations__tags",
    )
    serializer_class = PaintingObjectSerializer
    filter_backends = SEARCH_AND_FILTER
    filterset_fields = ["artist", "inventory_number", "object_year", "published"]
    search_fields = ["title", "inventory_number", "description", "material", "technique"]
    ordering_fields = ["title", "object_year", "created_at"]


class PaintingImageViewSet(DynamicDepthViewSet):
    queryset = PaintingImage.objects.filter(published=True).select_related("painting")
    serializer_class = PaintingImageSerializer
    filter_backends = SEARCH_AND_FILTER
    filterset_fields = ["painting", "image_type", "capture_year", "published"]
    search_fields = ["caption", "source_label", "painting__title"]
    ordering_fields = ["capture_year", "sort_order", "created_at"]


class MeshViewSet(DynamicDepthViewSet):
    queryset = Mesh.objects.filter(published=True).select_related("painting")
    serializer_class = MeshSerializer
    filter_backends = SEARCH_AND_FILTER
    filterset_fields = ["painting", "mesh_format", "published"]
    search_fields = ["title", "description", "painting__title"]
    ordering_fields = ["title", "created_at"]


class PaintingDocumentViewSet(DynamicDepthViewSet):
    queryset = PaintingDocument.objects.filter(published=True).select_related("painting")
    serializer_class = PaintingDocumentSerializer
    filter_backends = SEARCH_AND_FILTER
    filterset_fields = ["painting", "document_type", "published"]
    search_fields = ["title", "description", "painting__title"]
    ordering_fields = ["title", "created_at"]


class AnnotationCategoryViewSet(DynamicDepthViewSet):
    queryset = AnnotationCategory.objects.filter(published=True)
    serializer_class = AnnotationCategorySerializer
    filter_backends = SEARCH_AND_FILTER
    filterset_fields = ["name", "published"]
    search_fields = ["name", "description"]
    ordering_fields = ["name", "created_at"]


class TagViewSet(DynamicDepthViewSet):
    queryset = Tag.objects.filter(published=True)
    serializer_class = TagSerializer
    filter_backends = SEARCH_AND_FILTER
    filterset_fields = ["text", "published"]
    search_fields = ["text"]
    ordering_fields = ["text", "created_at"]


class VisualAnnotationViewSet(DynamicDepthViewSet):
    """API endpoint for polygon and multipolygon annotations with frontend filters."""

    queryset = VisualAnnotation.objects.filter(published=True).select_related(
        "painting",
        "image",
        "mesh",
        "category",
    ).prefetch_related("tags")
    serializer_class = VisualAnnotationSerializer
    filter_backends = SEARCH_AND_FILTER
    filterset_fields = {
        "painting": ["exact"],
        "image": ["exact"],
        "mesh": ["exact"],
        "category": ["exact"],
        "tags": ["exact"],
        "annotation_year": ["exact", "gte", "lte"],
        "source": ["exact"],
        "shape_type": ["exact"],
        "published": ["exact"],
    }
    search_fields = ["title", "notes", "svg_selector", "painting__title", "category__name", "tags__text"]
    ordering_fields = ["annotation_year", "created_at", "updated_at"]

    @action(detail=False, methods=["get"])
    def filters(self, request, *args, **kwargs):
        """Return the available frontend filter values for the current selection."""
        queryset = self.filter_queryset(self.get_queryset())
        years = list(
            queryset.exclude(annotation_year__isnull=True)
            .values_list("annotation_year", flat=True)
            .distinct()
            .order_by("annotation_year")
        )
        categories = AnnotationCategory.objects.filter(annotations__in=queryset).distinct().order_by("name")
        tags = Tag.objects.filter(visual_annotations__in=queryset).distinct().order_by("text")

        return Response(
            {
                "years": years,
                "categories": AnnotationCategorySerializer(categories, many=True).data,
                "tags": TagSerializer(tags, many=True).data,
            }
        )
