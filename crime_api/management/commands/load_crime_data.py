import csv
import os
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from crime_api.models import CrimeData


class Command(BaseCommand):
    """
    Django management command to load crime data from CSV file.

    Usage:
        python manage.py load_crime_data [path_to_csv]

    If no path is provided, looks for 'state_crime.csv' in the data directory.
    """

    help = 'Load crime data from CSV file into the database'

    def add_arguments(self, parser):
        parser.add_argument(
            'csv_file',
            nargs='?',
            type=str,
            default='data/state_crime.csv',
            help='Path to the CSV file containing crime data'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before loading'
        )

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        clear_data = options['clear']

        # Check if file exists
        if not os.path.exists(csv_file):
            # Try looking in BASE_DIR
            csv_file = os.path.join(settings.BASE_DIR, csv_file)
            if not os.path.exists(csv_file):
                raise CommandError(f'CSV file not found: {csv_file}')

        self.stdout.write(self.style.SUCCESS(f'Loading data from: {csv_file}'))

        # Clear existing data if requested
        if clear_data:
            self.stdout.write('Clearing existing crime data...')
            CrimeData.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Existing data cleared.'))

        # Load data from CSV
        loaded_count = 0
        skipped_count = 0
        error_count = 0

        try:
            with open(csv_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)

                for row_num, row in enumerate(reader, start=2):  # Start at 2 (accounting for header)
                    try:
                        # Parse the row data
                        crime_data = self.parse_row(row)

                        # Check if this record already exists
                        existing = CrimeData.objects.filter(
                            state=crime_data['state'],
                            year=crime_data['year']
                        ).first()

                        if existing:
                            if not clear_data:
                                skipped_count += 1
                                if skipped_count <= 5:  # Only show first 5 skips
                                    self.stdout.write(
                                        self.style.WARNING(
                                            f'Row {row_num}: Skipping duplicate - '
                                            f'{crime_data["state"]} {crime_data["year"]}'
                                        )
                                    )
                                continue

                        # Create the record
                        CrimeData.objects.create(**crime_data)
                        loaded_count += 1

                        # Progress indicator
                        if loaded_count % 100 == 0:
                            self.stdout.write(f'Loaded {loaded_count} records...')

                    except Exception as e:
                        error_count += 1
                        if error_count <= 5:  # Only show first 5 errors
                            self.stdout.write(
                                self.style.ERROR(f'Row {row_num}: Error - {str(e)}')
                            )

        except Exception as e:
            raise CommandError(f'Error reading CSV file: {str(e)}')

        # Summary
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS(f'Successfully loaded: {loaded_count} records'))
        if skipped_count > 0:
            self.stdout.write(self.style.WARNING(f'Skipped (duplicates): {skipped_count} records'))
        if error_count > 0:
            self.stdout.write(self.style.ERROR(f'Errors: {error_count} records'))
        self.stdout.write('='*50)

    def parse_row(self, row):
        """
        Parse a CSV row into a dictionary suitable for CrimeData model.

        Handles different CSV column naming conventions.
        """
        # Try to handle both "State" and "state" column names
        state = row.get('State') or row.get('state', '').strip()
        year = int(row.get('Year') or row.get('year', 0))

        # Handle nested column names like "Data.Population"
        population = self.get_value(row, ['Data.Population', 'Population', 'population'])

        return {
            'state': state,
            'year': year,
            'population': int(float(population)),

            # Property crime rates
            'property_rate_all': float(self.get_value(
                row, ['Data.Rates.Property.All', 'property_rate_all'], 0
            )),
            'property_rate_burglary': float(self.get_value(
                row, ['Data.Rates.Property.Burglary', 'property_rate_burglary'], 0
            )),
            'property_rate_larceny': float(self.get_value(
                row, ['Data.Rates.Property.Larceny', 'property_rate_larceny'], 0
            )),
            'property_rate_motor': float(self.get_value(
                row, ['Data.Rates.Property.Motor', 'property_rate_motor'], 0
            )),

            # Violent crime rates
            'violent_rate_all': float(self.get_value(
                row, ['Data.Rates.Violent.All', 'violent_rate_all'], 0
            )),
            'violent_rate_assault': float(self.get_value(
                row, ['Data.Rates.Violent.Assault', 'violent_rate_assault'], 0
            )),
            'violent_rate_murder': float(self.get_value(
                row, ['Data.Rates.Violent.Murder', 'violent_rate_murder'], 0
            )),
            'violent_rate_rape': float(self.get_value(
                row, ['Data.Rates.Violent.Rape', 'violent_rate_rape'], 0
            )),
            'violent_rate_robbery': float(self.get_value(
                row, ['Data.Rates.Violent.Robbery', 'violent_rate_robbery'], 0
            )),

            # Property crime totals
            'property_total_all': int(float(self.get_value(
                row, ['Data.Totals.Property.All', 'property_total_all'], 0
            ))),
            'property_total_burglary': int(float(self.get_value(
                row, ['Data.Totals.Property.Burglary', 'property_total_burglary'], 0
            ))),
            'property_total_larceny': int(float(self.get_value(
                row, ['Data.Totals.Property.Larceny', 'property_total_larceny'], 0
            ))),
            'property_total_motor': int(float(self.get_value(
                row, ['Data.Totals.Property.Motor', 'property_total_motor'], 0
            ))),

            # Violent crime totals
            'violent_total_all': int(float(self.get_value(
                row, ['Data.Totals.Violent.All', 'violent_total_all'], 0
            ))),
            'violent_total_assault': int(float(self.get_value(
                row, ['Data.Totals.Violent.Assault', 'violent_total_assault'], 0
            ))),
            'violent_total_murder': int(float(self.get_value(
                row, ['Data.Totals.Violent.Murder', 'violent_total_murder'], 0
            ))),
            'violent_total_rape': int(float(self.get_value(
                row, ['Data.Totals.Violent.Rape', 'violent_total_rape'], 0
            ))),
            'violent_total_robbery': int(float(self.get_value(
                row, ['Data.Totals.Violent.Robbery', 'violent_total_robbery'], 0
            ))),
        }

    def get_value(self, row, keys, default=0):
        """Get value from row trying multiple possible key names."""
        for key in keys:
            if key in row and row[key]:
                return row[key]
        return default
