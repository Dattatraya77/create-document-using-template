from django.contrib import admin
from .models import *


@admin.register(Template)
class TemplateAdmin(admin.ModelAdmin):
    list_display = ('temp_id','temp_owner', 'upload_template', 'temp_title', 'temp_description',
                    'temp_created_at', 'temp_edited_on', 'temp_status', 'temp_edited_by')


@admin.register(CreatedDocument)
class CreatedDocumentAdmin(admin.ModelAdmin):
    list_display = ('doc_id','document', 'document_name', 'doc_matched_template', 'doc_created_at',
                    'doc_created_by', 'status', 'doc_type', 'doc_updated_on')


@admin.register(MetadataChoice)
class MetadataChoiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'meta_choice')


@admin.register(MetadataKey)
class MetadataKeyAdmin(admin.ModelAdmin):
    list_display = ('key_id', 'metadata_key', 'metadata_description', 'metadata_type', 'external_metadata')


@admin.register(TemplateMetaData)
class TemplateMetaDataAdmin(admin.ModelAdmin):
    list_display = ('temp_meta_id', 'temp_metadata', 'temp_meta_key')


@admin.register(MetadataValue)
class MetadataValueAdmin(admin.ModelAdmin):
    list_display = ('meta_upload_id', 'meta_upload_value', 'meta_key', 'meta_created_doc')

