from django.shortcuts import get_object_or_404
from rest_framework import generics, serializers
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.analytics.selectors import platform_stats, record_export
from apps.audit.models import AuditLog
from apps.catalog.api.v1.serializers import CategorySerializer, SpecialtySerializer, TradeSerializer, ZoneSerializer
from apps.catalog.models import Category, Specialty, Trade
from apps.clients.models import Address, Favorite
from apps.professionals.models import ProfessionalProfile
from apps.core.exceptions import APIError
from apps.core.files import resolve_private_file
from apps.core.permissions import IsClient, IsEmailVerified, IsProfessional, IsSuperAdmin
from apps.identity.models import User
from apps.locations.models import Zone
from apps.moderation.models import Report
from apps.moderation.services.actions import (
    block_user,
    close_report,
    file_report,
    moderate_target,
    suspend_user,
    unblock_user,
)
from apps.notifications.models import Notification
from apps.privacy.models import DataDeletionRequest
from apps.privacy.services.requests import grant_consent, request_deletion
from apps.support.models import Dispute, SupportTicket
from apps.support.services.cases import close_ticket, open_ticket, resolve_dispute
from apps.verification.models import IdentityDocument, VerificationCase
from apps.verification.services.cases import decide_case, submit_case, upload_document
from django.http import FileResponse


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ("id", "label", "city", "district", "latitude", "longitude")


class AddressListView(generics.ListCreateAPIView):
    permission_classes = [IsClient]
    serializer_class = AddressSerializer

    def get_queryset(self):
        return Address.objects.filter(client=self.request.user.client_profile)

    def perform_create(self, serializer):
        serializer.save(client=self.request.user.client_profile)


class AddressDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsClient]
    serializer_class = AddressSerializer

    def get_queryset(self):
        return Address.objects.filter(client=self.request.user.client_profile)


class FavoriteView(APIView):
    permission_classes = [IsClient]

    def get(self, request):
        favorites = Favorite.objects.filter(client=request.user.client_profile).select_related("professional")
        return Response(
            [
                {"id": str(item.id), "professional": str(item.professional_id), "name": item.professional.business_name}
                for item in favorites
            ]
        )

    def post(self, request):
        professional = get_object_or_404(ProfessionalProfile, pk=request.data.get("professional"))
        favorite, _created = Favorite.objects.get_or_create(
            client=request.user.client_profile,
            professional=professional,
        )
        return Response({"id": str(favorite.id)}, status=201)

    def delete(self, request):
        Favorite.objects.filter(
            client=request.user.client_profile,
            professional_id=request.data.get("professional"),
        ).delete()
        return Response(status=204)


class ReportView(APIView):
    permission_classes = [IsEmailVerified]

    def post(self, request):
        report = file_report(
            reporter=request.user,
            target_type=request.data.get("target_type"),
            target_id=request.data.get("target_id"),
            reason=request.data.get("reason", Report.Reason.OTHER),
            description=request.data.get("description", ""),
        )
        return Response({"id": str(report.id), "status": report.status}, status=201)


class BlockView(APIView):
    permission_classes = [IsEmailVerified]

    def post(self, request):
        block = block_user(blocker=request.user, blocked_id=request.data["user"])
        return Response({"id": str(block.id)}, status=201)

    def delete(self, request):
        unblock_user(blocker=request.user, blocked_id=request.data["user"])
        return Response(status=204)


class NotificationListView(APIView):
    permission_classes = [IsEmailVerified]

    def get(self, request):
        notes = Notification.objects.filter(recipient=request.user)[:50]
        return Response(
            [
                {
                    "id": str(item.id),
                    "kind": item.kind,
                    "title": item.title,
                    "body": item.body,
                    "is_read": item.is_read,
                    "created_at": item.created_at,
                }
                for item in notes
            ]
        )


class NotificationReadView(APIView):
    permission_classes = [IsEmailVerified]

    def post(self, request, notification_id):
        updated = Notification.objects.filter(recipient=request.user, pk=notification_id).update(is_read=True)
        if not updated:
            raise APIError("not_found", "Notification introuvable.", status_code=404)
        return Response(status=204)


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
        document = get_object_or_404(IdentityDocument.objects.select_related("case__professional__user"), pk=document_id)
        owner = document.case.professional.user_id == request.user.id
        if not owner and request.user.role != User.Role.SUPER_ADMIN:
            raise APIError("forbidden", "Document privé.", status_code=403)
        return FileResponse(resolve_private_file(document.private_file_key).open("rb"), as_attachment=True)


class SupportTicketView(APIView):
    permission_classes = [IsEmailVerified]

    def get(self, request):
        tickets = SupportTicket.objects.filter(opened_by=request.user)
        return Response(
            [{"id": str(item.id), "subject": item.subject, "status": item.status, "priority": item.priority} for item in tickets]
        )

    def post(self, request):
        ticket = open_ticket(
            user=request.user,
            subject=request.data.get("subject", ""),
            description=request.data.get("description", ""),
            priority=request.data.get("priority", SupportTicket.Priority.NORMAL),
        )
        return Response({"id": str(ticket.id)}, status=201)


class ConsentView(APIView):
    permission_classes = [IsEmailVerified]

    def post(self, request):
        consent = grant_consent(
            user=request.user,
            code=request.data.get("code", "privacy"),
            granted=bool(request.data.get("granted", True)),
            version=request.data.get("version", "v1"),
        )
        return Response({"id": str(consent.id)}, status=201)


class DeletionView(APIView):
    permission_classes = [IsEmailVerified]

    def get(self, request):
        items = DataDeletionRequest.objects.filter(user=request.user)
        return Response([{"id": str(item.id), "status": item.status, "created_at": item.created_at} for item in items])

    def post(self, request):
        deletion = request_deletion(user=request.user, reason=request.data.get("reason", ""))
        return Response({"id": str(deletion.id), "status": deletion.status}, status=201)


class InactiveModuleView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        raise APIError("module_inactive", "Ce module sera activé après financement.", status_code=403)

    post = get


class AdminAuditView(APIView):
    permission_classes = [IsSuperAdmin]

    def get(self, request):
        logs = AuditLog.objects.select_related("actor").order_by("-created_at")[:100]
        return Response(
            [
                {
                    "id": str(item.id),
                    "action": item.action,
                    "actor": item.actor.email if item.actor_id else None,
                    "target_type": item.target_type,
                    "target_id": str(item.target_id) if item.target_id else None,
                    "created_at": item.created_at,
                }
                for item in logs
            ]
        )


class AdminStatsView(APIView):
    permission_classes = [IsSuperAdmin]

    def get(self, request):
        return Response(platform_stats())


class AdminExportView(APIView):
    permission_classes = [IsSuperAdmin]

    def post(self, request):
        export = record_export(admin=request.user, export_type=request.data.get("export_type", "platform"))
        return Response({"id": str(export.id), "payload": export.payload}, status=201)


class AdminVerificationListView(APIView):
    permission_classes = [IsSuperAdmin]

    def get(self, request):
        cases = VerificationCase.objects.select_related("professional").order_by("-submitted_at")
        status = request.query_params.get("status")
        if status:
            cases = cases.filter(status=status)
        return Response(
            [
                {
                    "id": str(item.id),
                    "professional": item.professional.business_name,
                    "status": item.status,
                    "submitted_at": item.submitted_at,
                }
                for item in cases[:100]
            ]
        )


class AdminVerificationDecisionView(APIView):
    permission_classes = [IsSuperAdmin]

    def post(self, request, case_id, decision):
        case = get_object_or_404(VerificationCase, pk=case_id)
        aliases = {
            "approve": "approved",
            "approved": "approved",
            "complement": "needs_complement",
            "needs_complement": "needs_complement",
            "reject": "rejected",
            "rejected": "rejected",
        }
        mapped = aliases.get(decision)
        if mapped is None:
            raise APIError("validation_error", "Décision inconnue.")
        updated = decide_case(
            case=case,
            admin=request.user,
            decision=mapped,
            comment=request.data.get("comment", ""),
        )
        return Response({"id": str(updated.id), "status": updated.status})


class AdminReportListView(APIView):
    permission_classes = [IsSuperAdmin]

    def get(self, request):
        reports = Report.objects.select_related("reporter").order_by("-created_at")[:100]
        return Response(
            [
                {
                    "id": str(item.id),
                    "target_type": item.target_type,
                    "target_id": str(item.target_id),
                    "reason": item.reason,
                    "status": item.status,
                    "description": item.description,
                }
                for item in reports
            ]
        )


class AdminReportDetailView(APIView):
    permission_classes = [IsSuperAdmin]

    def get(self, request, report_id):
        report = get_object_or_404(Report, pk=report_id)
        return Response(
            {
                "id": str(report.id),
                "reporter": report.reporter.email,
                "target_type": report.target_type,
                "target_id": str(report.target_id),
                "reason": report.reason,
                "description": report.description,
                "status": report.status,
            }
        )


class AdminReportCloseView(APIView):
    permission_classes = [IsSuperAdmin]

    def post(self, request, report_id):
        report = get_object_or_404(Report, pk=report_id)
        close_report(report=report, admin=request.user)
        return Response({"status": report.status})


class AdminModerationView(APIView):
    permission_classes = [IsSuperAdmin]

    def post(self, request):
        report = None
        if request.data.get("report_id"):
            report = get_object_or_404(Report, pk=request.data["report_id"])
        action = moderate_target(
            admin=request.user,
            target_type=request.data["target_type"],
            target_id=request.data["target_id"],
            action=request.data.get("action", "hide"),
            reason=request.data.get("reason", ""),
            report=report,
        )
        return Response({"id": str(action.id)}, status=201)


class AdminUserStateView(APIView):
    permission_classes = [IsSuperAdmin]

    def post(self, request, user_id, active):
        user = get_object_or_404(User, pk=user_id)
        suspend_user(admin=request.user, user=user, active=active)
        return Response({"id": str(user.id), "is_active": user.is_active})


class AdminDisputeListView(APIView):
    permission_classes = [IsSuperAdmin]

    def get(self, request):
        disputes = Dispute.objects.select_related("booking").order_by("-opened_at")[:100]
        return Response(
            [{"id": str(item.id), "booking": str(item.booking_id), "status": item.status, "description": item.description} for item in disputes]
        )


class AdminDisputeDetailView(APIView):
    permission_classes = [IsSuperAdmin]

    def get(self, request, dispute_id):
        dispute = get_object_or_404(Dispute.objects.prefetch_related("evidence"), pk=dispute_id)
        return Response(
            {
                "id": str(dispute.id),
                "status": dispute.status,
                "description": dispute.description,
                "resolution": dispute.resolution,
                "evidence": [item.file_key for item in dispute.evidence.all()],
            }
        )


class AdminDisputeResolveView(APIView):
    permission_classes = [IsSuperAdmin]

    def post(self, request, dispute_id):
        dispute = get_object_or_404(Dispute, pk=dispute_id)
        resolve_dispute(
            dispute=dispute,
            admin=request.user,
            resolution=request.data.get("resolution", ""),
            booking_status=request.data.get("booking_status"),
        )
        return Response({"status": dispute.status})


class AdminTicketCloseView(APIView):
    permission_classes = [IsSuperAdmin]

    def get(self, request):
        tickets = SupportTicket.objects.order_by("-created_at")[:100]
        return Response([{"id": str(item.id), "subject": item.subject, "status": item.status} for item in tickets])

    def post(self, request, ticket_id):
        ticket = get_object_or_404(SupportTicket, pk=ticket_id)
        close_ticket(ticket=ticket, admin=request.user)
        return Response({"status": ticket.status})


class AdminCatalogView(generics.ListCreateAPIView):
    permission_classes = [IsSuperAdmin]

    def get_queryset(self):
        return _catalog(self.kwargs["kind"]).objects.all()

    def get_serializer_class(self):
        return _catalog_serializer(self.kwargs["kind"])


class AdminCatalogDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsSuperAdmin]

    def get_queryset(self):
        return _catalog(self.kwargs["kind"]).objects.all()

    def get_serializer_class(self):
        return _catalog_serializer(self.kwargs["kind"])


def _catalog(kind):
    mapping = {"categories": Category, "trades": Trade, "specialties": Specialty, "zones": Zone}
    model = mapping.get(kind)
    if model is None:
        raise APIError("not_found", "Référentiel inconnu.", status_code=404)
    return model


def _catalog_serializer(kind):
    _catalog(kind)
    return {
        "categories": CategorySerializer,
        "trades": TradeSerializer,
        "specialties": SpecialtySerializer,
        "zones": ZoneSerializer,
    }[kind]
