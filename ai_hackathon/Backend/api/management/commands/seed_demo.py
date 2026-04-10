"""Seed the database with demo categories, tiers, users, and policy assignments."""

from datetime import date, timedelta

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from api.models import PolicyCategory, PolicyTier, UserPolicy


class Command(BaseCommand):
    help = "Create demo categories, tiers, users, and assign policies."

    def handle(self, *args, **options):
        # ── Categories ────────────────────────────────────────────────
        categories = {
            "Car": {
                "description": "Motor vehicle insurance covering third-party liability, damage, and theft.",
                "icon": "car",
            },
            "Health": {
                "description": "Medical and health insurance for hospitalisation, surgery, and prescriptions.",
                "icon": "health",
            },
            "Life": {
                "description": "Life insurance providing financial protection for family, income, and legacy.",
                "icon": "life",
            },
        }

        cat_objs = {}
        for name, info in categories.items():
            obj, created = PolicyCategory.objects.get_or_create(
                name=name, defaults=info,
            )
            cat_objs[name] = obj
            status = "created" if created else "exists"
            self.stdout.write(f"  Category '{name}' — {status}")

        # ── Tiers per category ────────────────────────────────────────
        tier_defs = [
            ("silver", "Basic cover with essential protections.", 999),
            ("gold", "Enhanced cover with wider protections and lower excess.", 1999),
            ("platinum", "Comprehensive cover with full protection and zero excess.", 3499),
        ]

        tier_objs = {}
        for cat_name, cat_obj in cat_objs.items():
            for tier_name, highlights, price in tier_defs:
                display = f"{cat_name} {tier_name.title()}"
                obj, created = PolicyTier.objects.get_or_create(
                    category=cat_obj,
                    name=tier_name,
                    defaults={
                        "display_name": display,
                        "price_monthly": price,
                        "highlights": highlights,
                    },
                )
                tier_objs[f"{cat_name}_{tier_name}"] = obj
                status = "created" if created else "exists"
                self.stdout.write(f"  Tier '{display}' — {status}")

        # ── Demo users ────────────────────────────────────────────────
        demo_users = [
            ("swarnali", "swarnali@demo.com", "swarnali123", False),
            ("aritro", "aritro@demo.com", "aritro123", False),
        ]

        user_objs = {}
        for username, email, password, is_staff in demo_users:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={"email": email, "is_staff": is_staff},
            )
            if created:
                user.set_password(password)
                user.save()
            user_objs[username] = user
            status = "created" if created else "exists"
            self.stdout.write(f"  User '{username}' — {status}")

        # ── Assign policies ───────────────────────────────────────────
        today = date.today()
        one_year = today + timedelta(days=365)

        assignments = [
            ("swarnali", "Car_gold", "CAR-GOLD-001"),
            ("swarnali", "Health_silver", "HLT-SLV-001"),
            ("aritro", "Car_silver", "CAR-SLV-002"),
            ("aritro", "Life_gold", "LIF-GOLD-002"),
        ]

        for username, tier_key, policy_number in assignments:
            user = user_objs[username]
            tier = tier_objs[tier_key]
            obj, created = UserPolicy.objects.get_or_create(
                user=user,
                tier=tier,
                defaults={
                    "policy_number": policy_number,
                    "start_date": today,
                    "end_date": one_year,
                    "is_active": True,
                },
            )
            status = "created" if created else "exists"
            self.stdout.write(f"  Policy '{policy_number}' ({tier}) → {username} — {status}")

        self.stdout.write(self.style.SUCCESS(
            "\nDemo data seeded. "
            "Upload PDFs for each tier via POST /api/upload-policy/ as admin."
        ))
