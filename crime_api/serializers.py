from rest_framework import serializers
from .models import CrimeData


class CrimeDataSerializer(serializers.ModelSerializer):
    """
    Serializer for CrimeData model with comprehensive validation.

    Validates all numeric fields to ensure data integrity and performs
    custom validation for state names and year ranges.
    """

    # Computed fields
    total_crimes = serializers.ReadOnlyField()
    crime_rate_per_capita = serializers.ReadOnlyField()

    class Meta:
        model = CrimeData
        fields = '__all__'

    def validate_state(self, value):
        """
        Validate that state name is not empty and properly formatted.
        """
        if not value or not value.strip():
            raise serializers.ValidationError("State name cannot be empty.")
        if not value.replace(' ', '').isalpha():
            raise serializers.ValidationError("State name must contain only letters and spaces.")
        return value.strip().title()

    def validate_year(self, value):
        """
        Validate that year is within acceptable range.
        """
        if value < 1960 or value > 2025:
            raise serializers.ValidationError("Year must be between 1960 and 2025.")
        return value

    def validate_population(self, value):
        """
        Validate population is positive and reasonable.
        """
        if value < 0:
            raise serializers.ValidationError("Population cannot be negative.")
        if value > 50000000:  # No US state has more than 50 million people
            raise serializers.ValidationError("Population value seems unrealistic for a US state.")
        return value

    def validate(self, data):
        """
        Cross-field validation to ensure data consistency.
        """
        # Check if crime totals match the 'all' category
        property_crimes = ['property_total_burglary', 'property_total_larceny', 'property_total_motor']
        if all(key in data for key in property_crimes):
            calculated_total = sum(data[key] for key in property_crimes)
            if 'property_total_all' in data:
                # Allow 5% margin of error due to rounding
                if abs(calculated_total - data['property_total_all']) > data['property_total_all'] * 0.05:
                    raise serializers.ValidationError(
                        "Property crime totals do not match individual crime sums."
                    )

        # Validate that rates are consistent with totals and population
        if 'property_total_all' in data and 'population' in data and 'property_rate_all' in data:
            if data['population'] > 0:
                expected_rate = (data['property_total_all'] / data['population']) * 100000
                # Allow 10% margin of error
                if abs(expected_rate - data['property_rate_all']) > data['property_rate_all'] * 0.10:
                    raise serializers.ValidationError(
                        "Property crime rate does not match calculated rate from totals and population."
                    )

        return data


class CrimeDataCreateSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for creating new crime data entries via POST.
    Only requires essential fields, with optional detailed breakdown.
    """

    class Meta:
        model = CrimeData
        fields = [
            'state', 'year', 'population',
            'property_rate_all', 'property_rate_burglary',
            'property_rate_larceny', 'property_rate_motor',
            'violent_rate_all', 'violent_rate_assault',
            'violent_rate_murder', 'violent_rate_rape', 'violent_rate_robbery',
            'property_total_all', 'property_total_burglary',
            'property_total_larceny', 'property_total_motor',
            'violent_total_all', 'violent_total_assault',
            'violent_total_murder', 'violent_total_rape', 'violent_total_robbery'
        ]

    def validate_state(self, value):
        """Ensure state name is properly formatted."""
        return value.strip().title()


class CrimeSummarySerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for list views with essential information only.
    """
    total_crimes = serializers.ReadOnlyField()
    crime_rate_per_capita = serializers.ReadOnlyField()

    class Meta:
        model = CrimeData
        fields = [
            'id', 'state', 'year', 'population',
            'violent_rate_all', 'property_rate_all',
            'violent_total_all', 'property_total_all',
            'total_crimes', 'crime_rate_per_capita'
        ]
