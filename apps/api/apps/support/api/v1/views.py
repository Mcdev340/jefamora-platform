from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.exceptions import APIError
from apps.core.permissions import IsEmailVerified
from apps.support.models import Dispute, SupportTicket
from apps.support.services import add_evidence, open_ticket


class SupportTicketView(APIView):
    permission_classes = [IsEmailVerified]

    def get(self, request):
        tickets = SupportTicket.objects.filter(opened_by=request.user)
        return Response(
            [
                {"id": str(item.id), "subject": item.subject, "status": item.status, "priority": item.priority}
                for item in tickets
            ]
        )

    def post(self, request):
        ticket = open_ticket(
            user=request.user,
            subject=request.data.get("subject", ""),
            description=request.data.get("description", ""),
            priority=request.data.get("priority", SupportTicket.Priority.NORMAL),
        )
        return Response({"id": str(ticket.id)}, status=201)


class DisputeEvidenceView(APIView):
    permission_classes = [IsEmailVerified]

    def post(self, request, dispute_id):
        dispute = get_object_or_404(
            Dispute.objects.select_related("booking__client", "booking__professional"),
            pk=dispute_id,
        )
        uploaded = request.FILES.get("file")
        if uploaded is None:
            raise APIError("validation_error", "Fichier manquant.", fields={"file": ["Obligatoire."]})
        evidence = add_evidence(dispute=dispute, user=request.user, uploaded=uploaded)
        return Response({"id": str(evidence.id), "file_key": evidence.file_key}, status=201)
