from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class CrimeData(models.Model):
    """
    Model representing crime statistics for US states.

    Contains both crime rates (per 100,000 population) and total crime counts,
    covering violent crimes (assault, murder, rape, robbery) and property crimes
    (burglary, larceny, motor vehicle theft) from 1960 to 2019.
    """

    # Basic Information
    state = models.CharField(
        max_length=100,
        db_index=True,
        help_text="US State name"
    )
    year = models.IntegerField(
        validators=[MinValueValidator(1960), MaxValueValidator(2025)],
        db_index=True,
        help_text="Year of the crime report"
    )
    population = models.IntegerField(
        validators=[MinValueValidator(0)],
        help_text="State population for the given year"
    )

    # Property Crime Rates (per 100,000 population)
    property_rate_all = models.FloatField(
        validators=[MinValueValidator(0)],
        help_text="Total property crime rate per 100,000 population"
    )
    property_rate_burglary = models.FloatField(
        validators=[MinValueValidator(0)],
        help_text="Burglary rate per 100,000 population"
    )
    property_rate_larceny = models.FloatField(
        validators=[MinValueValidator(0)],
        help_text="Larceny rate per 100,000 population"
    )
    property_rate_motor = models.FloatField(
        validators=[MinValueValidator(0)],
        help_text="Motor vehicle theft rate per 100,000 population"
    )

    # Violent Crime Rates (per 100,000 population)
    violent_rate_all = models.FloatField(
        validators=[MinValueValidator(0)],
        help_text="Total violent crime rate per 100,000 population"
    )
    violent_rate_assault = models.FloatField(
        validators=[MinValueValidator(0)],
        help_text="Assault rate per 100,000 population"
    )
    violent_rate_murder = models.FloatField(
        validators=[MinValueValidator(0)],
        help_text="Murder rate per 100,000 population"
    )
    violent_rate_rape = models.FloatField(
        validators=[MinValueValidator(0)],
        help_text="Rape rate per 100,000 population"
    )
    violent_rate_robbery = models.FloatField(
        validators=[MinValueValidator(0)],
        help_text="Robbery rate per 100,000 population"
    )

    # Property Crime Totals (absolute numbers)
    property_total_all = models.IntegerField(
        validators=[MinValueValidator(0)],
        help_text="Total property crimes"
    )
    property_total_burglary = models.IntegerField(
        validators=[MinValueValidator(0)],
        help_text="Total burglaries"
    )
    property_total_larceny = models.IntegerField(
        validators=[MinValueValidator(0)],
        help_text="Total larceny cases"
    )
    property_total_motor = models.IntegerField(
        validators=[MinValueValidator(0)],
        help_text="Total motor vehicle thefts"
    )

    # Violent Crime Totals (absolute numbers)
    violent_total_all = models.IntegerField(
        validators=[MinValueValidator(0)],
        help_text="Total violent crimes"
    )
    violent_total_assault = models.IntegerField(
        validators=[MinValueValidator(0)],
        help_text="Total assaults"
    )
    violent_total_murder = models.IntegerField(
        validators=[MinValueValidator(0)],
        help_text="Total murders"
    )
    violent_total_rape = models.IntegerField(
        validators=[MinValueValidator(0)],
        help_text="Total rapes"
    )
    violent_total_robbery = models.IntegerField(
        validators=[MinValueValidator(0)],
        help_text="Total robberies"
    )

    class Meta:
        ordering = ['-year', 'state']
        unique_together = ['state', 'year']
        verbose_name = "Crime Data"
        verbose_name_plural = "Crime Data"
        indexes = [
            models.Index(fields=['state', 'year']),
            models.Index(fields=['year']),
            models.Index(fields=['state']),
        ]

    def __str__(self):
        return f"{self.state} - {self.year}"

    @property
    def total_crimes(self):
        """Calculate total number of crimes (property + violent)"""
        return self.property_total_all + self.violent_total_all

    @property
    def crime_rate_per_capita(self):
        """Calculate overall crime rate per 100,000 population"""
        return self.property_rate_all + self.violent_rate_all
