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
)


class TagSerializer(GenericSerializer):
    class Meta(GenericSerializer.Meta):
        model = Tag
        fields = ["id", "text"]


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
    polygon_count = serializers.SerializerMethodField()

    def get_polygon_count(self, obj):
        return len(obj.geometry or [])

    class Meta(DynamicDepthSerializer.Meta):
        model = VisualAnnotation
        fields = "__all__"


class PaintingObjectSerializer(DynamicDepthSerializer):
    images = ImageSerializer(many=True, read_only=True)
    meshes = MeshSerializer(many=True, read_only=True)
    documents = PaintingDocumentSerializer(many=True, read_only=True)
    annotations = VisualAnnotationSerializer(many=True, read_only=True)

    class Meta(DynamicDepthSerializer.Meta):
        model = PaintingObject
        fields = "__all__"
