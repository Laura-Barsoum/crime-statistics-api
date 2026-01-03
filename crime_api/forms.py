from django import forms
from .models import CrimeData


class CrimeDataForm(forms.ModelForm):
    """
    Form for validating CrimeData input with custom validation rules.
    """

    class Meta:
        model = CrimeData
        fields = '__all__'

    def clean_state(self):
        """Clean and validate state name."""
        state = self.cleaned_data.get('state')
        if state:
            state = state.strip().title()
            if not state.replace(' ', '').isalpha():
                raise forms.ValidationError("State name must contain only letters.")
        return state

    def clean_year(self):
        """Validate year is within acceptable range."""
        year = self.cleaned_data.get('year')
        if year and (year < 1960 or year > 2025):
            raise forms.ValidationError("Year must be between 1960 and 2025.")
        return year

    def clean_population(self):
        """Validate population value."""
        population = self.cleaned_data.get('population')
        if population and population < 0:
            raise forms.ValidationError("Population cannot be negative.")
        if population and population > 50000000:
            raise forms.ValidationError("Population value seems unrealistic.")
        return population

    def clean(self):
        """Cross-field validation."""
        cleaned_data = super().clean()

        # Validate property crime totals
        property_total = cleaned_data.get('property_total_all')
        burglary = cleaned_data.get('property_total_burglary', 0)
        larceny = cleaned_data.get('property_total_larceny', 0)
        motor = cleaned_data.get('property_total_motor', 0)

        if property_total and (burglary + larceny + motor) > 0:
            calculated = burglary + larceny + motor
            if abs(calculated - property_total) > property_total * 0.05:
                raise forms.ValidationError(
                    "Property crime totals do not match sum of individual crimes."
                )

        return cleaned_data
