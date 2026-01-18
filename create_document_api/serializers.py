from .models import Template, TemplateMetaData, CreatedDocument, \
    MetadataKey, MetadataChoice, MetadataValue
from rest_framework import serializers



class TemplateDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Template
        fields = "__all__"


class TemplateTrainSerializer(serializers.ModelSerializer):
    external_metadata = serializers.CharField(read_only=True)

    class Meta:
        model = Template
        fields = [
            "temp_id",
            "temp_title",
            "temp_description",
            "upload_template",
            "external_metadata"
        ]