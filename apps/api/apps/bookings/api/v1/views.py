from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.bookings.api.v1.serializers import BookingSerializer
from apps.bookings.services import (
    confirm_completion,
    request_completion,
    start_booking,
    visible_bookings,
)
from apps.core.exceptions import APIError
from apps.core.pagination import DefaultPagination
from apps.core.permissions import IsClient, IsEmailVerified, IsProfessional
from apps.support.services import open_dispute


class BookingListView(APIView):
    permission_classes = [IsEmailVerified]

    def get(self, request):
        paginator = DefaultPagination()
        page = paginator.paginate_queryset(visible_bookings(request.user), request)
        return paginator.get_paginated_response(BookingSerializer(page, many=True).data)


class BookingDetailView(APIView):
    permission_classes = [IsEmailVerified]

    def get(self, request, booking_id):
        booking = get_object_or_404(visible_bookings(request.user), pk=booking_id)
        return Response(BookingSerializer(booking).data)


class BookingStartView(APIView):
    permission_classes = [IsProfessional]

    def post(self, request, booking_id):
        booking = start_booking(booking_id=booking_id, user=request.user)
        return Response(BookingSerializer(booking).data)


class BookingRequestCompletionView(APIView):
    permission_classes = [IsProfessional]

    def post(self, request, booking_id):
        booking = request_completion(booking_id=booking_id, user=request.user)
        return Response(BookingSerializer(booking).data)


class BookingConfirmCompletionView(APIView):
    permission_classes = [IsClient]

    def post(self, request, booking_id):
        booking = confirm_completion(booking_id=booking_id, user=request.user)
        return Response(BookingSerializer(booking).data)


class BookingDisputeView(APIView):
    permission_classes = [IsEmailVerified]

    def post(self, request, booking_id):
        booking = get_object_or_404(visible_bookings(request.user).select_related("client__user", "professional__user"), pk=booking_id)
        dispute = open_dispute(booking=booking, user=request.user, description=request.data.get("description", ""))
        return Response({"id": str(dispute.id), "status": dispute.status}, status=201)


