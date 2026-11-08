from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.exceptions import APIError
from apps.core.pagination import DefaultPagination
from apps.core.permissions import IsClient, IsEmailVerified, IsProfessional
from apps.quotes.models import Quote
from apps.service_requests.api.v1.serializers import (
    DeclineSerializer,
    QuoteSerializer,
    ServiceRequestCreateSerializer,
    ServiceRequestSerializer,
)
from apps.service_requests.models import ServiceRequest
from apps.service_requests.services import (
    add_attachment,
    cancel_service_request,
    create_service_request,
    decline_request,
    requests_for_user,
    update_service_request,
)


class ServiceRequestListCreateView(APIView):
    def get_permissions(self):
        if self.request.method == "POST":
            return [IsClient()]
        return [IsEmailVerified()]

    def get(self, request):
        queryset = requests_for_user(request.user)
        paginator = DefaultPagination()
        page = paginator.paginate_queryset(queryset, request)
        return paginator.get_paginated_response(ServiceRequestSerializer(page, many=True).data)

    def post(self, request):
        serializer = ServiceRequestCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        service_request = create_service_request(
            client_user=request.user,
            zone_id=data["zone"],
            title=data["title"],
            description=data["description"],
            professional_ids=data["professional_ids"],
            urgency=data.get("urgency", ServiceRequest.Urgency.NORMAL),
            budget=data.get("budget"),
            desired_date=data.get("desired_date"),
        )
        return Response(ServiceRequestSerializer(service_request).data, status=201)


class ServiceRequestDetailView(APIView):
    permission_classes = [IsEmailVerified]

    def get_object(self, request, request_id):
        service_request = get_object_or_404(requests_for_user(request.user), pk=request_id)
        return service_request

    def get(self, request, request_id):
        return Response(ServiceRequestSerializer(self.get_object(request, request_id)).data)

    def patch(self, request, request_id):
        service_request = self.get_object(request, request_id)
        changes = {
            key: request.data[key]
            for key in ("title", "description", "urgency", "budget", "desired_date")
            if key in request.data
        }
        updated = update_service_request(
            service_request=service_request,
            client_user=request.user,
            changes=changes,
        )
        return Response(ServiceRequestSerializer(updated).data)


class ServiceRequestCancelView(APIView):
    permission_classes = [IsClient]

    def post(self, request, request_id):
        service_request = get_object_or_404(ServiceRequest, pk=request_id)
        updated = cancel_service_request(service_request=service_request, client_user=request.user)
        return Response(ServiceRequestSerializer(updated).data)


class ServiceRequestDeclineView(APIView):
    permission_classes = [IsProfessional]

    def post(self, request, request_id):
        serializer = DeclineSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        decline_request(
            professional_user=request.user,
            service_request_id=request_id,
            reason=serializer.validated_data.get("reason", ""),
        )
        service_request = get_object_or_404(requests_for_user(request.user), pk=request_id)
        return Response(ServiceRequestSerializer(service_request).data)


class ServiceRequestAttachmentView(APIView):
    permission_classes = [IsClient]

    def post(self, request, request_id):
        service_request = get_object_or_404(ServiceRequest, pk=request_id)
        uploaded = request.FILES.get("file")
        if uploaded is None:
            raise APIError("validation_error", "Fichier manquant.", fields={"file": ["Obligatoire."]})
        attachment = add_attachment(service_request=service_request, user=request.user, uploaded=uploaded)
        return Response({"id": str(attachment.id), "file_key": attachment.file_key}, status=201)


class ServiceRequestQuoteListView(APIView):
    permission_classes = [IsEmailVerified]

    def get(self, request, request_id):
        service_request = get_object_or_404(requests_for_user(request.user), pk=request_id)
        quotes = Quote.objects.filter(service_request=service_request).prefetch_related("lines")
        if request.user.role == "client":
            quotes = quotes.exclude(status=Quote.Status.DRAFT)
        elif request.user.role == "professional":
            quotes = quotes.filter(recipient__professional__user=request.user)
        return Response(QuoteSerializer(quotes, many=True).data)


