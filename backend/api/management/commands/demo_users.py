"""Create a few demo players with drop history + purchases (idempotent).

Lets the admin panel's "Foydalanuvchilar" section show realistic data before
real Telegram players register. Safe to run on every deploy — it only touches
the fixed demo telegram_ids and skips if they already exist.

    python manage.py demo_users
"""
import random

from django.core.management.base import BaseCommand

from api.models import CaseItem, CoinPurchase, OpenRecord, Player

DEMOS = [
    (900000001, "shukurjon", "Shukurjon"),
    (900000002, "aziz_uz", "Aziz"),
    (900000003, "malika", "Malika"),
    (900000004, "bekzod07", "Bekzod"),
    (900000005, "diyor", "Diyor"),
]


class Command(BaseCommand):
    help = "Create demo players with sample history (idempotent)."

    def handle(self, *args, **options):
        items = list(CaseItem.objects.all().order_by("?")[:400])
        if not items:
            self.stdout.write("Avval `seed` ishga tushiring (skinlar yo'q).")
            return

        created = 0
        for tg_id, uname, name in DEMOS:
            if Player.objects.filter(telegram_id=tg_id).exists():
                continue
            p = Player.objects.create(
                telegram_id=tg_id, username=uname, first_name=name,
                photo_url="", balance=random.randint(500, 50000),
                coins_purchased=random.choice([0, 5000, 10000, 25000, 100000]),
            )
            for _ in range(random.randint(4, 14)):
                it = random.choice(items)
                OpenRecord.objects.create(
                    player=p, case=it.case, case_name=it.case.name,
                    skin_name=it.name, skin_image=it.image, skin_price=it.price,
                    rarity=it.rarity, color=it.color, wear=it.wear,
                    sold=random.random() < 0.5,
                )
            if p.coins_purchased:
                CoinPurchase.objects.create(player=p, amount=p.coins_purchased, note="demo")
            created += 1

        self.stdout.write(self.style.SUCCESS(
            f"Demo foydalanuvchilar: +{created} (jami {Player.objects.count()})"))
