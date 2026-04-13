from django.contrib import admin

from .models import (
    AnnotationCategory,
    Mesh,
    PaintingDocument,
    Image,
    PaintingObject,
    Tag,
    VisualAnnotation,
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


class VisualAnnotationInline(admin.TabularInline):
    model = VisualAnnotation
    extra = 0
    autocomplete_fields = ["image", "mesh", "category"]


@admin.register(PaintingObject)
class PaintingObjectAdmin(admin.ModelAdmin):
    list_display = ["title", "artist", "inventory_number", "object_year", "published"]
    list_filter = ["artist", "object_year", "published"]
    search_fields = ["title", "inventory_number", "description", "material", "technique"]
    inlines = [ImageInline, MeshInline, PaintingDocumentInline, VisualAnnotationInline]


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ["painting", "image_type", "capture_year", "sort_order", "published"]
    list_filter = ["image_type", "capture_year", "published"]
    search_fields = ["painting__title", "caption", "source_label"]
    autocomplete_fields = ["painting"]


@admin.register(Mesh)
class MeshAdmin(admin.ModelAdmin):
    list_display = ["title", "painting", "mesh_format", "published"]
    list_filter = ["mesh_format", "published"]
    search_fields = ["title", "painting__title", "description"]
    autocomplete_fields = ["painting"]


@admin.register(PaintingDocument)
class PaintingDocumentAdmin(admin.ModelAdmin):
    list_display = ["title", "painting", "document_type", "published"]
    list_filter = ["document_type", "published"]
    search_fields = ["title", "painting__title", "description"]
    autocomplete_fields = ["painting"]


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


@admin.register(VisualAnnotation)
class VisualAnnotationAdmin(admin.ModelAdmin):
    list_display = ["title", "painting", "category", "annotation_year", "shape_type", "published"]
    list_filter = ["category", "shape_type", "annotation_year", "published"]
    search_fields = ["title", "notes", "painting__title", "category__name", "svg_selector"]
    autocomplete_fields = ["painting", "image", "mesh", "category", "tags"]
    filter_horizontal = ["tags"]
