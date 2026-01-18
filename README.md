📄 Create Document Using docx Template

A Django REST Framework–based system to train document templates, extract dynamic metadata, and generate documents (DOCX) using JSON or multipart form-data, including image placeholders like company logos and signatures.

🚀 Key Features

📑 Upload & train DOCX templates

🔍 Auto-detect metadata placeholders ({{ variable_name }})

🖼 Image metadata support using _XXmm suffix

🧾 Create documents using:

application/json (raw data)

multipart/form-data (file + text)

🔐 Authentication-protected APIs

🗂 Metadata stored per generated document

🧠 Template Placeholder Rules
Text Metadata

{{ Employee_name_string }}
{{ Reference_integer }}
{{ Joining_date_date }}

Image Metadata (Auto-detected)
{{ company_logo_30mm }}
{{ company_signature_40mm }}

➡️ Any placeholder ending with _XXmm is automatically treated as:

metadata_type = "image"

🧩 Metadata Type Mapping

| Suffix           | Metadata Type |
| ---------------- | ------------- |
| `_string`        | String        |
| `_integer`       | Integer       |
| `_date`          | Date          |
| `_bool`          | Boolean       |
| `_textarea`      | TextArea      |
| `_choice`        | Choice        |
| `_30mm`, `_40mm` | Image         |

📦 Installed Tech Stack

Python 3.8+

Django

Django REST Framework

docxtpl

PostgreSQL / SQLite

JWT / Session Authentication

🔗 API Routes

router = routers.DefaultRouter()
router.register(r'template-train', TemplateTrainViewSet, basename='template-train')
router.register(r'get-template-metadata', TemplateMetadataViewSet, basename='get-template-metadata')
router.register(r'create-document', DocumentCreateViewSet, basename='create-document')

1️⃣ Train Template API
➤ Upload DOCX & Extract Metadata

Endpoint
POST /api/template-train/

Headers
Authorization: Bearer <token>
Content-Type: multipart/form-data

Form-Data
| Key              | Value                      |
| ---------------- | -------------------------- |
| temp_id          | TEMP-1001                  |
| temp_title       | Employment Agreement       |
| temp_description | Employee contract template |
| upload_template  | employment.docx            |

Response
{
  "temp_id": "TEMP-1001",
  "temp_title": "Employment Agreement",
  "external_metadata": [
    {
      "metadata_key": "company_logo_30mm",
      "metadata_type": "image"
    },
    {
      "metadata_key": "Employee_name_string",
      "metadata_type": "string"
    }
  ]
}

2️⃣ Get Template Metadata
➤ Fetch Metadata for UI / Client

Endpoint
GET /api/get-template-metadata/?template_id=TEMP-1001

Response

{
  "template_id": "TEMP-1001",
  "metadata": [
    {
      "key": "Employee_name_string",
      "type": "string"
    },
    {
      "key": "company_logo_30mm",
      "type": "image"
    }
  ]
}

3️⃣ Create Document (Form-Data)
➤ Used when images/signatures are required

Endpoint
POST /api/create-document/

Headers
Authorization: Bearer <token>
Content-Type: multipart/form-data

📌 Postman Form-Data Example

| Key                                  | Value             |
| ------------------------------------ | ----------------- |
| template_id                          | TEMP-1002         |
| metadata[Reference_integer]          | 12345             |
| metadata[Reference_date]             | 2026-01-18        |
| metadata[Employee_name_string]       | Dattatraya Walunj |
| metadata[Employee_position_string]   | Python Developer  |
| metadata[Joining_date]               | 2025-12-12        |
| metadata[Ending_date]                | 2027-01-25        |
| metadata[Company_signatory_string]   | John Doe          |
| metadata[Company_designation_string] | HR                |
| company_logo_30mm                    | 📎 logo.png       |
| company_signature_40mm               | 📎 sign.png       |

📝 Image keys must match template placeholder name exactly

4️⃣ Create Document (Raw JSON)
➤ Used when no file upload is required

Endpoint
POST /api/create-document/

Headers
Authorization: Bearer <token>
Content-Type: application/json

Body

{
  "template_id": "TEMP-1001",
  "metadata": {
    "Effective_date_date": "2026-01-18",
    "Company_name_string": "Virtualwebs Servers PVT LTD",
    "State_of_incorporation_string": "Goa",
    "Individual_party_name_string": "Dattatraya Walunj",
    "Street_address_of_individual_party_textarea": "Margaon, Goa, Pin-411033",
    "Disclosure_days_integer": "45",
    "Duration_of_contract_years_string": "Ten",
    "Duration_of_contract_years_integer": "10",
    "Termination_notice_days_integer": "20",
    "Company_signatory_name_string": "Smita Keni",
    "Title_of_company_signatory_string": "CEO",
    "Title_of_individual_string": "Python Developer",
    "Lawyer_name": "John Doe",
    "Document_type": "Agreement"
  }
}

✅ Success Response

{
  "success": true,
  "message": "Document Created Successfully",
  "data": {
    "doc_id": "202601181245309999",
    "document_name": "Employment_Agreement_202601181245309999"
  }
}

Generated file stored at:

/media/created_document/

🧱 Internal Architecture

Template
 └── TemplateMetaData
       └── MetadataKey
             └── MetadataValue
                   └── CreatedDocument

Each generated document has its own metadata snapshot.
🧪 Postman Testing Tips

✅ Use form-data when uploading images

✅ Use raw JSON for text-only templates

❌ Do not send images inside JSON

🔑 Always pass Authorization header

🛡 Permissions

All APIs require authentication

Templates must be in Active (ac) status

👨‍💻 Author

Dattatraya Walunj

Django | DRF | Workflow Automation



