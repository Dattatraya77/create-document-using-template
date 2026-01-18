import re
from django.conf import settings
from docx2python import docx2python


def get_metadata_details(template_document):
    path = settings.MEDIA_ROOT + '/' + str(template_document.upload_template)
    document = docx2python(path, html=False)
    full_text = document.text

    # 🔹 Extract text inside {{ }}
    raw_keys = re.findall(r'{{\s*(.*?)\s*}}', full_text)

    metadata_details = []
    seen_keys = set()

    for raw_key in raw_keys:
        key = raw_key.replace(" ", "")

        if key in seen_keys:
            continue
        seen_keys.add(key)

        # 🖼 IMAGE METADATA → ends with _XXmm
        if re.search(r'_\d+mm$', key):
            metadata_type = "image"

        # 🧠 OTHER TYPES (suffix-based)
        elif "_" in key:
            metadata_type = key.split("_")[-1]

        else:
            metadata_type = "string"

        metadata_details.append({
            "metadata_key": key,
            "metadata_type": metadata_type
        })

    return metadata_details
