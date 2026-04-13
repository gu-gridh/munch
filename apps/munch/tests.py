"""Tests for the Edvard Munch annotation backend."""

import io

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image as PILImage
from rest_framework import status
from rest_framework.test import APIClient

from .models import AnnotationCategory, Image, PaintingObject, Tag, VisualAnnotation


SVG_POLYGON = '<svg><polygon points="2327,18512 3780,12207 7960,13838 7953,18702 3798,18702" /></svg>'


def generate_test_image(name="annotation-test.png"):
    buffer = io.BytesIO()
    PILImage.new("RGB", (20, 20), color="orange").save(buffer, format="PNG")
    return SimpleUploadedFile(name, buffer.getvalue(), content_type="image/png")


@pytest.mark.django_db
class TestVisualAnnotationModel:
    def setup_method(self):
        self.painting = PaintingObject.objects.create(
            title="The Sun",
            inventory_number="MUNCH-001",
            object_year=1911,
        )
        self.category = AnnotationCategory.objects.create(name="Crack", color="#ff0000")
        self.image = Image.objects.create(
            painting=self.painting,
            image_type="orthophoto",
            caption="Full painting",
            file=generate_test_image(),
        )

    def test_svg_selector_is_parsed_to_geometry(self):
        annotation = VisualAnnotation.objects.create(
            painting=self.painting,
            image=self.image,
            category=self.category,
            annotation_year=2024,
            svg_selector=SVG_POLYGON,
        )

        assert annotation.shape_type == "polygon"
        assert len(annotation.geometry) == 1
        assert annotation.geometry[0][0]["x"] == 2327.0
        assert annotation.geometry[0][0]["y"] == 18512.0

    def test_tag_can_be_attached_to_annotation(self):
        tag = Tag.objects.create(text="retouching")
        annotation = VisualAnnotation.objects.create(
            painting=self.painting,
            image=self.image,
            category=self.category,
            annotation_year=2025,
            geometry=[[{"x": 0, "y": 0}, {"x": 1, "y": 0}, {"x": 1, "y": 1}, {"x": 0, "y": 0}]],
        )
        annotation.tags.add(tag)

        assert annotation.tags.count() == 1
        assert annotation.tags.first().text == "retouching"


@pytest.mark.django_db
class TestAnnotationAPI:
    def setup_method(self):
        self.client = APIClient()
        self.painting = PaintingObject.objects.create(title="The Sun", inventory_number="MUNCH-002")
        self.category = AnnotationCategory.objects.create(name="Paint loss", color="#00ff99")
        self.tag = Tag.objects.create(text="surface")
        self.image = Image.objects.create(
            painting=self.painting,
            image_type="topographical",
            caption="Topography",
            file=generate_test_image("topography.png"),
        )
        self.annotation = VisualAnnotation.objects.create(
            painting=self.painting,
            image=self.image,
            category=self.category,
            annotation_year=2026,
            svg_selector=SVG_POLYGON,
        )
        self.annotation.tags.add(self.tag)

    def test_list_visual_annotations(self):
        response = self.client.get("/api/munch/visual-annotations/?annotation_year=2026")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
        assert response.data["results"][0]["annotation_year"] == 2026

    def test_filter_metadata_endpoint(self):
        response = self.client.get(f"/api/munch/visual-annotations/filters/?painting={self.painting.pk}")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["years"] == [2026]
        assert response.data["categories"][0]["name"] == "Paint loss"
        assert response.data["tags"][0]["text"] == "surface"

    def test_retrieve_painting_with_nested_resources(self):
        response = self.client.get(f"/api/munch/paintings/{self.painting.pk}/?depth=1")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["title"] == "The Sun"
