from django.urls import path

from apps.quotes.api.v1.views import QuoteAcceptView, QuoteCreateView, QuoteRejectView

urlpatterns = [
    path("", QuoteCreateView.as_view(), name="quotes"),
    path("<uuid:quote_id>/accept/", QuoteAcceptView.as_view(), name="quote-accept"),
    path("<uuid:quote_id>/reject/", QuoteRejectView.as_view(), name="quote-reject"),
]
