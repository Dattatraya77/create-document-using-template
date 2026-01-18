from django.db import models
from django.contrib.auth.models import User


TEMPLATE_STATUS = (
    ('ac', 'Active'),
    ('ia', 'Inactive'),
    ('de', 'Deleted'),
    ('pe', 'Pending')
)

class Template(models.Model):
    temp_id = models.CharField(max_length=64, primary_key=True, unique=True)
    temp_status = models.CharField(max_length=2, choices=TEMPLATE_STATUS, default='pe')
    temp_title = models.CharField(max_length=100, default='title for template')
    temp_description = models.CharField(max_length=400, default='description for template')
    upload_template = models.FileField(upload_to="template/", max_length=200)

    temp_owner = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='owned_templates'
    )

    temp_created_at = models.DateTimeField(auto_now_add=True)

    temp_edited_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='edited_templates'
    )

    temp_edited_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.temp_title


FILE_STATUS = (
    ('ac', 'Active'),
    ('ia', 'Inactive'),
    ('de', 'Deleted')
)

DOC_TYPE = (
    ('docx', 'docx'),
    ('pdf', 'pdf'),
    ('xlsx', 'xlsx'),
    ('html', 'html'),
)

class CreatedDocument(models.Model):
    doc_id = models.CharField(max_length=64, primary_key=True, unique=True)
    document = models.FileField(
        upload_to="created_document/",
        max_length=200,
        null=True,
        blank=True
    )
    document_name = models.CharField(max_length=200, null=True, blank=True)

    doc_matched_template = models.ForeignKey(
        Template,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='created_documents'
    )

    doc_created_at = models.DateTimeField(auto_now_add=True)

    doc_created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='created_documents'
    )

    status = models.CharField(max_length=2, choices=FILE_STATUS, default='ac')
    doc_type = models.CharField(max_length=20, choices=DOC_TYPE, default='docx')
    doc_updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.doc_id


class MetadataChoice(models.Model):
    meta_choice = models.CharField(max_length=250, unique=True)

    def __str__(self):
        return self.meta_choice


METADATA_TYPE = (
    ('string', 'String'),
    ('integer', 'Integer'),
    ('date', 'Date'),
    ('bool', 'Boolean'),
    ('choice', 'Choice'),
    ('textarea', 'TextArea'),
    ('image', 'Image'),
    ('signature', 'Signature'),
)

class MetadataKey(models.Model):
    key_id = models.AutoField(primary_key=True)
    metadata_key = models.CharField(max_length=100, unique=True)
    metadata_description = models.CharField(max_length=200, blank=True)
    metadata_type = models.CharField(max_length=10, choices=METADATA_TYPE)
    external_metadata = models.BooleanField(default=False)
    metadata_choice = models.ManyToManyField(
        MetadataChoice,
        blank=True,
        related_name='metadata_keys'
    )

    def __str__(self):
        return self.metadata_key


class TemplateMetaData(models.Model):
    temp_meta_id = models.AutoField(primary_key=True)

    temp_metadata = models.ForeignKey(
        Template,
        on_delete=models.CASCADE,
        related_name='template_metadata_items'
    )

    temp_meta_key = models.ForeignKey(
        MetadataKey,
        on_delete=models.CASCADE,
        related_name='template_metadata_items'
    )

    def __str__(self):
        return self.temp_meta_key.metadata_key

    class Meta:
        unique_together = ('temp_metadata', 'temp_meta_key')


class MetadataValue(models.Model):
    meta_upload_id = models.AutoField(primary_key=True)
    meta_upload_value = models.CharField(max_length=1000)

    meta_key = models.ForeignKey(
        MetadataKey,
        on_delete=models.CASCADE,
        related_name='metadata_values'
    )

    meta_created_doc = models.ForeignKey(
        CreatedDocument,
        on_delete=models.CASCADE,
        related_name='metadata_values'
    )

    def __str__(self):
        return self.meta_upload_value
