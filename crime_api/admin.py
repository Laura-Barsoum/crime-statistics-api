from django.contrib import admin
from .models import CrimeData


@admin.register(CrimeData)
class CrimeDataAdmin(admin.ModelAdmin):
    """
    Admin interface configuration for CrimeData model.
    """

    list_display = [
        'state', 'year', 'population',
        'violent_rate_all', 'property_rate_all',
        'violent_total_all', 'property_total_all'
    ]

    list_filter = ['year', 'state']

    search_fields = ['state', 'year']

    ordering = ['-year', 'state']

    fieldsets = (
        ('Basic Information', {
            'fields': ('state', 'year', 'population')
        }),
        ('Violent Crime Rates (per 100,000)', {
            'fields': (
                'violent_rate_all', 'violent_rate_assault',
                'violent_rate_murder', 'violent_rate_rape',
                'violent_rate_robbery'
            ),
            'classes': ('collapse',)
        }),
        ('Property Crime Rates (per 100,000)', {
            'fields': (
                'property_rate_all', 'property_rate_burglary',
                'property_rate_larceny', 'property_rate_motor'
            ),
            'classes': ('collapse',)
        }),
        ('Violent Crime Totals', {
            'fields': (
                'violent_total_all', 'violent_total_assault',
                'violent_total_murder', 'violent_total_rape',
                'violent_total_robbery'
            ),
            'classes': ('collapse',)
        }),
        ('Property Crime Totals', {
            'fields': (
                'property_total_all', 'property_total_burglary',
                'property_total_larceny', 'property_total_motor'
            ),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = []

    def get_readonly_fields(self, request, obj=None):
        """Make certain fields read-only when editing existing objects."""
        if obj:  # Editing an existing object
            return ['state', 'year']
        return []
