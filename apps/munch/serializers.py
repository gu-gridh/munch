"""Serializers for the Edvard Munch annotation backend."""

from rest_framework import serializers

from munch.abstract.serializers import DynamicDepthSerializer, GenericSerializer

from .models import (
    AnnotationCategory,
    Mesh,
    PaintingDocument,
    Image,
    PaintingObject,
    Tag,
    VisualAnnotation,
    Year,
)


class TagSerializer(GenericSerializer):
    class Meta(GenericSerializer.Meta):
        model = Tag
        fields = ["id", "text"]

class YearSerializer(GenericSerializer):
    class Meta(GenericSerializer.Meta):
        model = Year
        fields = ["id", "year"]

class AnnotationCategorySerializer(GenericSerializer):
    class Meta(GenericSerializer.Meta):
        model = AnnotationCategory
        fields = ["id", "name", "color", "description"]


class ImageSerializer(GenericSerializer):
    class Meta(GenericSerializer.Meta):
        model = Image
        fields = [
            "id",
            "uuid",
            "file",
            "image_type",
            "caption",
            "capture_year",
            "source_label",
            "sort_order",
            "painting",
        ]


class MeshSerializer(GenericSerializer):
    class Meta(GenericSerializer.Meta):
        model = Mesh
        fields = "__all__"


class PaintingDocumentSerializer(GenericSerializer):
    class Meta(GenericSerializer.Meta):
        model = PaintingDocument
        fields = "__all__"


class VisualAnnotationSerializer(DynamicDepthSerializer):
    category_detail = AnnotationCategorySerializer(source="category", read_only=True)
    tags_detail = TagSerializer(source="tags", many=True, read_only=True)
    class Meta(DynamicDepthSerializer.Meta):
        model = VisualAnnotation
        fields = "__all__"


class AnnotoriousAnnotationSerializer(serializers.ModelSerializer):
    """Read/write W3C Web Annotation format compatible with Annotorious."""

    class Meta:
        model = VisualAnnotation
        fields = [
            "id", "image", "category", "tags",
            "title", "notes", "annotation_year", "source", "annotation_borders",
        ]

    def to_representation(self, instance):
        return {
            "id": str(instance.pk),
            "type": "Annotation",
            "target": {
                "source": str(instance.image_id),
                "selector": {
                    "type": "SvgSelector",
                    "value": instance.annotation_borders or "",
                },
            },
            "category": instance.category_id,
            "category_detail": {
                "id": instance.category.pk,
                "name": instance.category.name,
                "color": instance.category.color,
            } if instance.category_id else None,
            "tags": [{"id": t.pk, "text": t.text} for t in instance.tags.all()],
            "title": instance.title,
            "annotation_year": instance.annotation_year_id,
            "notes": instance.notes,
            "source": instance.source,
        }

    def to_internal_value(self, data):
        # Accept W3C format (from Annotorious) or flat format
        if "target" in data:
            selector = data.get("target", {}).get("selector", {})
            flat_data = {
                "annotation_borders": selector.get("value", ""),
                "image": data.get("target", {}).get("source") or data.get("image"),
                "category": data.get("category"),
                "title": data.get("title", ""),
                "notes": data.get("notes", ""),
                "source": data.get("source", "annotorious"),
                "annotation_year": data.get("annotation_year"),
            }
        else:
            flat_data = data
        return super().to_internal_value(flat_data)


class PaintingObjectSerializer(DynamicDepthSerializer):
    images = ImageSerializer(many=True, read_only=True)
    meshes = MeshSerializer(many=True, read_only=True)
    documents = PaintingDocumentSerializer(many=True, read_only=True)
    annotations = VisualAnnotationSerializer(many=True, read_only=True)

    class Meta(DynamicDepthSerializer.Meta):
        model = PaintingObject
        fields = "__all__"
