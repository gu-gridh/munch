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


class Artist(models.Model):
    """Controlled list of artists."""

    name = models.CharField(max_length=256, unique=True, verbose_name=_("Name"))

    class Meta:
        verbose_name = _("Artist")
        verbose_name_plural = _("Artists")
        ordering = ["name"]

    def __str__(self):
        return self.name


class Material(models.Model):
    """Controlled list of materials."""

    name = models.CharField(max_length=256, unique=True, verbose_name=_("Name"))

    class Meta:
        verbose_name = _("Material")
        verbose_name_plural = _("Materials")
        ordering = ["name"]

    def __str__(self):
        return self.name


class Technique(models.Model):
    """Controlled list of techniques."""

    name = models.CharField(max_length=256, unique=True, verbose_name=_("Name"))

    class Meta:
        verbose_name = _("Technique")
        verbose_name_plural = _("Techniques")
        ordering = ["name"]

    def __str__(self):
        return self.name


class Artwork(AbstractBaseModel):
    """Core metadata for an Edvard Munch artwork (painting, mosaic, etc.)."""

    title = models.CharField(max_length=256, verbose_name=_("Title"))
    artist = models.ForeignKey("Artist", on_delete=models.SET_NULL, related_name="artworks", blank=True, null=True, verbose_name=_("Artist"))
    inventory_number = models.CharField(max_length=128, blank=True, verbose_name=_("Inventory number"))
    creation_year = models.PositiveIntegerField(blank=True, null=True, verbose_name=_("Creation year"))
    width = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True, verbose_name=_("Width (cm)"))
    height = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True, verbose_name=_("Height (cm)"))
    materials = models.ManyToManyField("Material", blank=True, related_name="artworks", verbose_name=_("Materials"))
    techniques = models.ManyToManyField("Technique", blank=True, related_name="artworks", verbose_name=_("Techniques"))
    description = models.TextField(blank=True, verbose_name=_("Description"))

    class Meta:
        verbose_name = _("Artwork")
        verbose_name_plural = _("Artworks")
        ordering = ["title"]

    def __str__(self):
        return self.title


class Tag(AbstractTagModel):
    """Reusable tag for annotation filtering."""

    class Meta(AbstractTagModel.Meta):
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")
        ordering = ["text"]

class Year(models.Model):
    year = models.PositiveIntegerField(unique=True, verbose_name=_("Year"))

    class Meta:
        verbose_name = _("Year")
        verbose_name_plural = _("Years")
        ordering = ["year"]

    def __str__(self):
        return str(self.year)

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
    """Image representation of an artwork, e.g. orthophoto or topographical view."""

    artwork = models.ForeignKey(
        Artwork,
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name=_("Artwork"),
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
        return f"{self.get_image_type_display()}"

class Mesh(AbstractBaseModel):
    """3D mesh or related geometric model for an artwork."""

    artwork = models.ForeignKey(
        Artwork,
        on_delete=models.CASCADE,
        related_name="meshes",
        verbose_name=_("Artwork"),
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
    """Downloadable documents associated with an artwork."""

    artwork = models.ForeignKey(
        Artwork,
        on_delete=models.CASCADE,
        related_name="documents",
        verbose_name=_("Artwork"),
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
    """Polygon or multipolygon visual annotation connected to an artwork and category."""

    svg_selector = models.TextField(
        blank=True,
        verbose_name=_("SVG selector"),
        help_text=_("Raw SVG polygon snippet from Annotorious, e.g. <svg><polygon points=.../></svg>."),
    )
    artwork = models.ForeignKey(
        Artwork,
        on_delete=models.CASCADE,
        related_name="annotations",
        blank=True,
        null=True,
        verbose_name=_("Artwork"),
    )
    title = models.CharField(max_length=256, blank=True, editable=False, verbose_name=_("Title"))
    alt_title = models.CharField(max_length=256, blank=True, verbose_name=_("Alternative title"))
    category = models.ForeignKey(
        AnnotationCategory,
        on_delete=models.PROTECT,
        related_name="annotations",
        verbose_name=_("Category"),
    )
    tags = models.ManyToManyField(Tag, blank=True, related_name="visual_annotations", verbose_name=_("Tags"))
    annotation_year = models.ForeignKey(Year, on_delete=models.SET_NULL, related_name="annotations", blank=True, null=True, verbose_name=_("Annotation year"))
    source = models.CharField(
        max_length=32,
        choices=ANNOTATION_SOURCE_CHOICES,
        default="manual",
        verbose_name=_("Source"),
    )
    shape_type = models.CharField(
        max_length=32,
        choices=SHAPE_TYPE_CHOICES,
        default="polygon",
        verbose_name=_("Shape type"),
    )

    notes = models.TextField(blank=True, verbose_name=_("Notes"))

    class Meta:
        verbose_name = _("Visual annotation")
        verbose_name_plural = _("Visual annotations")
        ordering = ["annotation_year__year", "id"]
        indexes = [models.Index(fields=["annotation_year"])]

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        artwork_title = self.artwork.title if self.artwork_id else "Unknown"
        auto_title = f"{artwork_title}:{self.pk}"
        VisualAnnotation.objects.filter(pk=self.pk).update(title=auto_title)
        self.title = auto_title

    def __str__(self):
        label = self.alt_title or self.title or self.category.name
        artwork_title = self.artwork.title if self.artwork_id else "–"
        return f"{artwork_title} – {label}"
