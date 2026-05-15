"""Viewsets for the Edvard Munch annotation backend."""

import django_filters
from django.db.models import Q
from rest_framework import filters
from rest_framework.decorators import action
from rest_framework.response import Response

from munch.abstract.views import DynamicDepthViewSet

from .models import (
    AnnotationCategory,
    Artist,
    Artwork,
    Material,
    Mesh,
    PaintingDocument,
    Image,
    Tag,
    Technique,
    VisualAnnotation,
    Year,
)
from .serializers import (
    AnnotationCategorySerializer,
    AnnotoriousAnnotationSerializer,
    AnnotoriousMinimalSerializer,
    ArtistSerializer,
    ArtworkSerializer,
    MaterialSerializer,
    MeshSerializer,
    PaintingDocumentSerializer,
    ImageSerializer,
    TagSerializer,
    TechniqueSerializer,
    VisualAnnotationSerializer,
    YearSerializer,
)


SEARCH_AND_FILTER = DynamicDepthViewSet.filter_backends + [
    filters.SearchFilter,
    filters.OrderingFilter,
]


class ArtworkFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(method="filter_lower")
    inventory_number = django_filters.CharFilter(method="filter_lower")

    def filter_lower(self, queryset, name, value):
        return queryset.filter(**{f"{name}__iexact": value.lower()})

    class Meta:
        model = Artwork
        fields = ["title", "inventory_number", "artist", "creation_year", "published"]


class TagFilter(django_filters.FilterSet):
    panel = django_filters.CharFilter(method="filter_by_panel")

    def filter_by_panel(self, queryset, name, value):
        return queryset.filter(
            visual_annotations__artwork__title__iexact=value.lower()
        ).distinct()

    class Meta:
        model = Tag
        fields = ["text", "published"]


class YearFilter(django_filters.FilterSet):
    panel = django_filters.CharFilter(method="filter_by_panel")

    def filter_by_panel(self, queryset, name, value):
        return queryset.filter(
            Q(annotations__artwork__title__iexact=value.lower())
            | Q(documents__artwork__title__iexact=value.lower())
        ).distinct()

    class Meta:
        model = Year
        fields = ["year"]


class AnnotationCategoryFilter(django_filters.FilterSet):
    panel = django_filters.CharFilter(method="filter_by_panel")

    def filter_by_panel(self, queryset, name, value):
        return queryset.filter(
            annotations__artwork__title__iexact=value.lower()
        ).distinct()

    class Meta:
        model = AnnotationCategory
        fields = ["name", "published"]


class ImageFilter(django_filters.FilterSet):
    panel = django_filters.CharFilter(method="filter_by_panel")

    def filter_by_panel(self, queryset, name, value):
        return queryset.filter(artwork__title__iexact=value.lower())

    class Meta:
        model = Image
        fields = ["artwork", "image_type", "capture_year", "published"]


class MeshFilter(django_filters.FilterSet):
    panel = django_filters.CharFilter(method="filter_by_panel")

    def filter_by_panel(self, queryset, name, value):
        return queryset.filter(artwork__title__iexact=value.lower())

    class Meta:
        model = Mesh
        fields = ["artwork", "mesh_format", "published"]


class PaintingDocumentFilter(django_filters.FilterSet):
    panel = django_filters.CharFilter(method="filter_by_panel")
    year = django_filters.CharFilter(method="filter_year")

    def filter_by_panel(self, queryset, name, value):
        return queryset.filter(artwork__title__iexact=value.lower())

    def filter_year(self, queryset, name, value):
        raw_values = self.data.getlist("year")
        split_values = [v.strip() for entry in raw_values for v in entry.split(",") if v.strip()]
        if not split_values:
            return queryset
        try:
            ids = [int(v) for v in split_values]
            return queryset.filter(year__in=ids).distinct()
        except (ValueError, TypeError):
            return queryset

    class Meta:
        model = PaintingDocument
        fields = ["artwork", "document_type", "published"]

class VisualAnnotationFilter(django_filters.FilterSet):
    panel = django_filters.CharFilter(method="filter_by_panel")
    panel_id = django_filters.NumberFilter(field_name="artwork", lookup_expr="exact")
    id = django_filters.NumberFilter(field_name="id", lookup_expr="exact")
    category = django_filters.ModelMultipleChoiceFilter(queryset=AnnotationCategory.objects.all())
    tags = django_filters.ModelMultipleChoiceFilter(queryset=Tag.objects.all())

    def filter_by_panel(self, queryset, name, value):
        return queryset.filter(artwork__title__iexact=value.lower())

    class Meta:
        model = VisualAnnotation
        fields = {
            "annotation_year": ["exact", "gte", "lte"],
            "source": ["exact"],
            "shape_type": ["exact"],
            "published": ["exact"],
        }


class AnnotoriousFilter(VisualAnnotationFilter):
    """Extends VisualAnnotationFilter to treat 'all' as no-op for category, tags, and annotation_year."""

    category = django_filters.CharFilter(method="filter_or_all")
    tags = django_filters.CharFilter(method="filter_or_all")
    annotation_year = django_filters.CharFilter(method="filter_or_all")

    def filter_or_all(self, queryset, name, value):
        raw_values = self.data.getlist(name)
        # Support both comma-separated (?tags=1,2) and repeated (?tags=1&tags=2)
        split_values = [v.strip() for entry in raw_values for v in entry.split(",") if v.strip()]
        if not split_values or "all" in split_values:
            return queryset
        try:
            ids = [int(v) for v in split_values]
            if not ids:
                return queryset
            return queryset.filter(**{f"{name}__in": ids}).distinct()
        except (ValueError, TypeError):
            return queryset


class ArtistViewSet(DynamicDepthViewSet):
    queryset = Artist.objects.all()
    serializer_class = ArtistSerializer
    filter_backends = SEARCH_AND_FILTER
    search_fields = ["name"]
    ordering_fields = ["name"]


class MaterialViewSet(DynamicDepthViewSet):
    queryset = Material.objects.all()
    serializer_class = MaterialSerializer
    filter_backends = SEARCH_AND_FILTER
    search_fields = ["name"]
    ordering_fields = ["name"]


class TechniqueViewSet(DynamicDepthViewSet):
    queryset = Technique.objects.all()
    serializer_class = TechniqueSerializer
    filter_backends = SEARCH_AND_FILTER
    search_fields = ["name"]
    ordering_fields = ["name"]


# Panel refers to artwork here
class ArtworkViewSet(DynamicDepthViewSet):
    """API endpoint for artwork metadata and nested annotation resources."""

    queryset = Artwork.objects.filter(published=True).prefetch_related(
        "documents",
        "materials",
        "techniques",
    ).select_related("artist")
    serializer_class = ArtworkSerializer
    filter_backends = SEARCH_AND_FILTER
    filterset_class = ArtworkFilter
    search_fields = ["title", "inventory_number", "description"]
    ordering_fields = ["title", "creation_year", "created_at"]


class ImageViewSet(DynamicDepthViewSet):
    queryset = Image.objects.filter(published=True).select_related("artwork")
    serializer_class = ImageSerializer
    filter_backends = SEARCH_AND_FILTER
    filterset_class = ImageFilter
    search_fields = ["caption", "source_label", "artwork__title"]
    ordering_fields = ["capture_year", "sort_order", "created_at"]


class MeshViewSet(DynamicDepthViewSet):
    queryset = Mesh.objects.filter(published=True).select_related("artwork")
    serializer_class = MeshSerializer
    filter_backends = SEARCH_AND_FILTER
    filterset_class = MeshFilter
    search_fields = ["title", "description", "artwork__title"]
    ordering_fields = ["title", "created_at"]


class PaintingDocumentViewSet(DynamicDepthViewSet):
    queryset = PaintingDocument.objects.filter(published=True).select_related("artwork", "year")
    serializer_class = PaintingDocumentSerializer
    filter_backends = SEARCH_AND_FILTER
    filterset_class = PaintingDocumentFilter
    search_fields = ["title", "description", "artwork__title"]
    ordering_fields = ["title", "year__year", "created_at"]


class AnnotationCategoryViewSet(DynamicDepthViewSet):
    queryset = AnnotationCategory.objects.filter(published=True)
    serializer_class = AnnotationCategorySerializer
    filter_backends = SEARCH_AND_FILTER
    filterset_class = AnnotationCategoryFilter
    search_fields = ["name", "description"]
    ordering_fields = ["name", "created_at"]


class TagViewSet(DynamicDepthViewSet):
    queryset = Tag.objects.filter(published=True)
    serializer_class = TagSerializer
    filter_backends = SEARCH_AND_FILTER
    filterset_class = TagFilter
    search_fields = ["text"]
    ordering_fields = ["text", "created_at"]

class YearViewSet(DynamicDepthViewSet):
    queryset = Year.objects.all()
    serializer_class = YearSerializer
    filter_backends = SEARCH_AND_FILTER
    filterset_class = YearFilter
    search_fields = ["year"]
    ordering_fields = ["year"]

class VisualAnnotationViewSet(DynamicDepthViewSet):
    """API endpoint for polygon and multipolygon annotations with frontend filters."""

    queryset = VisualAnnotation.objects.filter(published=True).select_related(
        "artwork",
    ).prefetch_related("category", "tags")
    serializer_class = VisualAnnotationSerializer
    filter_backends = SEARCH_AND_FILTER
    filterset_class = VisualAnnotationFilter
    search_fields = ["title", "alt_title", "notes", "artwork__title", "category__name", "tags__text"]
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

    @action(detail=False, methods=["get", "post"], url_path="annotorious")
    def annotorious(self, request):
        """List or create annotations in W3C Web Annotation format for Annotorious."""
        if request.method == "GET":
            qs = self.filter_queryset(self.get_queryset())
            serializer = AnnotoriousAnnotationSerializer(qs, many=True)
            return Response(serializer.data)

        serializer = AnnotoriousAnnotationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=201)

    @action(detail=True, methods=["put", "patch", "delete"], url_path="annotorious")
    def annotorious_detail(self, request, pk=None):
        """Update or delete a single annotation in W3C format."""
        instance = self.get_object()
        if request.method == "DELETE":
            instance.delete()
            return Response(status=204)
        partial = request.method == "PATCH"
        serializer = AnnotoriousAnnotationSerializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class AnnoationViewSet(VisualAnnotationViewSet):
    """
    Simplified W3C Web Annotation endpoint for Annotorious.

    Returns only id + svg_selector in W3C format::

        [
          {
            "id": 1,
            "type": "Annotation",
            "target": {"selector": {"type": "SvgSelector", "value": "<svg>...</svg>"}}
          },
          ...
        ]

    Supports all VisualAnnotationFilter params (panel, panel_id, source, shape_type,
    published). Pass ``category=all``, ``tags=all``, or ``annotation_year=all`` to skip
    filtering on those fields and return all values.
    """

    serializer_class = AnnotoriousMinimalSerializer
    filter_backends = SEARCH_AND_FILTER
    filterset_class = AnnotoriousFilter
    search_fields = ["title", "alt_title", "notes", "artwork__title", "category__name", "tags__text"]
    ordering_fields = ["annotation_year", "created_at", "updated_at"]



                
