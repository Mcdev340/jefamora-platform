from django.http import FileResponse
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.exceptions import APIError
from apps.core.files import resolve_private_file
from apps.core.permissions import IsEmailVerified, IsProfessional
from apps.users.models import User
from apps.verification.models import IdentityDocument
from apps.verification.services import submit_case, upload_document


class VerificationView(APIView):
    permission_classes = [IsProfessional]

    def get(self, request):
        case = request.user.professional_profile.verification_cases.order_by("-submitted_at").first()
        if case is None:
            return Response({"status": "not_submitted", "documents": []})
        return Response(
            {
                "id": str(case.id),
                "status": case.status,
                "admin_comment": case.admin_comment,
                "documents": [
                    {"id": str(item.id), "document_type": item.document_type, "original_name": item.original_name}
                    for item in case.documents.all()
                ],
            }
        )

    def post(self, request):
        if request.FILES.get("file"):
            document = upload_document(
                user=request.user,
                document_type=request.data.get("document_type", IdentityDocument.DocumentType.NATIONAL_ID),
                uploaded=request.FILES["file"],
            )
            return Response({"id": str(document.id)}, status=201)
        case = submit_case(user=request.user)
        return Response({"id": str(case.id), "status": case.status})


class DocumentDownloadView(APIView):
    permission_classes = [IsEmailVerified]

    def get(self, request, document_id):
        document = get_object_or_404(
            IdentityDocument.objects.select_related("case__professional__user"),
            pk=document_id,
        )
        owner = document.case.professional.user_id == request.user.id
        if not owner and request.user.role != User.Role.SUPER_ADMIN:
            raise APIError("forbidden", "Document privé.", status_code=403)
        return FileResponse(resolve_private_file(document.private_file_key).open("rb"), as_attachment=True)
