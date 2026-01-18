from django.core.files.storage import default_storage
import datetime
from create_document_using_template.settings import MEDIA_ROOT
from .models import Template, MetadataKey, TemplateMetaData, CreatedDocument, MetadataValue
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from .actions import get_metadata_details
import json
from rest_framework import viewsets
from docxtpl import DocxTemplate, InlineImage
from docx.shared import Mm
import os
from django.conf import settings


class TemplateTrainViewSet(viewsets.ModelViewSet):
    queryset = Template.objects.filter(temp_status='ac')
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        user = request.user
        data = request.data

        temp_id = data["temp_id"]
        temp_title = data["temp_title"]
        temp_description = data["temp_description"]
        upload_template = data["upload_template"]

        # external_metadata is OPTIONAL
        external_metadata_raw = data.get("external_metadata")
        external_metadata_list = (
            json.loads(external_metadata_raw)
            if external_metadata_raw else []
        )

        # Save file
        path = f"templates/{upload_template.name}"
        file_path = default_storage.save(path, upload_template)

        try:
            template = Template.objects.create(
                temp_id=temp_id,
                upload_template=file_path,
                temp_title=temp_title,
                temp_description=temp_description,
                temp_owner=user,
                temp_status='pe',
                temp_edited_by=user,
            )

            # ---------------------------
            # 1️⃣ INTERNAL METADATA (from DOCX)
            # ---------------------------
            metadata_list = get_metadata_details(template)

            for item in metadata_list:
                metadata_key = item["metadata_key"]
                metadata_type = item["metadata_type"]
                metadata_description = " ".join(metadata_key.split("_"))

                key_obj, _ = MetadataKey.objects.get_or_create(
                    metadata_key=metadata_key,
                    defaults={
                        "metadata_description": metadata_description,
                        "metadata_type": metadata_type,
                        "external_metadata": False,
                    }
                )

                TemplateMetaData.objects.get_or_create(
                    temp_metadata=template,
                    temp_meta_key=key_obj,
                )

            # ---------------------------
            # 2️⃣ EXTERNAL METADATA (OPTIONAL)
            # ---------------------------
            for item in external_metadata_list:
                metadata_key = item["metadata_key"]
                metadata_type = item.get("metadata_type", "string")
                metadata_description = item.get(
                    "metadata_description",
                    " ".join(metadata_key.split("_"))
                )

                key_obj, created = MetadataKey.objects.get_or_create(
                    metadata_key=metadata_key,
                    defaults={
                        "metadata_description": metadata_description,
                        "metadata_type": metadata_type,
                        "external_metadata": True,
                    }
                )

                # If key already exists but was not marked external
                if not created and not key_obj.external_metadata:
                    key_obj.external_metadata = True
                    key_obj.save(update_fields=["external_metadata"])

                TemplateMetaData.objects.get_or_create(
                    temp_metadata=template,
                    temp_meta_key=key_obj,
                )

            # ---------------------------
            # 3️⃣ ACTIVATE TEMPLATE
            # ---------------------------
            template.temp_status = 'ac'
            template.save(update_fields=["temp_status"])

            return Response(
                {
                    "success": True,
                    "message": "Template Trained Successfully!",
                },
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {
                    "success": False,
                    "errors": str(e),
                },
                status=status.HTTP_400_BAD_REQUEST
            )


class TemplateMetadataViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, pk=None):
        """
        pk = temp_id
        """
        try:
            template = Template.objects.get(temp_id=pk, temp_status='ac')

            metadata_qs = TemplateMetaData.objects.filter(
                temp_metadata=template
            ).select_related('temp_meta_key')

            metadata = []
            for item in metadata_qs:
                key = item.temp_meta_key
                metadata.append({
                    "metadata_key": key.metadata_key,
                    "metadata_type": key.metadata_type,
                    "metadata_description": key.metadata_description,
                })

            return Response({
                "success": True,
                "template_id": template.temp_id,
                "metadata": metadata
            }, status=status.HTTP_200_OK)

        except Template.DoesNotExist:
            return Response({
                "success": False,
                "message": "Template not found"
            }, status=status.HTTP_404_NOT_FOUND)


# class DocumentCreateViewSet(viewsets.ViewSet):
#     permission_classes = [IsAuthenticated]
#
#     def create(self, request):
#         user = request.user
#         template_id = request.data.get("template_id")
#         metadata_values = request.data.get("metadata", {})
#
#         if not template_id:
#             return Response(
#                 {"success": False, "error": "template_id is required"},
#                 status=status.HTTP_400_BAD_REQUEST
#             )
#
#         try:
#             template = Template.objects.get(
#                 temp_id=template_id,
#                 temp_status='ac'
#             )
#         except Template.DoesNotExist:
#             return Response(
#                 {"success": False, "error": "Template not found"},
#                 status=status.HTTP_404_NOT_FOUND
#             )
#
#         # 🔹 Fetch template metadata
#         template_metadata = TemplateMetaData.objects.filter(
#             temp_metadata=template
#         ).select_related("temp_meta_key")
#
#         # 🔹 Validate metadata keys
#         allowed_keys = {
#             tm.temp_meta_key.metadata_key
#             for tm in template_metadata
#         }
#
#         invalid_keys = set(metadata_values.keys()) - allowed_keys
#         if invalid_keys:
#             return Response(
#                 {
#                     "success": False,
#                     "error": f"Invalid metadata keys: {list(invalid_keys)}"
#                 },
#                 status=status.HTTP_400_BAD_REQUEST
#             )
#
#         # 🔹 Create document ID
#         doc_id = datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')
#
#         document = CreatedDocument.objects.create(
#             doc_id=doc_id,
#             document_name=f"{template.temp_title}_{doc_id}",
#             doc_matched_template=template,
#             doc_created_by=user,
#             status='ia',
#             doc_type='docx'
#         )
#
#         # 🔹 Save metadata values
#         for key, value in metadata_values.items():
#             meta_key = MetadataKey.objects.get(metadata_key=key)
#             MetadataValue.objects.create(
#                 meta_key=meta_key,
#                 meta_upload_value=value,
#                 meta_created_doc=document
#             )
#
#         # 🔹 Render document
#         tpl = DocxTemplate(MEDIA_ROOT + '/' + str(template.upload_template))
#         tpl.render(metadata_values)
#
#         file_name = f"{template.temp_title}_{doc_id}.docx"
#         relative_path = f"created_document/{file_name}"
#         absolute_path = os.path.join(MEDIA_ROOT, relative_path)
#
#         # Ensure directory exists
#         os.makedirs(os.path.dirname(absolute_path), exist_ok=True)
#
#         # Save docx
#         tpl.save(absolute_path)
#
#         # Save to DB
#         document.document = relative_path
#         document.status = 'ac'
#         document.save(update_fields=["document", "status"])
#
#         return Response(
#             {
#                 "success": True,
#                 "message": "Document Created Successfully",
#                 "data": {
#                     "doc_id": document.doc_id,
#                     "document_name": document.document_name
#                 }
#             },
#             status=status.HTTP_201_CREATED
#         )


# class DocumentCreateViewSet(viewsets.ViewSet):
#     permission_classes = [IsAuthenticated]
#
#     def create(self, request):
#         user = request.user
#         template_id = request.data.get("template_id")
#         metadata_payload = request.data.get("metadata", {})  # ✅ FIX
#
#         if not template_id:
#             return Response(
#                 {"success": False, "error": "template_id is required"},
#                 status=status.HTTP_400_BAD_REQUEST
#             )
#
#         # 1️⃣ Get template
#         try:
#             template = Template.objects.get(
#                 temp_id=template_id,
#                 temp_status='ac'
#             )
#         except Template.DoesNotExist:
#             return Response(
#                 {"success": False, "error": "Template not found"},
#                 status=status.HTTP_404_NOT_FOUND
#             )
#
#         # 2️⃣ Get template metadata
#         template_metadata = TemplateMetaData.objects.filter(
#             temp_metadata=template
#         ).select_related("temp_meta_key")
#
#         meta_key_map = {
#             tm.temp_meta_key.metadata_key: tm.temp_meta_key
#             for tm in template_metadata
#         }
#
#         # 3️⃣ Create document
#         doc_id = datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')
#
#         document = CreatedDocument.objects.create(
#             doc_id=doc_id,
#             document_name=f"{template.temp_title}_{doc_id}",
#             doc_matched_template=template,
#             doc_created_by=user,
#             status='ia',
#             doc_type='docx'
#         )
#
#         tpl = DocxTemplate(os.path.join(settings.MEDIA_ROOT, str(template.upload_template)))
#
#         context = {}
#
#         # 4️⃣ Process metadata
#         for key, meta_key in meta_key_map.items():
#             meta_type = meta_key.metadata_type
#
#             # 🖼 IMAGE METADATA
#             if meta_type == "image":
#                 if key not in request.FILES:
#                     context[key] = ""
#                     continue
#
#                 image_file = request.FILES[key]
#                 image_path = default_storage.save(f"images/{image_file.name}", image_file)
#
#                 try:
#                     width_mm = float(key.split("_")[-1].replace("mm", ""))
#                 except Exception:
#                     width_mm = 30
#
#                 context[key] = InlineImage(
#                     tpl,
#                     os.path.join(settings.MEDIA_ROOT, image_path),
#                     width=Mm(width_mm)
#                 )
#
#                 MetadataValue.objects.create(
#                     meta_key=meta_key,
#                     meta_upload_value=image_path,
#                     meta_created_doc=document
#                 )
#                 continue
#
#             # 📝 TEXT / DATE / INTEGER / STRING
#             value = metadata_payload.get(key, "")  # ✅ FIX HERE
#
#             context[key] = value
#
#             MetadataValue.objects.create(
#                 meta_key=meta_key,
#                 meta_upload_value=str(value),
#                 meta_created_doc=document
#             )
#
#         # 5️⃣ Render docx
#         tpl.render(context)
#
#         file_name = f"{template.temp_title}_{doc_id}.docx"
#         relative_path = f"created_document/{file_name}"
#         absolute_path = os.path.join(settings.MEDIA_ROOT, relative_path)
#
#         os.makedirs(os.path.dirname(absolute_path), exist_ok=True)
#         tpl.save(absolute_path)
#
#         document.document = relative_path
#         document.status = 'ac'
#         document.save(update_fields=["document", "status"])
#
#         return Response(
#             {
#                 "success": True,
#                 "message": "Document Created Successfully",
#                 "data": {
#                     "doc_id": document.doc_id,
#                     "document_name": document.document_name
#                 }
#             },
#             status=status.HTTP_201_CREATED
#         )


class DocumentCreateViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def extract_metadata(self, request):
        metadata = {}

        if isinstance(request.data.get("metadata"), dict):
            metadata = request.data.get("metadata", {})
        else:
            for key, value in request.data.items():
                if key.startswith("metadata[") and key.endswith("]"):
                    clean_key = key[len("metadata["):-1]
                    metadata[clean_key] = value

        return metadata

    def create(self, request):
        user = request.user
        template_id = request.data.get("template_id")
        metadata_payload = self.extract_metadata(request)  # ✅ SINGLE SOURCE

        if not template_id:
            return Response(
                {"success": False, "error": "template_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            template = Template.objects.get(
                temp_id=template_id,
                temp_status='ac'
            )
        except Template.DoesNotExist:
            return Response(
                {"success": False, "error": "Template not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        template_metadata = TemplateMetaData.objects.filter(
            temp_metadata=template
        ).select_related("temp_meta_key")

        meta_key_map = {
            tm.temp_meta_key.metadata_key: tm.temp_meta_key
            for tm in template_metadata
        }

        doc_id = datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')

        document = CreatedDocument.objects.create(
            doc_id=doc_id,
            document_name=f"{template.temp_title}_{doc_id}",
            doc_matched_template=template,
            doc_created_by=user,
            status='ia',
            doc_type='docx'
        )

        tpl = DocxTemplate(os.path.join(settings.MEDIA_ROOT, str(template.upload_template)))
        context = {}

        for key, meta_key in meta_key_map.items():
            meta_type = meta_key.metadata_type

            # 🖼 IMAGE METADATA
            if meta_type == "image":
                if key not in request.FILES:
                    context[key] = ""
                    continue

                image_file = request.FILES[key]
                image_path = default_storage.save(f"images/{image_file.name}", image_file)

                try:
                    width_mm = float(key.split("_")[-1].replace("mm", ""))
                except Exception:
                    width_mm = 30

                context[key] = InlineImage(
                    tpl,
                    os.path.join(settings.MEDIA_ROOT, image_path),
                    width=Mm(width_mm)
                )

                MetadataValue.objects.create(
                    meta_key=meta_key,
                    meta_upload_value=image_path,
                    meta_created_doc=document
                )
                continue

            # 📝 TEXT / DATE / INTEGER / STRING
            value = metadata_payload.get(key, "")
            context[key] = value

            MetadataValue.objects.create(
                meta_key=meta_key,
                meta_upload_value=str(value),
                meta_created_doc=document
            )

        tpl.render(context)

        file_name = f"{template.temp_title}_{doc_id}.docx"
        relative_path = f"created_document/{file_name}"
        absolute_path = os.path.join(settings.MEDIA_ROOT, relative_path)

        os.makedirs(os.path.dirname(absolute_path), exist_ok=True)
        tpl.save(absolute_path)

        document.document = relative_path
        document.status = 'ac'
        document.save(update_fields=["document", "status"])

        return Response(
            {
                "success": True,
                "message": "Document Created Successfully",
                "data": {
                    "doc_id": document.doc_id,
                    "document_name": document.document_name
                }
            },
            status=status.HTTP_201_CREATED
        )





