"""Django admin registrations."""
from django.contrib import admin

from .models import Case, CaseItem, CoinPurchase, Drop, OpenRecord, Player

admin.site.site_header = "SKINRUSH — boshqaruv paneli"
admin.site.site_title = "SKINRUSH admin"
admin.site.index_title = "Boshqaruv"


@admin.register(Case)
class CaseAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "openings", "opens", "sort_order")
    search_fields = ("name",)


@admin.register(CaseItem)
class CaseItemAdmin(admin.ModelAdmin):
    list_display = ("name", "wear", "chance", "price", "rarity", "case")
    list_filter = ("rarity", "case")
    search_fields = ("name", "weapon")


@admin.register(Drop)
class DropAdmin(admin.ModelAdmin):
    list_display = ("item", "case", "created_at")
    list_filter = ("case",)


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ("display_name", "username", "telegram_id", "balance",
                    "coins_purchased", "created_at")
    search_fields = ("first_name", "username", "telegram_id")


@admin.register(OpenRecord)
class OpenRecordAdmin(admin.ModelAdmin):
    list_display = ("player", "skin_name", "case_name", "skin_price", "sold", "created_at")
    list_filter = ("sold",)
    search_fields = ("skin_name", "case_name")


@admin.register(CoinPurchase)
class CoinPurchaseAdmin(admin.ModelAdmin):
    list_display = ("player", "amount", "note", "created_at")
