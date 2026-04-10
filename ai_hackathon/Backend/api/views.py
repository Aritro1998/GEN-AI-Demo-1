"""DRF views for the insurance policy provider platform."""

from django.http import FileResponse
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.models import PolicyCategory, PolicyDocument
from api.serializers import PolicyCategorySerializer, PolicyQuerySerializer, UserPolicySerializer
from api.policy_services import get_user_policies, ingest_policy_pdf, query_policy
from modules.recommendations import get_recommendations_for_user


class HealthCheckView(APIView):
    """Return a small readiness response for local smoke testing."""

    authentication_classes = []
    permission_classes = []

    def get(self, request):
        """Handle health-check requests."""
        return Response({"status": "ok"})


class PolicyUploadView(APIView):
    """Admin-only: upload a PDF for a specific policy tier."""

    permission_classes = [IsAdminUser]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        """Accept a PDF + tier_id, extract, chunk, and store in DB."""
        tier_id = request.data.get("tier_id")
        pdf_file = request.FILES.get("file")

        if not tier_id:
            return Response(
                {"error": "tier_id is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not pdf_file:
            return Response(
                {"error": "No file provided. Upload a PDF as 'file'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not pdf_file.name.lower().endswith(".pdf"):
            return Response(
                {"error": "Only PDF files are supported."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            result = ingest_policy_pdf(pdf_file, tier_id=int(tier_id))
            return Response(
                {"message": "Policy uploaded and indexed.", **result},
                status=status.HTTP_201_CREATED,
            )
        except Exception as exc:
            return Response(
                {"error": "Policy ingestion failed.", "details": str(exc)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class MyPoliciesView(APIView):
    """Return all active policies for the logged-in user."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        policies = get_user_policies(request.user)
        serializer = UserPolicySerializer(policies, many=True)
        return Response(serializer.data)


class PolicyDetailView(APIView):
    """Return full detail for a single user policy."""

    permission_classes = [IsAuthenticated]

    def get(self, request, policy_id):
        policy = get_user_policies(request.user).filter(pk=policy_id).first()
        if not policy:
            return Response(
                {"error": "Policy not found or not assigned to your account."},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = UserPolicySerializer(policy)
        return Response(serializer.data)


class PolicyDocumentDownloadView(APIView):
    """Download the PDF document for a user's policy."""

    permission_classes = [IsAuthenticated]

    def get(self, request, policy_id):
        policy = get_user_policies(request.user).filter(pk=policy_id).first()
        if not policy:
            return Response(
                {"error": "Policy not found or not assigned to your account."},
                status=status.HTTP_404_NOT_FOUND,
            )

        doc = PolicyDocument.objects.filter(tier=policy.tier, pdf_file__isnull=False).exclude(pdf_file="").first()
        if not doc or not doc.pdf_file:
            return Response(
                {"error": "No document available for this policy."},
                status=status.HTTP_404_NOT_FOUND,
            )

        return FileResponse(
            doc.pdf_file.open("rb"),
            content_type="application/pdf",
            as_attachment=False,
            filename=doc.file_name,
        )


class ScopedPolicyQueryView(APIView):
    """Answer a question scoped to a specific user policy."""

    permission_classes = [IsAuthenticated]

    def post(self, request, policy_id):
        serializer = PolicyQuerySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Verify the policy belongs to this user
        policy = get_user_policies(request.user).filter(pk=policy_id).first()
        if not policy:
            return Response(
                {"error": "Policy not found or not assigned to your account."},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            result = query_policy(
                user=request.user,
                question=serializer.validated_data["question"],
                user_policy_id=policy_id,
                chat_history=serializer.validated_data.get("chat_history", []),
            )
            return Response(result)
        except Exception as exc:
            return Response(
                {"error": "Query failed.", "details": str(exc)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class OfferingsView(APIView):
    """Return all policy categories and their tiers — public."""

    authentication_classes = []
    permission_classes = []

    def get(self, request):
        categories = PolicyCategory.objects.prefetch_related("tiers").all()
        data = []
        for cat in categories:
            tiers = cat.tiers.order_by("name").all()
            data.append({
                "id": cat.id,
                "name": cat.name,
                "description": cat.description,
                "icon": cat.icon,
                "tiers": [
                    {
                        "id": t.id,
                        "name": t.name,
                        "display_name": t.display_name,
                        "price_monthly": float(t.price_monthly) if t.price_monthly else None,
                        "highlights": t.highlights,
                    }
                    for t in tiers
                ],
            })
        return Response({"categories": data})


class DashboardView(APIView):
    """Combined dashboard: user info + policies + recommendation count."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        policies = get_user_policies(user)
        policy_data = UserPolicySerializer(policies, many=True).data

        # Lightweight recommendation summary (no LLM call)
        from modules.recommendations import (
            get_loan_recommendations,
            get_upgrade_recommendations,
        )
        upgrades = get_upgrade_recommendations(policies)
        loans = get_loan_recommendations(policies)

        return Response({
            "user": {
                "user_id": user.pk,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
            },
            "policies": policy_data,
            "recommendation_summary": {
                "upgrade_count": len(upgrades),
                "loan_count": len(loans),
                "total": len(upgrades) + len(loans),
            },
        })


class RecommendationsView(APIView):
    """Return personalised upgrade and loan recommendations for the user."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            recs = get_recommendations_for_user(request.user)
            return Response({"recommendations": recs})
        except Exception as exc:
            return Response(
                {"error": "Failed to generate recommendations.", "details": str(exc)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class PolicyQueryView(APIView):
    """Answer a question about the user's assigned policies."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Retrieve relevant chunks from user's policies and generate an answer."""
        serializer = PolicyQuerySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            result = query_policy(
                user=request.user,
                question=serializer.validated_data["question"],
                user_policy_id=serializer.validated_data.get("user_policy_id"),
                chat_history=serializer.validated_data.get("chat_history", []),
            )
            return Response(result)
        except Exception as exc:
            return Response(
                {"error": "Query failed.", "details": str(exc)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
