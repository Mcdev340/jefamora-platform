from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.bookings.api.v1.serializers import ReviewReplySerializer, ReviewSerializer
from apps.core.exceptions import APIError
from apps.core.permissions import IsClient, IsEmailVerified
from apps.notifications.services import notify
from apps.reviews.models import Review


class ReviewCreateView(APIView):
    permission_classes = [IsClient]

    def post(self, request):
        serializer = ReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        booking = serializer.validated_data["booking"]
        if booking.client.user_id != request.user.id:
            raise APIError("forbidden", "Vous ne pouvez noter que votre mission.", status_code=403)
        review = Review(
            booking_id=booking.id,
            rating=serializer.validated_data["rating"],
            comment=serializer.validated_data.get("comment", ""),
        )
        review.save()
        notify(
            recipient=review.booking.professional.user,
            kind="review_received",
            title="Nouvel avis",
            body=review.comment[:180],
            payload={"review_id": str(review.id)},
        )
        return Response(ReviewSerializer(review).data, status=201)


class ReviewDetailView(APIView):
    permission_classes = [IsEmailVerified]

    def patch(self, request, review_id):
        review = get_object_or_404(
            Review.objects.select_related("booking__client__user", "booking__professional__user"),
            pk=review_id,
        )
        if request.user.id == review.booking.client.user_id:
            if "rating" in request.data:
                review.rating = request.data["rating"]
            if "comment" in request.data:
                review.comment = request.data["comment"]
        elif request.user.id == review.booking.professional.user_id:
            reply = ReviewReplySerializer(data=request.data)
            reply.is_valid(raise_exception=True)
            review.professional_reply = reply.validated_data["professional_reply"]
        else:
            raise APIError("forbidden", "Vous ne pouvez pas modifier cet avis.", status_code=403)
        review.save()
        return Response(ReviewSerializer(review).data)
