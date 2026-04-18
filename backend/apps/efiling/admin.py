from django.contrib import admin
from .models import PaymentObjection


@admin.register(PaymentObjection)
class PaymentObjectionAdmin(admin.ModelAdmin):
    list_display = ['id', 'e_filing', 'court_fee_amount', 'status', 'raised_by', 'raised_at']
    list_filter = ['status', 'raised_at']
    search_fields = ['e_filing__e_filing_number', 'e_filing__petitioner_name', 'remarks']
    readonly_fields = ['raised_at', 'resolved_at']
    date_hierarchy = 'raised_at'

    fieldsets = (
        (None, {
            'fields': ('e_filing', 'court_fee_amount', 'status')
        }),
        ('Details', {
            'fields': ('remarks', 'raised_by', 'raised_at', 'resolved_at')
        }),
    )
