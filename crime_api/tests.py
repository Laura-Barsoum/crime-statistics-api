from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from .models import CrimeData
from .serializers import CrimeDataSerializer


class CrimeDataModelTest(TestCase):
    """Test cases for CrimeData model."""

    def setUp(self):
        """Create test data."""
        self.crime_data = CrimeData.objects.create(
            state="California",
            year=2015,
            population=39000000,
            property_rate_all=2500.5,
            property_rate_burglary=450.2,
            property_rate_larceny=1800.3,
            property_rate_motor=250.0,
            violent_rate_all=450.5,
            violent_rate_assault=250.0,
            violent_rate_murder=5.5,
            violent_rate_rape=30.0,
            violent_rate_robbery=165.0,
            property_total_all=975195,
            property_total_burglary=175578,
            property_total_larceny=702117,
            property_total_motor=97500,
            violent_total_all=175695,
            violent_total_assault=97500,
            violent_total_murder=2145,
            violent_total_rape=11700,
            violent_total_robbery=64350
        )

    def test_crime_data_creation(self):
        """Test that crime data is created correctly."""
        self.assertEqual(self.crime_data.state, "California")
        self.assertEqual(self.crime_data.year, 2015)
        self.assertEqual(self.crime_data.population, 39000000)

    def test_string_representation(self):
        """Test the string representation of crime data."""
        expected = "California - 2015"
        self.assertEqual(str(self.crime_data), expected)

    def test_total_crimes_property(self):
        """Test the total_crimes computed property."""
        total = self.crime_data.property_total_all + self.crime_data.violent_total_all
        self.assertEqual(self.crime_data.total_crimes, total)

    def test_crime_rate_per_capita_property(self):
        """Test the crime_rate_per_capita computed property."""
        rate = self.crime_data.property_rate_all + self.crime_data.violent_rate_all
        self.assertEqual(self.crime_data.crime_rate_per_capita, rate)

    def test_unique_together_constraint(self):
        """Test that state and year combination must be unique."""
        with self.assertRaises(Exception):
            CrimeData.objects.create(
                state="California",
                year=2015,  # Same state and year as setUp
                population=39000000,
                property_rate_all=2500.5,
                property_rate_burglary=450.2,
                property_rate_larceny=1800.3,
                property_rate_motor=250.0,
                violent_rate_all=450.5,
                violent_rate_assault=250.0,
                violent_rate_murder=5.5,
                violent_rate_rape=30.0,
                violent_rate_robbery=165.0,
                property_total_all=975195,
                property_total_burglary=175578,
                property_total_larceny=702117,
                property_total_motor=97500,
                violent_total_all=175695,
                violent_total_assault=97500,
                violent_total_murder=2145,
                violent_total_rape=11700,
                violent_total_robbery=64350
            )


class CrimeDataAPITest(APITestCase):
    """Test cases for Crime Data API endpoints."""

    def setUp(self):
        """Set up test client and create test data."""
        self.client = APIClient()

        # Create test data for California
        self.california_2015 = CrimeData.objects.create(
            state="California",
            year=2015,
            population=39000000,
            property_rate_all=2500.5,
            property_rate_burglary=450.2,
            property_rate_larceny=1800.3,
            property_rate_motor=250.0,
            violent_rate_all=450.5,
            violent_rate_assault=250.0,
            violent_rate_murder=5.5,
            violent_rate_rape=30.0,
            violent_rate_robbery=165.0,
            property_total_all=975195,
            property_total_burglary=175578,
            property_total_larceny=702117,
            property_total_motor=97500,
            violent_total_all=175695,
            violent_total_assault=97500,
            violent_total_murder=2145,
            violent_total_rape=11700,
            violent_total_robbery=64350
        )

        # Create test data for Texas
        self.texas_2015 = CrimeData.objects.create(
            state="Texas",
            year=2015,
            population=27000000,
            property_rate_all=2800.0,
            property_rate_burglary=600.0,
            property_rate_larceny=1900.0,
            property_rate_motor=300.0,
            violent_rate_all=400.0,
            violent_rate_assault=220.0,
            violent_rate_murder=4.5,
            violent_rate_rape=35.0,
            violent_rate_robbery=140.5,
            property_total_all=756000,
            property_total_burglary=162000,
            property_total_larceny=513000,
            property_total_motor=81000,
            violent_total_all=108000,
            violent_total_assault=59400,
            violent_total_murder=1215,
            violent_total_rape=9450,
            violent_total_robbery=37935
        )

        # Create test data for California 2010
        self.california_2010 = CrimeData.objects.create(
            state="California",
            year=2010,
            population=37000000,
            property_rate_all=2700.0,
            property_rate_burglary=500.0,
            property_rate_larceny=1950.0,
            property_rate_motor=250.0,
            violent_rate_all=470.0,
            violent_rate_assault=260.0,
            violent_rate_murder=6.0,
            violent_rate_rape=32.0,
            violent_rate_robbery=172.0,
            property_total_all=999000,
            property_total_burglary=185000,
            property_total_larceny=721500,
            property_total_motor=92500,
            violent_total_all=173900,
            violent_total_assault=96200,
            violent_total_murder=2220,
            violent_total_rape=11840,
            violent_total_robbery=63640
        )

    def test_get_crime_data_list(self):
        """Test GET request to list all crime data."""
        url = reverse('crime-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

    def test_get_crime_data_detail(self):
        """Test GET request to retrieve specific crime data."""
        url = reverse('crime-detail', kwargs={'pk': self.california_2015.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['state'], 'California')
        self.assertEqual(response.data['year'], 2015)

    def test_create_crime_data(self):
        """Test POST request to create new crime data."""
        url = reverse('crime-list')
        data = {
            'state': 'New York',
            'year': 2015,
            'population': 19700000,
            'property_rate_all': 1800.0,
            'property_rate_burglary': 300.0,
            'property_rate_larceny': 1300.0,
            'property_rate_motor': 200.0,
            'violent_rate_all': 380.0,
            'violent_rate_assault': 210.0,
            'violent_rate_murder': 4.0,
            'violent_rate_rape': 25.0,
            'violent_rate_robbery': 141.0,
            'property_total_all': 354600,
            'property_total_burglary': 59100,
            'property_total_larceny': 256100,
            'property_total_motor': 39400,
            'violent_total_all': 74860,
            'violent_total_assault': 41370,
            'violent_total_murder': 788,
            'violent_total_rape': 4925,
            'violent_total_robbery': 27777
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CrimeData.objects.count(), 4)
        self.assertEqual(CrimeData.objects.get(state='New York', year=2015).population, 19700000)

    def test_filter_by_state(self):
        """Test filtering crime data by state."""
        url = reverse('crime-list')
        response = self.client.get(url, {'state': 'California'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_filter_by_year(self):
        """Test filtering crime data by year."""
        url = reverse('crime-list')
        response = self.client.get(url, {'year': 2015})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_high_crime_states(self):
        """Test high crime states endpoint."""
        url = reverse('high-crime-states')
        response = self.client.get(url, {'threshold': 2500, 'year': 2015})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertGreater(len(response.data['results']), 0)

    def test_crime_trends(self):
        """Test crime trends endpoint."""
        url = reverse('crime-trends', kwargs={'state_name': 'California'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['state'], 'California')
        self.assertIn('statistics', response.data)
        self.assertIn('yearly_data', response.data)
        self.assertEqual(len(response.data['yearly_data']), 2)

    def test_crime_trends_not_found(self):
        """Test crime trends endpoint with non-existent state."""
        url = reverse('crime-trends', kwargs={'state_name': 'NonExistentState'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_compare_states(self):
        """Test compare states endpoint."""
        url = reverse('compare-states')
        response = self.client.get(url, {
            'states': 'California,Texas',
            'year': 2015
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['states_compared'], 2)
        self.assertIn('comparison', response.data)

    def test_compare_states_missing_params(self):
        """Test compare states endpoint with missing parameters."""
        url = reverse('compare-states')
        response = self.client.get(url, {'states': 'California'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_safest_states(self):
        """Test safest states endpoint."""
        url = reverse('safest-states')
        response = self.client.get(url, {
            'year': 2015,
            'limit': 5,
            'crime_type': 'violent'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('safest_states', response.data)
        self.assertLessEqual(len(response.data['safest_states']), 5)

    def test_safest_states_missing_year(self):
        """Test safest states endpoint without year parameter."""
        url = reverse('safest-states')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_decade_comparison(self):
        """Test decade comparison endpoint."""
        url = reverse('decade-comparison', kwargs={'state_name': 'California'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('decade_statistics', response.data)
        self.assertGreater(len(response.data['decade_statistics']), 0)

    def test_crime_type_analysis(self):
        """Test crime type analysis endpoint."""
        url = reverse('crime-type-analysis')
        response = self.client.get(url, {
            'year': 2015,
            'crime_type': 'murder',
            'sort': 'rate',
            'limit': 10
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertEqual(response.data['crime_type'], 'murder')

    def test_crime_type_analysis_invalid_type(self):
        """Test crime type analysis with invalid crime type."""
        url = reverse('crime-type-analysis')
        response = self.client.get(url, {
            'year': 2015,
            'crime_type': 'invalid_crime'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_crime_data(self):
        """Test PUT request to update crime data."""
        url = reverse('crime-detail', kwargs={'pk': self.california_2015.pk})
        updated_data = {
            'state': 'California',
            'year': 2015,
            'population': 39500000,  # Updated population
            'property_rate_all': 2500.5,
            'property_rate_burglary': 450.2,
            'property_rate_larceny': 1800.3,
            'property_rate_motor': 250.0,
            'violent_rate_all': 450.5,
            'violent_rate_assault': 250.0,
            'violent_rate_murder': 5.5,
            'violent_rate_rape': 30.0,
            'violent_rate_robbery': 165.0,
            'property_total_all': 975195,
            'property_total_burglary': 175578,
            'property_total_larceny': 702117,
            'property_total_motor': 97500,
            'violent_total_all': 175695,
            'violent_total_assault': 97500,
            'violent_total_murder': 2145,
            'violent_total_rape': 11700,
            'violent_total_robbery': 64350
        }
        response = self.client.put(url, updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.california_2015.refresh_from_db()
        self.assertEqual(self.california_2015.population, 39500000)

    def test_delete_crime_data(self):
        """Test DELETE request to remove crime data."""
        url = reverse('crime-detail', kwargs={'pk': self.california_2015.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(CrimeData.objects.count(), 2)


class CrimeDataSerializerTest(TestCase):
    """Test cases for CrimeData serializers."""

    def setUp(self):
        """Create test data."""
        self.crime_data = CrimeData.objects.create(
            state="Florida",
            year=2018,
            population=21000000,
            property_rate_all=2600.0,
            property_rate_burglary=480.0,
            property_rate_larceny=1870.0,
            property_rate_motor=250.0,
            violent_rate_all=430.0,
            violent_rate_assault=240.0,
            violent_rate_murder=5.0,
            violent_rate_rape=28.0,
            violent_rate_robbery=157.0,
            property_total_all=546000,
            property_total_burglary=100800,
            property_total_larceny=392700,
            property_total_motor=52500,
            violent_total_all=90300,
            violent_total_assault=50400,
            violent_total_murder=1050,
            violent_total_rape=5880,
            violent_total_robbery=32970
        )

    def test_serializer_contains_expected_fields(self):
        """Test that serializer contains all expected fields."""
        serializer = CrimeDataSerializer(instance=self.crime_data)
        data = serializer.data
        self.assertIn('state', data)
        self.assertIn('year', data)
        self.assertIn('population', data)
        self.assertIn('total_crimes', data)
        self.assertIn('crime_rate_per_capita', data)

    def test_serializer_validation_state(self):
        """Test state name validation in serializer."""
        serializer = CrimeDataSerializer(data={
            'state': '   florida   ',  # Should be cleaned
            'year': 2018,
            'population': 21000000,
            'property_rate_all': 2600.0,
            'property_rate_burglary': 480.0,
            'property_rate_larceny': 1870.0,
            'property_rate_motor': 250.0,
            'violent_rate_all': 430.0,
            'violent_rate_assault': 240.0,
            'violent_rate_murder': 5.0,
            'violent_rate_rape': 28.0,
            'violent_rate_robbery': 157.0,
            'property_total_all': 546000,
            'property_total_burglary': 100800,
            'property_total_larceny': 392700,
            'property_total_motor': 52500,
            'violent_total_all': 90300,
            'violent_total_assault': 50400,
            'violent_total_murder': 1050,
            'violent_total_rape': 5880,
            'violent_total_robbery': 32970
        })
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['state'], 'Florida')
