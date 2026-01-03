from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create a router for the ViewSet
router = DefaultRouter()
router.register(r'crime', views.CrimeDataViewSet, basename='crime')

urlpatterns = [
    # ViewSet URLs (CRUD operations)
    path('api/', include(router.urls)),

    # Custom endpoint URLs
    path('api/high-crime-states/', views.high_crime_states, name='high-crime-states'),
    path('api/crime-trends/<str:state_name>/', views.crime_trends, name='crime-trends'),
    path('api/compare-states/', views.compare_states, name='compare-states'),
    path('api/safest-states/', views.safest_states, name='safest-states'),
    path('api/decade-comparison/<str:state_name>/', views.decade_comparison, name='decade-comparison'),
    path('api/crime-type-analysis/', views.crime_type_analysis, name='crime-type-analysis'),
]
