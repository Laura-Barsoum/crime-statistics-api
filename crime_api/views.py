from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Avg, Max, Min, Sum, Q
from django.shortcuts import render
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from .models import CrimeData
from .serializers import CrimeDataSerializer, CrimeDataCreateSerializer, CrimeSummarySerializer
from .forms import CrimeDataForm


def home_view(request):
    """
    Home page view displaying API information and endpoint hyperlinks.
    """
    import django
    import rest_framework
    import sys

    context = {
        'python_version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        'django_version': django.get_version(),
        'drf_version': rest_framework.VERSION,
        'admin_username': 'admin',
        'admin_password': 'admin123',
    }
    return render(request, 'crime_api/home.html', context)


class CrimeDataViewSet(viewsets.ModelViewSet):
    """
    ViewSet for CrimeData model providing CRUD operations.

    Endpoints:
    - GET /api/crime/ - List all crime data (with optional filtering)
    - POST /api/crime/ - Create new crime data entry
    - GET /api/crime/{id}/ - Retrieve specific crime data
    - PUT /api/crime/{id}/ - Update crime data
    - DELETE /api/crime/{id}/ - Delete crime data
    """
    queryset = CrimeData.objects.all()
    serializer_class = CrimeDataSerializer

    def get_serializer_class(self):
        """Use different serializer for create action."""
        if self.action == 'create':
            return CrimeDataCreateSerializer
        elif self.action == 'list':
            return CrimeSummarySerializer
        return CrimeDataSerializer

    def get_queryset(self):
        """
        Filter queryset based on query parameters.
        Supports filtering by state, year, and year range.
        """
        queryset = CrimeData.objects.all()
        state = self.request.query_params.get('state', None)
        year = self.request.query_params.get('year', None)
        year_from = self.request.query_params.get('year_from', None)
        year_to = self.request.query_params.get('year_to', None)

        if state:
            queryset = queryset.filter(state__icontains=state)
        if year:
            queryset = queryset.filter(year=year)
        if year_from:
            queryset = queryset.filter(year__gte=year_from)
        if year_to:
            queryset = queryset.filter(year__lte=year_to)

        return queryset


@extend_schema(
    parameters=[
        OpenApiParameter(
            name='threshold',
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description='Crime rate per capita threshold',
            required=False,
            default=5000,
        ),
        OpenApiParameter(
            name='year',
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description='Specific year to filter',
            required=False,
        ),
        OpenApiParameter(
            name='crime_type',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description='Type of crime: violent, property, or all',
            required=False,
            default='all',
            enum=['violent', 'property', 'all'],
        ),
    ],
    responses={200: CrimeDataSerializer(many=True)},
    description='Get states with crime rates above specified threshold.'
)
@api_view(['GET'])
def high_crime_states(request):
    """
    ENDPOINT 1: Get states with crime rates above specified threshold.

    Query Parameters:
    - threshold: Crime rate per capita threshold (default: 5000)
    - year: Specific year to filter (optional)
    - crime_type: 'violent' or 'property' (default: 'all')

    Example: /api/high-crime-states/?threshold=6000&year=2015&crime_type=violent

    This endpoint is interesting because it allows identification of high-crime
    areas for policy-making and resource allocation.
    """
    threshold = float(request.query_params.get('threshold', 5000))
    year = request.query_params.get('year', None)
    crime_type = request.query_params.get('crime_type', 'all')

    queryset = CrimeData.objects.all()

    if year:
        queryset = queryset.filter(year=year)

    # Filter based on crime type
    if crime_type == 'violent':
        queryset = queryset.filter(violent_rate_all__gte=threshold)
    elif crime_type == 'property':
        queryset = queryset.filter(property_rate_all__gte=threshold)
    else:
        # Both violent and property crimes combined
        queryset = [
            record for record in queryset
            if (record.violent_rate_all + record.property_rate_all) >= threshold
        ]

    serializer = CrimeSummarySerializer(queryset, many=True)
    return Response({
        'threshold': threshold,
        'crime_type': crime_type,
        'year': year if year else 'all years',
        'count': len(serializer.data),
        'results': serializer.data
    })


@extend_schema(
    parameters=[
        OpenApiParameter(
            name='state_name',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.PATH,
            description='Name of the state',
            required=True,
        ),
        OpenApiParameter(
            name='year_from',
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description='Start year',
            required=False,
        ),
        OpenApiParameter(
            name='year_to',
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description='End year',
            required=False,
        ),
    ],
    responses={200: CrimeDataSerializer(many=True)},
    description='Analyze crime trends for a specific state over time.'
)
@api_view(['GET'])
def crime_trends(request, state_name):
    """
    ENDPOINT 2: Analyze crime trends for a specific state over time.

    URL Parameter:
    - state_name: Name of the state

    Query Parameters:
    - year_from: Start year (optional)
    - year_to: End year (optional)

    Example: /api/crime-trends/California/?year_from=2000&year_to=2019

    This endpoint is interesting because it shows how crime has evolved over
    decades in a state, useful for evaluating policy effectiveness.
    """
    year_from = request.query_params.get('year_from', None)
    year_to = request.query_params.get('year_to', None)

    queryset = CrimeData.objects.filter(state__iexact=state_name).order_by('year')

    if year_from:
        queryset = queryset.filter(year__gte=year_from)
    if year_to:
        queryset = queryset.filter(year__lte=year_to)

    if not queryset.exists():
        return Response(
            {'error': f'No data found for state: {state_name}'},
            status=status.HTTP_404_NOT_FOUND
        )

    # Calculate trend statistics
    stats = queryset.aggregate(
        avg_violent_rate=Avg('violent_rate_all'),
        avg_property_rate=Avg('property_rate_all'),
        max_violent_rate=Max('violent_rate_all'),
        min_violent_rate=Min('violent_rate_all'),
        total_murders=Sum('violent_total_murder'),
        avg_population=Avg('population')
    )

    serializer = CrimeDataSerializer(queryset, many=True)

    return Response({
        'state': state_name,
        'year_range': f"{queryset.first().year} to {queryset.last().year}",
        'statistics': stats,
        'data_points': len(serializer.data),
        'yearly_data': serializer.data
    })


@extend_schema(
    parameters=[
        OpenApiParameter(
            name='states',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description='Comma-separated list of state names (e.g., California,Texas,Florida)',
            required=True,
            examples=[
                OpenApiExample('Three states', value='California,Texas,Florida'),
                OpenApiExample('Two states', value='California,New York'),
            ]
        ),
        OpenApiParameter(
            name='year',
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description='Year to compare (e.g., 2015)',
            required=True,
            examples=[
                OpenApiExample('Recent year', value='2015'),
                OpenApiExample('Earlier year', value='2000'),
            ]
        ),
    ],
    responses={200: CrimeDataSerializer(many=True)},
    description='Compare crime statistics across multiple states for a specific year.'
)
@api_view(['GET'])
def compare_states(request):
    """
    ENDPOINT 3: Compare crime statistics across multiple states for a specific year.

    Query Parameters:
    - states: Comma-separated list of state names (required)
    - year: Year to compare (required)
    - metric: Specific crime metric to compare (optional, default: all)

    Example: /api/compare-states/?states=California,Texas,New York&year=2015

    This endpoint is interesting for understanding regional crime disparities
    and comparing different state approaches to law enforcement.
    """
    states_param = request.query_params.get('states', '')
    year = request.query_params.get('year', None)

    if not states_param or not year:
        return Response(
            {'error': 'Both states and year parameters are required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    states = [s.strip() for s in states_param.split(',')]

    # Build query for multiple states
    query = Q()
    for state in states:
        query |= Q(state__iexact=state)

    queryset = CrimeData.objects.filter(query, year=year)

    if not queryset.exists():
        return Response(
            {'error': f'No data found for specified states in year {year}'},
            status=status.HTTP_404_NOT_FOUND
        )

    serializer = CrimeDataSerializer(queryset, many=True)

    # Calculate comparison metrics
    comparison = []
    for data in serializer.data:
        comparison.append({
            'state': data['state'],
            'population': data['population'],
            'violent_rate': data['violent_rate_all'],
            'property_rate': data['property_rate_all'],
            'total_crime_rate': data['crime_rate_per_capita'],
            'murder_rate': data['violent_rate_murder']
        })

    return Response({
        'year': year,
        'states_compared': len(comparison),
        'comparison': comparison,
        'detailed_data': serializer.data
    })


@extend_schema(
    parameters=[
        OpenApiParameter(
            name='year',
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description='Specific year to analyze',
            required=True,
            examples=[
                OpenApiExample('Recent year', value='2015'),
            ]
        ),
        OpenApiParameter(
            name='limit',
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description='Number of states to return',
            required=False,
            default=10,
        ),
        OpenApiParameter(
            name='crime_type',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description='Type of crime: violent, property, or all',
            required=False,
            default='all',
            enum=['violent', 'property', 'all'],
        ),
    ],
    responses={200: CrimeSummarySerializer(many=True)},
    description='Get the safest states based on lowest crime rates.'
)
@api_view(['GET'])
def safest_states(request):
    """
    ENDPOINT 4: Get the safest states based on lowest crime rates.

    Query Parameters:
    - year: Specific year (required)
    - limit: Number of states to return (default: 10)
    - crime_type: 'violent', 'property', or 'all' (default: 'all')

    Example: /api/safest-states/?year=2015&limit=5&crime_type=violent

    This endpoint is interesting for identifying best practices in crime
    prevention and states with effective law enforcement.
    """
    year = request.query_params.get('year', None)
    limit = int(request.query_params.get('limit', 10))
    crime_type = request.query_params.get('crime_type', 'all')

    if not year:
        return Response(
            {'error': 'Year parameter is required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    queryset = CrimeData.objects.filter(year=year)

    # Sort based on crime type
    if crime_type == 'violent':
        queryset = queryset.order_by('violent_rate_all')[:limit]
    elif crime_type == 'property':
        queryset = queryset.order_by('property_rate_all')[:limit]
    else:
        # Sort by combined rate
        results = list(queryset)
        results.sort(key=lambda x: x.crime_rate_per_capita)
        queryset = results[:limit]

    serializer = CrimeSummarySerializer(queryset, many=True)

    return Response({
        'year': year,
        'crime_type': crime_type,
        'limit': limit,
        'safest_states': serializer.data
    })


@extend_schema(
    parameters=[
        OpenApiParameter(
            name='state_name',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.PATH,
            description='Name of the state',
            required=True,
        ),
    ],
    responses={200: CrimeDataSerializer(many=True)},
    description='Compare crime statistics across decades for a specific state.'
)
@api_view(['GET'])
def decade_comparison(request, state_name):
    """
    ENDPOINT 5: Compare crime statistics across decades for a specific state.

    URL Parameter:
    - state_name: Name of the state

    Example: /api/decade-comparison/Florida/

    This endpoint is interesting for long-term trend analysis and understanding
    how crime patterns have changed over multiple decades.
    """
    queryset = CrimeData.objects.filter(state__iexact=state_name).order_by('year')

    if not queryset.exists():
        return Response(
            {'error': f'No data found for state: {state_name}'},
            status=status.HTTP_404_NOT_FOUND
        )

    # Group data by decades
    decades = {}
    for record in queryset:
        decade = (record.year // 10) * 10
        decade_label = f"{decade}s"

        if decade_label not in decades:
            decades[decade_label] = {
                'violent_rates': [],
                'property_rates': [],
                'murder_totals': [],
                'populations': []
            }

        decades[decade_label]['violent_rates'].append(record.violent_rate_all)
        decades[decade_label]['property_rates'].append(record.property_rate_all)
        decades[decade_label]['murder_totals'].append(record.violent_total_murder)
        decades[decade_label]['populations'].append(record.population)

    # Calculate averages for each decade
    decade_stats = {}
    for decade, data in decades.items():
        decade_stats[decade] = {
            'avg_violent_rate': sum(data['violent_rates']) / len(data['violent_rates']),
            'avg_property_rate': sum(data['property_rates']) / len(data['property_rates']),
            'total_murders': sum(data['murder_totals']),
            'avg_population': sum(data['populations']) / len(data['populations']),
            'years_included': len(data['violent_rates'])
        }

    return Response({
        'state': state_name,
        'decades_analyzed': len(decade_stats),
        'decade_statistics': decade_stats
    })


@extend_schema(
    parameters=[
        OpenApiParameter(
            name='year',
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description='Year to analyze',
            required=True,
            examples=[
                OpenApiExample('Recent year', value='2015'),
            ]
        ),
        OpenApiParameter(
            name='crime_type',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description='Type of crime to analyze',
            required=True,
            enum=['murder', 'assault', 'robbery', 'rape', 'burglary', 'larceny', 'motor'],
            examples=[
                OpenApiExample('Murder', value='murder'),
                OpenApiExample('Burglary', value='burglary'),
            ]
        ),
        OpenApiParameter(
            name='sort',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description='Sort by rate or total',
            required=False,
            default='rate',
            enum=['rate', 'total'],
        ),
        OpenApiParameter(
            name='limit',
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description='Number of results to return',
            required=False,
            default=50,
        ),
    ],
    responses={200: CrimeDataSerializer(many=True)},
    description='Analyze specific crime types across all states for a given year.'
)
@api_view(['GET'])
def crime_type_analysis(request):
    """
    ENDPOINT 6: Analyze specific crime types across all states for a given year.

    Query Parameters:
    - year: Year to analyze (required)
    - crime_type: Type of crime ('murder', 'assault', 'robbery', 'rape',
                  'burglary', 'larceny', 'motor') (required)
    - sort: 'rate' or 'total' (default: 'rate')
    - limit: Number of results (default: 50)

    Example: /api/crime-type-analysis/?year=2015&crime_type=murder&sort=rate&limit=10

    This endpoint is interesting for identifying states with specific crime
    problems and targeting interventions for particular crime types.
    """
    year = request.query_params.get('year', None)
    crime_type = request.query_params.get('crime_type', None)
    sort_by = request.query_params.get('sort', 'rate')
    limit = int(request.query_params.get('limit', 50))

    if not year or not crime_type:
        return Response(
            {'error': 'Both year and crime_type parameters are required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Map crime type to field names
    crime_field_map = {
        'murder': ('violent_rate_murder', 'violent_total_murder'),
        'assault': ('violent_rate_assault', 'violent_total_assault'),
        'robbery': ('violent_rate_robbery', 'violent_total_robbery'),
        'rape': ('violent_rate_rape', 'violent_total_rape'),
        'burglary': ('property_rate_burglary', 'property_total_burglary'),
        'larceny': ('property_rate_larceny', 'property_total_larceny'),
        'motor': ('property_rate_motor', 'property_total_motor'),
    }

    if crime_type not in crime_field_map:
        return Response(
            {'error': f'Invalid crime_type. Must be one of: {", ".join(crime_field_map.keys())}'},
            status=status.HTTP_400_BAD_REQUEST
        )

    rate_field, total_field = crime_field_map[crime_type]

    queryset = CrimeData.objects.filter(year=year)

    # Sort by rate or total
    if sort_by == 'total':
        queryset = queryset.order_by(f'-{total_field}')[:limit]
    else:
        queryset = queryset.order_by(f'-{rate_field}')[:limit]

    # Build response with specific crime data
    results = []
    for record in queryset:
        results.append({
            'state': record.state,
            'population': record.population,
            f'{crime_type}_rate': getattr(record, rate_field),
            f'{crime_type}_total': getattr(record, total_field)
        })

    return Response({
        'year': year,
        'crime_type': crime_type,
        'sorted_by': sort_by,
        'states_analyzed': len(results),
        'results': results
    })
