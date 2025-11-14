from django.contrib import admin
from .models import Member, Payment


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'admission_date', 'fee_amount', 'next_due_date', 'created_at']
    list_filter = ['admission_date', 'next_due_date', 'created_at']
    search_fields = ['name', 'phone']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['member', 'amount', 'paid_on', 'recorded_at']
    list_filter = ['paid_on', 'recorded_at']
    search_fields = ['member__name', 'member__phone']

