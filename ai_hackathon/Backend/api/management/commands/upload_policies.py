"""Upload policy PDFs from the Policy Plan folder to all seeded tiers."""

from pathlib import Path

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.db import transaction

from api.models import PolicyChunk, PolicyDocument, PolicyTier
from api.policy_services import ingest_policy_pdf_from_path


# Map (category_name, tier_name) → relative PDF path under "Policy Plan/"
TIER_PDF_MAP = {
    # ── Vehicle Insurance → Car ──────────────────────────────────────
    ("Car", "silver"): "Vehicle Insurance/DriveSecure_Basic_Plan.pdf",
    ("Car", "gold"): "Vehicle Insurance/AutoShield_Premium_Plan.pdf",
    ("Car", "platinum"): "Vehicle Insurance/Infinity_MotorLife_Supreme_Plan.pdf",
    # ── Health Insurance ─────────────────────────────────────────────
    ("Health", "silver"): "Health Insurance/Silver_Health_Insurance_Plan.pdf",
    ("Health", "gold"): "Health Insurance/Gold_Health_Insurance_Plan.pdf",
    ("Health", "platinum"): "Health Insurance/Platinum_Health_Insurance_Plan.pdf",
    # ── Life Insurance ───────────────────────────────────────────────
    ("Life", "silver"): "Life Insurance/LifeSecure_Basic_Plan.pdf",
    ("Life", "gold"): "Life Insurance/WealthBuilder_Life_Plan.pdf",
    ("Life", "platinum"): "Life Insurance/EliteLegacy_Life_Plan.pdf",
}


class Command(BaseCommand):
    help = "Upload policy PDFs from the Policy Plan folder for every tier."

    def handle(self, *args, **options):
        # Policy Plan folder sits next to Backend/
        base_dir = Path(__file__).resolve().parent.parent.parent.parent.parent
        plan_dir = base_dir / "Policy Plan"

        if not plan_dir.exists():
            self.stderr.write(self.style.ERROR(f"Policy Plan folder not found at {plan_dir}"))
            return

        uploaded = 0
        skipped = 0

        for (cat_name, tier_name), rel_path in TIER_PDF_MAP.items():
            pdf_path = plan_dir / rel_path

            if not pdf_path.exists():
                self.stderr.write(self.style.WARNING(f"  SKIP {rel_path} — file not found"))
                skipped += 1
                continue

            tier = PolicyTier.objects.filter(
                category__name=cat_name, name=tier_name,
            ).first()

            if not tier:
                self.stderr.write(self.style.WARNING(
                    f"  SKIP {cat_name} {tier_name} — tier not found in DB (run seed_demo first)"
                ))
                skipped += 1
                continue

            self.stdout.write(f"  Uploading {rel_path} → {tier} ...")

            result = ingest_policy_pdf_from_path(pdf_path, tier.pk)

            self.stdout.write(self.style.SUCCESS(
                f"    ✓ {result['pages_extracted']} pages, "
                f"{result['chunks_created']} chunks"
            ))
            uploaded += 1

        self.stdout.write(self.style.SUCCESS(
            f"\nDone. Uploaded {uploaded} PDFs, skipped {skipped}."
        ))
