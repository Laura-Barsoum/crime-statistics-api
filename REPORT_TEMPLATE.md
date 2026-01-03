# US Crime Statistics REST API - Assignment Report

**Student Name:** [Your Name]
**Student ID:** [Your ID]
**Date:** [Date]

---

## Executive Summary

This report describes the implementation of a RESTful web application using Django and Django REST Framework. The application provides access to comprehensive crime statistics for US states from 1960 to 2019, sourced from the FBI's Unified Crime Reporting program via the CORGIS Datasets Project.

---

## 1. Dataset Selection and Justification

### 1.1 Dataset Information

- **Name:** State Crime Dataset
- **Source:** CORGIS Datasets Project (https://corgis-edu.github.io/corgis/csv/state_crime/)
- **Original Data Source:** U.S. Department of Justice and Federal Bureau of Investigation
- **Size:** Approximately 3,000 entries (50 states × 60 years)
- **Time Period:** 1960-2019
- **Geographic Coverage:** All 50 US states

### 1.2 Why This Dataset is Interesting

The State Crime dataset was chosen for several compelling reasons:

1. **Historical Significance:** 60 years of data allows for meaningful longitudinal analysis of crime trends across different eras of American history, including major policy shifts and social changes.

2. **Policy Relevance:** Crime statistics are crucial for:
   - Evidence-based policy making
   - Resource allocation in law enforcement
   - Evaluating the effectiveness of crime prevention programs
   - Understanding the relationship between demographics and crime

3. **Rich Query Possibilities:** The dataset enables complex and interesting queries:
   - Comparing crime rates across states with different policies
   - Analyzing trends over decades to identify long-term patterns
   - Identifying correlations between population growth and crime rates
   - Examining specific crime types (violent vs. property crimes)

4. **Real-World Application:** This type of API could be used by:
   - Researchers studying criminology and sociology
   - Policy makers evaluating law enforcement strategies
   - Journalists reporting on crime trends
   - Citizens understanding public safety in their states

5. **Data Quality:** The FBI's Unified Crime Reporting program is one of the most reliable crime data sources, ensuring accuracy and consistency.

### 1.3 Dataset Structure

The dataset includes both **crime rates** (per 100,000 population) and **absolute totals** for:

**Violent Crimes:**
- Murder
- Rape
- Robbery
- Assault

**Property Crimes:**
- Burglary
- Larceny
- Motor vehicle theft

This dual representation (rates and totals) allows for both per-capita analysis and understanding of absolute crime burden.

---

## 2. Database Design (R2)

### 2.1 Conceptual Design

The application uses a single, comprehensive `CrimeData` model that captures all necessary information about crime statistics for a specific state in a specific year.

### 2.2 Django Model Implementation

```python
class CrimeData(models.Model):
    # Core identifiers
    state = CharField (indexed for fast lookups)
    year = IntegerField (indexed for temporal queries)
    population = IntegerField (context for rates)

    # Crime rates (per 100,000)
    - property_rate_* (all, burglary, larceny, motor)
    - violent_rate_* (all, assault, murder, rape, robbery)

    # Crime totals (absolute numbers)
    - property_total_* (all, burglary, larceny, motor)
    - violent_total_* (all, assault, murder, rape, robbery)
```

### 2.3 Design Decisions

1. **Single Table vs. Normalized Design:**
   - **Chosen:** Single table (denormalized)
   - **Rationale:** Crime statistics are inherently atomic (each year-state combination is independent). Normalization would add complexity without benefits. All queries naturally filter by state and/or year, making this structure optimal.

2. **Storing Both Rates and Totals:**
   - **Chosen:** Store both computed rates and absolute totals
   - **Rationale:** Prevents recalculation, improves query performance, and allows for both per-capita analysis and understanding absolute crime burden.

3. **Indexing Strategy:**
   - Primary index: `(state, year)` composite
   - Secondary indexes: `state`, `year`
   - **Rationale:** Most queries filter by state, year, or both. These indexes dramatically improve query performance.

4. **Unique Constraint:**
   - `unique_together = ['state', 'year']`
   - **Rationale:** Only one record per state per year should exist, preventing duplicates.

5. **Validators:**
   - MinValueValidator for all numeric fields
   - Year range validation (1960-2025)
   - Population limits (0 to 50 million)
   - **Rationale:** Data integrity at the database level prevents invalid data.

### 2.4 Database Schema

[Insert your database diagram here or describe the schema in detail]

### 2.5 Advantages of This Design

- **Query Performance:** Indexes on state and year enable fast filtering
- **Data Integrity:** Validators and unique constraints prevent invalid data
- **Simplicity:** Single table is easy to understand and maintain
- **Flexibility:** Supports complex filtering and aggregation queries

---

## 3. Application Architecture (R1)

### 3.1 Django Models and Migrations

**File:** `crime_api/models.py`

The CrimeData model includes:
- 20 fields covering all crime statistics
- Built-in validators using Django's validator framework
- Custom properties for computed fields (`total_crimes`, `crime_rate_per_capita`)
- Proper Meta configuration (ordering, indexes, unique constraints)

**Example Code:**
```python
class CrimeData(models.Model):
    state = models.CharField(max_length=100, db_index=True)
    year = models.IntegerField(
        validators=[MinValueValidator(1960), MaxValueValidator(2025)],
        db_index=True
    )
    # ... additional fields

    class Meta:
        unique_together = ['state', 'year']
        indexes = [models.Index(fields=['state', 'year'])]
```

**Migrations:**
The application uses Django's migration system to create the database schema. The initial migration creates all tables, indexes, and constraints.

### 3.2 Forms and Validators

**File:** `crime_api/forms.py`

The CrimeDataForm provides Django form validation:
- State name cleaning and formatting
- Year range validation
- Population value validation
- Cross-field validation for crime totals

**File:** `crime_api/serializers.py`

Three serializers with different purposes:

1. **CrimeDataSerializer:** Full serialization with all fields
2. **CrimeDataCreateSerializer:** Simplified for POST operations
3. **CrimeSummarySerializer:** Lightweight for list views

**Validation Features:**
- State name normalization (title case, trimming)
- Numeric field range validation
- Cross-field validation (e.g., verifying totals match component sums)
- Rate consistency checking (rates vs. totals vs. population)

**Example Code:**
```python
def validate_state(self, value):
    if not value or not value.strip():
        raise serializers.ValidationError("State name cannot be empty.")
    return value.strip().title()
```

### 3.3 Django REST Framework Usage

**ViewSets:**
The CrimeDataViewSet provides standard CRUD operations:
- List (GET /api/crime/)
- Create (POST /api/crime/)
- Retrieve (GET /api/crime/{id}/)
- Update (PUT /api/crime/{id}/)
- Delete (DELETE /api/crime/{id}/)

**API Views:**
Six custom function-based views for specialized queries:
1. high_crime_states
2. crime_trends
3. compare_states
4. safest_states
5. decade_comparison
6. crime_type_analysis

**Configuration:**
```python
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 50,
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
}
```

### 3.4 URL Routing

**File:** `crime_api/urls.py`

Clean, RESTful URL structure:
- `/api/crime/` - CRUD operations via ViewSet
- `/api/high-crime-states/` - High crime state analysis
- `/api/crime-trends/{state}/` - Temporal analysis
- `/api/compare-states/` - Cross-state comparison
- `/api/safest-states/` - Safest state identification
- `/api/decade-comparison/{state}/` - Long-term trends
- `/api/crime-type-analysis/` - Specific crime analysis

**Router Configuration:**
```python
router = DefaultRouter()
router.register(r'crime', views.CrimeDataViewSet, basename='crime')
```

### 3.5 Unit Testing

**File:** `crime_api/tests.py`

Comprehensive test suite covering:

**Model Tests:**
- Model creation and validation
- String representation
- Computed properties
- Unique constraints

**API Tests:**
- All CRUD operations
- Filtering by state, year, year range
- All custom endpoints
- Error handling (404, 400)
- Edge cases

**Serializer Tests:**
- Field validation
- State name cleaning
- Cross-field validation

**Test Coverage:**
- 30+ test cases
- All endpoints covered
- Both success and failure paths tested

**Example Test:**
```python
def test_get_crime_data_list(self):
    url = reverse('crime-list')
    response = self.client.get(url)
    self.assertEqual(response.status_code, status.HTTP_200_OK)
```

---

## 4. REST API Endpoints (R3)

### 4.1 Endpoint 1: List/Create Crime Data (GET/POST)

**URL:** `/api/crime/`

**Methods:** GET, POST

**Purpose:** Standard CRUD operations for crime data

**GET Features:**
- Pagination (50 records per page)
- Filtering by state, year, or year range
- Returns summary view with key metrics

**POST Features:**
- Create new crime records
- Full validation of all fields
- Automatic state name normalization

**Example Request:**
```bash
GET /api/crime/?state=California&year_from=2010&year_to=2015
```

**Example Response:**
```json
{
    "count": 6,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "state": "California",
            "year": 2015,
            "population": 38904296,
            "violent_rate_all": 426.3,
            "property_rate_all": 2490.3,
            "total_crimes": 1134790,
            "crime_rate_per_capita": 2916.6
        }
    ]
}
```

**Why Interesting:** Provides flexible access to raw data with filtering, essential for any analysis

---

### 4.2 Endpoint 2: High Crime States

**URL:** `/api/high-crime-states/`

**Method:** GET

**Parameters:**
- `threshold` (default: 5000): Crime rate threshold
- `year` (optional): Specific year
- `crime_type` (default: 'all'): 'violent', 'property', or 'all'

**Purpose:** Identify states exceeding crime rate thresholds for targeted interventions

**Use Cases:**
- Federal resource allocation
- Identifying states needing assistance
- Comparing high-crime regions

**Example:**
```bash
GET /api/high-crime-states/?threshold=6000&year=2015&crime_type=violent
```

**Response Structure:**
```json
{
    "threshold": 6000,
    "crime_type": "violent",
    "year": 2015,
    "count": 3,
    "results": [...]
}
```

**Implementation Details:**
- Filters based on combined or specific crime types
- Supports historical analysis across all years
- Returns summary statistics

**Why Interesting:** Enables data-driven identification of states with significant crime problems, helping policymakers prioritize resources and interventions.

---

### 4.3 Endpoint 3: Crime Trends

**URL:** `/api/crime-trends/{state_name}/`

**Method:** GET

**Parameters:**
- `state_name` (URL): State to analyze
- `year_from` (optional): Start year
- `year_to` (optional): End year

**Purpose:** Analyze how crime has evolved over time in a specific state

**Use Cases:**
- Evaluating policy effectiveness
- Understanding long-term trends
- Identifying inflection points

**Example:**
```bash
GET /api/crime-trends/California/?year_from=2000&year_to=2019
```

**Response Includes:**
- Year-by-year data
- Statistical aggregates (average, max, min)
- Total counts across time period

**Why Interesting:** Shows whether crime prevention policies are working. For example, if California implemented tough-on-crime laws in 2010, this endpoint would show if violent crime rates decreased afterward.

---

### 4.4 Endpoint 4: Compare States

**URL:** `/api/compare-states/`

**Method:** GET

**Parameters:**
- `states` (required): Comma-separated state names
- `year` (required): Year to compare

**Purpose:** Side-by-side comparison of crime statistics across states

**Use Cases:**
- Understanding regional differences
- Comparing policy approaches
- Identifying best and worst performers

**Example:**
```bash
GET /api/compare-states/?states=California,Texas,Florida&year=2015
```

**Response Structure:**
- Comparison table with key metrics
- Population-adjusted rates
- Detailed breakdown by crime type

**Why Interesting:** Reveals which states are doing better or worse, enabling knowledge transfer of effective strategies. For instance, if Vermont has low crime rates, other states can study their approaches.

---

### 4.5 Endpoint 5: Safest States

**URL:** `/api/safest-states/`

**Method:** GET

**Parameters:**
- `year` (required): Year to analyze
- `limit` (default: 10): Number of states to return
- `crime_type` (default: 'all'): Type of crime to consider

**Purpose:** Identify states with the lowest crime rates

**Use Cases:**
- Identifying best practices
- Understanding factors contributing to low crime
- Benchmarking performance

**Example:**
```bash
GET /api/safest-states/?year=2015&limit=5&crime_type=violent
```

**Why Interesting:** Helps identify what works in crime prevention. States with low crime rates can be studied to understand their successful strategies, which can then be replicated elsewhere.

---

### 4.6 Endpoint 6: Decade Comparison

**URL:** `/api/decade-comparison/{state_name}/`

**Method:** GET

**Purpose:** Compare crime statistics across decades for long-term trend analysis

**Use Cases:**
- Understanding generational changes
- Identifying long-term patterns
- Historical analysis

**Example:**
```bash
GET /api/decade-comparison/Florida/
```

**Response:**
- Decade-by-decade statistics (1960s, 1970s, etc.)
- Average rates per decade
- Total crimes per decade

**Why Interesting:** Provides historical context showing how crime has changed over generations. For example, violent crime peaked in the 1990s nationally but has declined since—this endpoint quantifies those trends for individual states.

---

### 4.7 Endpoint 7: Crime Type Analysis

**URL:** `/api/crime-type-analysis/`

**Method:** GET

**Parameters:**
- `year` (required): Year to analyze
- `crime_type` (required): Specific crime type
- `sort` (default: 'rate'): Sort by 'rate' or 'total'
- `limit` (default: 50): Number of results

**Purpose:** Focus on specific crime types across all states

**Use Cases:**
- Identifying murder hot spots
- Analyzing specific crime problems
- Targeted policy interventions

**Example:**
```bash
GET /api/crime-type-analysis/?year=2015&crime_type=murder&sort=rate&limit=10
```

**Why Interesting:** Allows targeted analysis of specific crimes. For example, if a state has a high murder rate but low property crime, it needs different interventions than a state with the opposite pattern.

---

## 5. Data Loading Implementation (R4)

### 5.1 Management Command

**File:** `crime_api/management/commands/load_crime_data.py`

**Usage:**
```bash
python manage.py load_crime_data data/state_crime.csv
python manage.py load_crime_data data/state_crime.csv --clear
```

### 5.2 Features

1. **Flexible CSV Parsing:**
   - Handles different column naming conventions
   - Supports nested column names (e.g., "Data.Population")
   - Tolerates missing or extra columns

2. **Data Validation:**
   - Validates each row before insertion
   - Reports validation errors with line numbers
   - Continues loading despite individual errors

3. **Duplicate Handling:**
   - Detects existing records (state + year)
   - Option to skip or overwrite duplicates
   - Clear feedback on skipped records

4. **Progress Reporting:**
   - Shows number of records loaded
   - Reports errors and warnings
   - Provides summary statistics

5. **Robust Error Handling:**
   - Graceful handling of malformed data
   - Clear error messages
   - Continues processing after errors

### 5.3 Implementation Details

**Key Functions:**

```python
def parse_row(self, row):
    """Parse CSV row into model fields"""
    # Handle various column name formats
    # Convert data types appropriately
    # Return dictionary ready for model creation

def get_value(self, row, keys, default=0):
    """Try multiple column names to find value"""
    # Flexible column name matching
```

**Process Flow:**
1. Open and validate CSV file
2. For each row:
   - Parse into model fields
   - Check for duplicates
   - Validate data
   - Create database record
   - Report progress
3. Display summary statistics

### 5.4 Why This Approach

- **Bulk Operations:** Efficient loading of thousands of records
- **Idempotent:** Can be run multiple times safely
- **User-Friendly:** Clear progress and error reporting
- **Flexible:** Handles various CSV formats
- **Robust:** Continues despite individual record errors

---

## 6. Code Organization (C1-C7)

### 6.1 File Structure

```
crime_api/
├── models.py          # Data models
├── serializers.py     # DRF serializers
├── views.py           # API views
├── urls.py            # URL routing
├── forms.py           # Django forms
├── admin.py           # Admin configuration
├── tests.py           # Unit tests
├── management/
│   └── commands/
│       └── load_crime_data.py
└── templates/
    └── crime_api/
        └── home.html
```

### 6.2 Code Style Compliance

**C1 - Organization:** ✅
- Clear separation of concerns
- Models, views, serializers in appropriate files
- Management commands in proper directory structure

**C2 - Comments:** ✅
- Comprehensive docstrings for all classes and functions
- Inline comments for complex logic
- Parameter descriptions in docstrings

**C3 - PEP 8:** ✅
- Consistent 4-space indentation
- Proper naming conventions (snake_case for functions, PascalCase for classes)
- Line length within 79-100 characters
- Proper spacing around operators

**C4 - Function Purpose:** ✅
- Each function has a single, clear purpose
- Small, focused functions (typically 10-30 lines)
- Avoid code duplication through reusable functions

**C5 - Naming:** ✅
- Descriptive variable names (`violent_rate_all`, not `vra`)
- Consistent naming patterns across similar entities
- Clear function names describing their action

**C6 - Unit Tests:** ✅
- 30+ test cases covering all endpoints
- Tests for success and failure paths
- Model, serializer, and API tests

**C7 - Hyperlinked Endpoints:** ✅
- Home page at `/` with all endpoints listed
- Clickable links to try each endpoint
- System information displayed (Python, Django versions)
- Admin credentials shown

---

## 7. Development Environment

### 7.1 System Information

- **Operating System:** macOS (Darwin 25.1.0)
- **Python Version:** 3.x
- **Django Version:** 6.0
- **Django REST Framework:** 3.15.2
- **Database:** SQLite3

### 7.2 Packages Used

```
Django==6.0
djangorestframework==3.15.2
coverage==7.6.1
python-dateutil==2.9.0.post0
pytz==2024.2
```

### 7.3 Installation Instructions

1. Extract application: `unzip django_proj.zip`
2. Create virtual environment: `python3 -m venv venv`
3. Activate environment: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Run migrations: `python manage.py migrate`
6. Create superuser: `python manage.py createsuperuser`
7. Load data: `python manage.py load_crime_data data/state_crime.csv`
8. Run server: `python manage.py runserver`

### 7.4 Admin Access

- **URL:** http://127.0.0.1:8000/admin/
- **Username:** admin
- **Password:** admin123

### 7.5 Running Tests

```bash
# All tests
python manage.py test crime_api

# With coverage
coverage run --source='.' manage.py test crime_api
coverage report
```

### 7.6 Data Loading Script Location

**Path:** `crime_api/management/commands/load_crime_data.py`

**Usage:**
```bash
python manage.py load_crime_data data/state_crime.csv [--clear]
```

---

## 8. Testing Results

[Include test output here]

Example:
```
Ran 30 tests in 2.451s

OK

Creating test database...
System check identified no issues (0 silenced).
..............................
----------------------------------------------------------------------
Ran 30 tests in 2.451s

OK
Destroying test database...
```

---

## 9. Challenges and Solutions

### 9.1 Challenge 1: Data Validation

**Problem:** Need to ensure data consistency (e.g., crime totals matching component sums)

**Solution:** Implemented multi-layer validation:
- Model-level validators
- Form validation
- Serializer validation with custom logic

### 9.2 Challenge 2: Complex Queries

**Problem:** Some endpoints require complex aggregations and filtering

**Solution:** Used Django ORM's advanced features:
- Aggregate functions (Avg, Max, Min, Sum)
- Q objects for complex filtering
- Custom Python logic for decade grouping

### 9.3 Challenge 3: Performance

**Problem:** Listing thousands of records could be slow

**Solution:**
- Pagination (50 records per page)
- Database indexing on frequently queried fields
- Lightweight serializer for list views

---

## 10. Future Enhancements

If this project were to be extended, possible enhancements include:

1. **Geographic Visualization:**
   - Choropleth maps showing crime rates
   - Interactive visualizations

2. **Predictive Analytics:**
   - Machine learning models to forecast crime trends
   - Anomaly detection for unusual crime patterns

3. **Additional Data Sources:**
   - Economic indicators
   - Education statistics
   - Weather data

4. **Advanced Filtering:**
   - Filter by crime rate ranges
   - Multiple year comparisons
   - Custom aggregation periods

5. **Export Functionality:**
   - Export results to CSV, Excel
   - Generate PDF reports

---

## 11. Conclusion

This project successfully implements a comprehensive RESTful web service for crime statistics analysis using Django and Django REST Framework. The application demonstrates:

- Proper use of Django models, forms, and migrations
- Effective implementation of DRF serializers and views
- Complex query capabilities through 6+ interesting endpoints
- Robust data loading from CSV files
- Comprehensive unit testing
- Clean code organization following best practices

The State Crime dataset provides rich opportunities for meaningful analysis, and the implemented endpoints enable various stakeholders—from researchers to policymakers—to gain insights into crime trends across US states over six decades.

The application is fully functional, well-tested, and documented, meeting all assignment requirements (R1-R4 and C1-C7).

---

## 12. References

1. CORGIS Datasets Project. (n.d.). State Crime Dataset. Retrieved from https://corgis-edu.github.io/corgis/csv/state_crime/

2. Federal Bureau of Investigation. Unified Crime Reporting Program. U.S. Department of Justice.

3. Django Software Foundation. (2024). Django Documentation (Version 6.0). https://docs.djangoproject.com/

4. Encode. (2024). Django REST Framework Documentation (Version 3.15). https://www.django-rest-framework.org/

---

## Appendices

### Appendix A: Complete Endpoint List

[List all endpoints with URLs and descriptions]

### Appendix B: Database Schema Diagram

[Include ER diagram or schema visualization]

### Appendix C: Sample API Responses

[Include example JSON responses for each endpoint]

### Appendix D: Test Coverage Report

[Include coverage report if using coverage.py]

---

**Word Count:** [Approximately 2000 words - adjust as needed]
