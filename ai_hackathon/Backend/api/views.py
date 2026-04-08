"""DRF views for the generic multimodal hackathon API."""

from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from api.serializers import KnowledgeEntrySerializer, PromoteKnowledgeSerializer
from api.services import (
    add_manual_knowledge_entry,
    promote_output_to_knowledge,
    run_orchestration_request,
)


class HealthCheckView(APIView):
    """Return a small readiness response for local smoke testing."""

    authentication_classes = []
    permission_classes = []

    def get(self, request):
        """Handle health-check requests."""
        return Response({"status": "ok"})


class ProcessRequestView(APIView):
    """Accept text, audio, and screenshots and return orchestrator output."""

    authentication_classes = []
    permission_classes = []
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        """Process the supplied multimodal input through the orchestrator."""
        # Accept both `text` and `input_text` so the UI team has a forgiving
        # contract while iterating quickly during the hackathon.
        text_input = (request.data.get("text") or request.data.get("input_text") or "").strip()
        audio_file = request.FILES.get("audio")
        image_files = request.FILES.getlist("images") or request.FILES.getlist("screenshots")

        if not text_input and not audio_file and not image_files:
            return Response(
                {"error": "Provide at least one of: text, audio, or images."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            payload = run_orchestration_request(
                text_input=text_input,
                audio_file=audio_file,
                image_files=image_files,
            )
            return Response(payload)
        except Exception as exc:
            return Response(
                {
                    "error": "Processing failed.",
                    "details": str(exc),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class KnowledgeEntryCreateView(APIView):
    """Create a manual reviewed knowledge entry from a form or UI action."""

    authentication_classes = []
    permission_classes = []

    def post(self, request):
        """Validate and store a manual knowledge record."""
        serializer = KnowledgeEntrySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        saved_entry, created = add_manual_knowledge_entry(serializer.validated_data)
        return Response(
            {
                "message": "Knowledge entry added." if created else "Knowledge entry already exists.",
                "entry": saved_entry,
            },
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


class KnowledgePromoteView(APIView):
    """Promote a reviewed model output into the knowledge base."""

    authentication_classes = []
    permission_classes = []

    def post(self, request):
        """Validate and store a promoted output as a knowledge record."""
        serializer = PromoteKnowledgeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        saved_entry, created = promote_output_to_knowledge(serializer.validated_data)
        return Response(
            {
                "message": (
                    "Reviewed output promoted to knowledge."
                    if created
                    else "Reviewed output already exists in knowledge."
                ),
                "entry": saved_entry,
            },
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )
