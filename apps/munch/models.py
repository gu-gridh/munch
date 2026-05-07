"""Domain models for the Edvard Munch annotation backend."""

import re

from colorfield.fields import ColorField
from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _

from munch.abstract.models import AbstractBaseModel, AbstractImageModel, AbstractTagModel


IMAGE_TYPE_CHOICES = [
    ("orthophoto", _("Orthophoto")),
    ("topographical", _("Topographical visualisation")),
    ("detail", _("Detail")),
    ("other", _("Other")),
]

DOCUMENT_TYPE_CHOICES = [
    ("pdf", _("PDF")),
    ("report", _("Report")),
    ("metadata", _("Metadata")),
    ("other", _("Other")),
]

ANNOTATION_SOURCE_CHOICES = [
    ("annotorious", _("Annotorious")),
    ("manual", _("Manual")),
    ("imported", _("Imported")),
]

SHAPE_TYPE_CHOICES = [
    ("polygon", _("Polygon")),
    ("multipolygon", _("Multipolygon")),
]

POLYGON_PATTERN = re.compile(r'points="([^"]+)"')


def parse_svg_polygons(value: str) -> list[list[dict[str, float]]]:
    """Parse one or more SVG polygon point lists into JSON-friendly coordinates."""
    if not value:
        return []

    raw_polygons = POLYGON_PATTERN.findall(value)
    if not raw_polygons and "<" not in value:
        raw_polygons = [value]

    polygons: list[list[dict[str, float]]] = []
    for raw_polygon in raw_polygons:
        points: list[dict[str, float]] = []
        for pair in raw_polygon.replace("\n", " ").split():
            if "," not in pair:
                continue
            x_value, y_value = pair.split(",", 1)
            try:
                points.append({"x": float(x_value), "y": float(y_value)})
            except ValueError:
                continue

        if len(points) >= 3:
            if points[0] != points[-1]:
                points.append(points[0].copy())
            polygons.append(points)

    return polygons


class PaintingObject(AbstractBaseModel):
    """Core metadata for an Edvard Munch painting or painted surface."""

    title = models.CharField(max_length=256, verbose_name=_("Title"))
    artist = models.CharField(max_length=256, default="Edvard Munch", verbose_name=_("Artist"))
    inventory_number = models.CharField(max_length=128, blank=True, verbose_name=_("Inventory number"))
    object_year = models.PositiveIntegerField(blank=True, null=True, verbose_name=_("Object year"))
    material = models.CharField(max_length=256, blank=True, verbose_name=_("Material"))
    technique = models.CharField(max_length=256, blank=True, verbose_name=_("Technique"))
    description = models.TextField(blank=True, verbose_name=_("Description"))

    class Meta:
        verbose_name = _("Painting object")
        verbose_name_plural = _("Painting objects")
        ordering = ["title"]

    def __str__(self):
        return self.title


class Tag(AbstractTagModel):
    """Reusable tag for annotation filtering."""

    class Meta(AbstractTagModel.Meta):
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")
        ordering = ["text"]


class AnnotationCategory(AbstractBaseModel):
    """Category / type of visual annotation, with frontend display color."""

    name = models.CharField(max_length=128, unique=True, verbose_name=_("Name"))
    color = ColorField(default="#E85D04", verbose_name=_("Color"))
    description = models.TextField(blank=True, verbose_name=_("Description"))

    class Meta:
        verbose_name = _("Annotation category")
        verbose_name_plural = _("Annotation categories")
        ordering = ["name"]

    def __str__(self):
        return self.name


class Image(AbstractImageModel):
    """Image representation of the painting, e.g. orthophoto or topographical view."""

    painting = models.ForeignKey(
        PaintingObject,
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name=_("Painting object"),
    )
    image_type = models.CharField(
        max_length=32,
        choices=IMAGE_TYPE_CHOICES,
        default="orthophoto",
        verbose_name=_("Image type"),
    )
    caption = models.CharField(max_length=512, blank=True, verbose_name=_("Caption"))
    capture_year = models.PositiveIntegerField(blank=True, null=True, verbose_name=_("Capture year"))
    source_label = models.CharField(max_length=256, blank=True, verbose_name=_("Source label"))
    sort_order = models.PositiveIntegerField(default=0, verbose_name=_("Sort order"))

    class Meta:
        verbose_name = _("image")
        verbose_name_plural = _("images")
        ordering = ["sort_order", "id"]

    def __str__(self):
        return f"{self.painting.title} – {self.get_image_type_display()}"

class Mesh(AbstractBaseModel):
    """3D mesh or related geometric model for the painting surface."""

    painting = models.ForeignKey(
        PaintingObject,
        on_delete=models.CASCADE,
        related_name="meshes",
        verbose_name=_("Painting object"),
    )
    title = models.CharField(max_length=256, verbose_name=_("Title"))
    mesh_file = models.FileField(upload_to="munch/meshes/", verbose_name=_("Mesh file"))
    mesh_format = models.CharField(max_length=64, blank=True, verbose_name=_("Mesh format"))
    description = models.TextField(blank=True, verbose_name=_("Description"))

    class Meta:
        verbose_name = _("Mesh")
        verbose_name_plural = _("Meshes")
        ordering = ["title"]

    def __str__(self):
        return self.title


class PaintingDocument(AbstractBaseModel):
    """Downloadable documents associated with a painting object."""

    painting = models.ForeignKey(
        PaintingObject,
        on_delete=models.CASCADE,
        related_name="documents",
        verbose_name=_("Painting object"),
    )
    title = models.CharField(max_length=256, verbose_name=_("Title"))
    document_type = models.CharField(
        max_length=32,
        choices=DOCUMENT_TYPE_CHOICES,
        default="pdf",
        verbose_name=_("Document type"),
    )
    file = models.FileField(upload_to="munch/documents/", verbose_name=_("File"))
    description = models.TextField(blank=True, verbose_name=_("Description"))

    class Meta:
        verbose_name = _("Painting document")
        verbose_name_plural = _("Painting documents")
        ordering = ["title"]

    def __str__(self):
        return self.title


class VisualAnnotation(AbstractBaseModel):
    """Polygon or multipolygon visual annotation connected to an image and category."""

    # painting = models.ForeignKey(
    #     PaintingObject,
    #     on_delete=models.CASCADE,
    #     related_name="annotations",
    #     verbose_name=_("Painting object"),
    # )
    geometry = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_("Geometry"),
        help_text=_("List of polygons; each polygon is stored as x/y coordinate objects."),
    )
    image = models.ForeignKey(
        Image,
        on_delete=models.CASCADE,
        related_name="annotations",
        verbose_name=_("Image"),
    )
    # mesh = models.ForeignKey(
    #     Mesh,
    #     on_delete=models.SET_NULL,
    #     related_name="annotations",
    #     blank=True,
    #     null=True,
    #     verbose_name=_("Mesh"),
    # )
    title = models.CharField(max_length=256, blank=True, verbose_name=_("Title"))
    category = models.ForeignKey(
        AnnotationCategory,
        on_delete=models.PROTECT,
        related_name="annotations",
        verbose_name=_("Category"),
    )
    tags = models.ManyToManyField(Tag, blank=True, related_name="visual_annotations", verbose_name=_("Tags"))
    annotation_year = models.PositiveIntegerField(blank=True, null=True, verbose_name=_("Annotation year"))
    source = models.CharField(
        max_length=32,
        choices=ANNOTATION_SOURCE_CHOICES,
        default="annotorious",
        verbose_name=_("Source"),
    )
    shape_type = models.CharField(
        max_length=32,
        choices=SHAPE_TYPE_CHOICES,
        default="polygon",
        verbose_name=_("Shape type"),
    )

    # svg_selector = models.TextField(
    #     blank=True,
    #     verbose_name=_("SVG selector"),
    #     help_text=_("Raw SVG polygon snippet from Annotorious, e.g. <svg><polygon points=.../></svg>."),
    # )
    notes = models.TextField(blank=True, verbose_name=_("Notes"))

    class Meta:
        verbose_name = _("Visual annotation")
        verbose_name_plural = _("Visual annotations")
        ordering = ["annotation_year", "id"]
        indexes = [models.Index(fields=["annotation_year"])]

    def save(self, *args, **kwargs):
        if self.svg_selector and not self.geometry:
            self.geometry = parse_svg_polygons(self.svg_selector)

        if len(self.geometry or []) > 1:
            self.shape_type = "multipolygon"
        else:
            self.shape_type = "polygon"

        super().save(*args, **kwargs)

    def __str__(self):
        label = self.title or self.category.name
        return f"{self.image.title} – {label}"
