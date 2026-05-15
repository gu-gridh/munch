from django.contrib import admin
from django.db.models import TextField
from django.forms import Textarea

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


class ImageInline(admin.TabularInline):
    model = Image
    extra = 0


class MeshInline(admin.TabularInline):
    model = Mesh
    extra = 0


class PaintingDocumentInline(admin.TabularInline):
    model = PaintingDocument
    extra = 0


# class VisualAnnotationInline(admin.TabularInline):
#     model = VisualAnnotation
#     extra = 0
#     autocomplete_fields = ["image", "mesh", "category"]


@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    list_display = ["name"]
    search_fields = ["name"]


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ["name"]
    search_fields = ["name"]


@admin.register(Technique)
class TechniqueAdmin(admin.ModelAdmin):
    list_display = ["name"]
    search_fields = ["name"]


@admin.register(Artwork)
class ArtworkAdmin(admin.ModelAdmin):
    list_display = ["title", "artist", "inventory_number", "creation_year", "width", "height", "published"]
    list_filter = ["artist", "published"]
    search_fields = ["title", "inventory_number", "description"]
    filter_horizontal = ["materials", "techniques"]
    autocomplete_fields = ["artist"]
    inlines = [ImageInline, MeshInline, PaintingDocumentInline]


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ["artwork", "image_type", "capture_year", "sort_order", "published"]
    list_filter = ["image_type", "capture_year", "published"]
    search_fields = ["artwork__title", "caption", "source_label"]
    autocomplete_fields = ["artwork"]


@admin.register(Mesh)
class MeshAdmin(admin.ModelAdmin):
    list_display = ["title", "artwork", "mesh_format", "published"]
    list_filter = ["mesh_format", "published"]
    search_fields = ["title", "artwork__title", "description"]
    autocomplete_fields = ["artwork"]


@admin.register(PaintingDocument)
class PaintingDocumentAdmin(admin.ModelAdmin):
    list_display = ["title", "artwork", "document_type", "year", "published"]
    list_filter = ["document_type", "year", "published"]
    search_fields = ["title", "artwork__title", "description"]
    autocomplete_fields = ["artwork"]


@admin.register(AnnotationCategory)
class AnnotationCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "color", "published"]
    list_filter = ["published"]
    search_fields = ["name", "description"]


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ["text", "published"]
    list_filter = ["published"]
    search_fields = ["text"]

 
@admin.register(Year)
class YearAdmin(admin.ModelAdmin):
    list_display = ["year"]
    search_fields = ["year"]

@admin.register(VisualAnnotation)
class VisualAnnotationAdmin(admin.ModelAdmin):
    list_display = ["title", "alt_title", "artwork", "get_categories", "annotation_year", "shape_type", "published"]
    list_filter = ["category", "shape_type", "annotation_year", "source", "published"]
    search_fields = ["title", "alt_title", "notes", "artwork__title", "category__name", "svg_selector"]
    autocomplete_fields = ["artwork"]
    filter_horizontal = ["category", "tags"]
    readonly_fields = ["title"]
    formfield_overrides = {
        TextField: {"widget": Textarea(attrs={"rows": 4})},
    }
    fieldsets = [
        (None, {
            "fields": ["artwork", "title", "alt_title", "category", "tags", "annotation_year", "source", "shape_type", "published"],
        }),
        ("Polygon coordinates", {
            "fields": ["svg_selector"],
        }),
        ("Notes", {
            "fields": ["notes"],
            "classes": ["collapse"],
        }),
    ]

    @admin.display(description="Categories")
    def get_categories(self, obj):
        return ", ".join(obj.category.values_list("name", flat=True))
