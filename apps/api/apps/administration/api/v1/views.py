from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.catalog.api.v1.serializers import CategorySerializer, SpecialtySerializer, TradeSerializer, ZoneSerializer
from apps.catalog.models import Category, Specialty, Trade
from apps.core.exceptions import APIError
from apps.core.permissions import IsSuperAdmin
from apps.locations.models import Zone
from apps.moderation.models import Report
from apps.moderation.services import close_report, moderate_target, suspend_user
from apps.support.models import Dispute, SupportTicket
from apps.support.services import close_ticket, resolve_dispute
from apps.users.models import User
from apps.verification.models import VerificationCase
from apps.verification.services import decide_case


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
