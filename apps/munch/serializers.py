"""Serializers for the Edvard Munch annotation backend."""

from rest_framework import serializers

from munch.abstract.serializers import DynamicDepthSerializer, GenericSerializer

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


class ArtistSerializer(GenericSerializer):
    class Meta(GenericSerializer.Meta):
        model = Artist
        fields = ["id", "name"]


class MaterialSerializer(GenericSerializer):
    class Meta(GenericSerializer.Meta):
        model = Material
        fields = ["id", "name"]


class TechniqueSerializer(GenericSerializer):
    class Meta(GenericSerializer.Meta):
        model = Technique
        fields = ["id", "name"]


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
            "artwork",
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
        read_only_fields = ["title"]



class AnnotoriousAnnotationSerializer(serializers.ModelSerializer):
    """Read/write W3C Web Annotation format compatible with Annotorious."""

    class Meta:
        model = VisualAnnotation
        fields = [
            "id", "artwork", "category", "tags",
            "alt_title", "notes", "annotation_year", "source",
        ]
        read_only_fields = ["title"]

    def to_representation(self, instance):
        # return in W3C format for Annotorious frontend
        return {
            "category": instance.category_id,
            "category_detail": {
                "id": instance.category.pk,
                "name": instance.category.name,
                "color": instance.category.color,
            } if instance.category_id else None,
            "tags": [{"id": t.pk, "text": t.text} for t in instance.tags.all()],
            "title": instance.title,
            "alt_title": instance.alt_title,
            "annotation_year": instance.annotation_year_id,
            "notes": instance.notes,
            "source": instance.source,
        }

    def to_internal_value(self, data):
        # Accept W3C format (from Annotorious) or flat format
        if "target" in data:
            selector = data.get("target", {}).get("selector", {})
            flat_data = {
                "artwork": data.get("target", {}).get("source") or data.get("artwork"),
                "category": data.get("category"),
                "alt_title": data.get("alt_title", ""),
                "notes": data.get("notes", ""),
                "source": data.get("source", "manual"),
                "annotation_year": data.get("annotation_year"),
            }
        else:
            flat_data = data
        return super().to_internal_value(flat_data)


class AnnotoriousMinimalSerializer(serializers.ModelSerializer):
    """Minimal W3C Web Annotation serializer returning id, svg_selector, and category colour."""

    class Meta:
        model = VisualAnnotation
        fields = ["id", "svg_selector", "category"]

    def to_representation(self, instance):
        category = instance.category
        return {
            "id": instance.pk,
            "type": "Annotation",
            "body": {
                "category": {
                    "id": category.pk,
                    "name": category.name,
                    "color": category.color,
                } if category else None,
            },
            "target": {
                "selector": {
                    "type": "SvgSelector",
                    "value": instance.svg_selector,
                }
            },
        }


class ArtworkSerializer(DynamicDepthSerializer):

    documents = PaintingDocumentSerializer(many=True, read_only=True)
    artist_detail = ArtistSerializer(source="artist", read_only=True)
    materials_detail = MaterialSerializer(source="materials", many=True, read_only=True)
    techniques_detail = TechniqueSerializer(source="techniques", many=True, read_only=True)

    class Meta(DynamicDepthSerializer.Meta):
        model = Artwork
        fields = "__all__"
