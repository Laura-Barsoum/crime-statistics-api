# Video Demonstration Script

**Duration:** 7-8 minutes
**Format:** Screen recording with voiceover

---

## Introduction (30 seconds)

**Visual:** Show yourself or desktop

**Script:**
> "Hello, in this video I'll demonstrate my Django REST API application for analyzing US crime statistics. This application was built using Django 6.0 and Django REST Framework, with a SQLite database. Let me walk you through the deployment and main functionalities."

---

## Part 1: Dataset Explanation (45 seconds)

**Visual:** Show CSV file in text editor or show first few rows

**Script:**
> "First, let me explain the dataset. I'm using the State Crime dataset from the CORGIS project, which contains FBI crime statistics for all 50 US states from 1960 to 2019. The dataset includes both violent crimes—murder, rape, robbery, and assault—and property crimes like burglary, larceny, and motor vehicle theft. It has about 3,000 entries total, well under the 10,000 limit.
>
> I chose this dataset because it offers rich opportunities for analysis. We can track crime trends over decades, compare states with different policies, and identify which states are doing better or worse. This type of analysis is valuable for policymakers, researchers, and citizens."

---

## Part 2: Unzipping and Setup (1 minute)

**Visual:** Terminal showing commands

**Script:**
> "Let me start by unzipping the application and setting it up. I'll navigate to my directory and unzip the file."

```bash
cd Desktop
unzip django_proj.zip
cd django_proj
```

> "Now I'll create a virtual environment and install the dependencies using the requirements.txt file."

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

> "The requirements file includes Django 6.0, Django REST Framework 3.15, and a few utility packages for date handling and testing."

---

## Part 3: Database Setup and Migrations (45 seconds)

**Visual:** Terminal showing migration commands

**Script:**
> "Next, I'll set up the database. First, let me run the migrations to create the database schema."

```bash
python manage.py makemigrations
python manage.py migrate
```

> "The migrations create our CrimeData table with all the fields for storing crime statistics—rates and totals for both violent and property crimes. I've also added indexes on state and year fields for fast querying."

---

## Part 4: Creating Superuser (30 seconds)

**Visual:** Terminal showing superuser creation

**Script:**
> "Now I'll create an admin superuser to access the Django admin interface."

```bash
python manage.py createsuperuser
```

> "I'll use 'admin' as the username and 'admin123' as the password for easy testing."

---

## Part 5: Loading Data (1 minute)

**Visual:** Terminal showing data loading command and output

**Script:**
> "Now comes the important part—loading the crime data from the CSV file using our custom management command."

```bash
python manage.py load_crime_data data/state_crime.csv --clear
```

> "This command reads the CSV file, validates each row, and loads it into the database. The script handles different column naming formats and provides progress updates. You can see it's loading the data... and done! It successfully loaded [X] records.
>
> The script is robust—it validates data before insertion, handles duplicates gracefully, and provides clear error messages if anything goes wrong. It's located in crime_api/management/commands/load_crime_data.py."

---

## Part 6: Running Tests (1 minute)

**Visual:** Terminal showing test execution

**Script:**
> "Let's verify everything is working by running the unit tests."

```bash
python manage.py test crime_api
```

> "I've written comprehensive tests covering all endpoints—both success and failure cases. This includes testing CRUD operations, filtering, and all six custom endpoints. You can see all [X] tests passed, confirming the application is working correctly.
>
> The tests are in crime_api/tests.py and cover model validation, serializer behavior, and all API endpoints."

---

## Part 7: Starting the Server (15 seconds)

**Visual:** Terminal showing server start

**Script:**
> "Now let's start the development server."

```bash
python manage.py runserver
```

> "The server is running on localhost port 8000. Let me open a browser and demonstrate the API."

---

## Part 8: Home Page (30 seconds)

**Visual:** Browser showing home page

**Script:**
> "Here's the home page. It displays system information—Python 3.x, Django 6.0, and DRF 3.15. It also shows the admin credentials and, most importantly, lists all the API endpoints with clickable links. Each endpoint has a description and example usage. This makes it easy to explore the API."

---

## Part 9: Demonstrating Endpoints (2 minutes)

**Visual:** Browser showing each endpoint

### Endpoint 1: List Crime Data
**Script:**
> "Let me click on the first endpoint—list all crime data. This shows a paginated list of all records. I can filter by state... here's California data. Or by year... here's 2015 data for all states. The API returns summary information with key metrics."

### Endpoint 2: High Crime States
**Script:**
> "This endpoint identifies states with crime rates above a threshold. Let me set the threshold to 5000 and year to 2015. It returns states exceeding that crime rate, which is useful for identifying areas needing intervention."

### Endpoint 3: Crime Trends
**Script:**
> "Here's the crime trends endpoint for California. It shows how crime has evolved from 2010 to 2015, including average rates, maximums, minimums, and yearly data. This is perfect for evaluating whether policies are working."

### Endpoint 4: Compare States
**Script:**
> "The compare states endpoint lets me compare multiple states side by side. I'll compare California, Texas, and Florida for 2015. It shows population, crime rates, and totals for each state, making it easy to see regional differences."

### Endpoint 5: Safest States
**Script:**
> "This endpoint finds the safest states. For 2015, these are the 5 states with the lowest violent crime rates. This helps identify best practices that other states can learn from."

### Endpoint 6 (if time): Additional endpoints
**Script:**
> "There are additional endpoints for decade comparisons and crime-type analysis that provide even more granular insights."

---

## Part 10: POST Request Demonstration (30 seconds)

**Visual:** Browser or Postman showing POST request

**Script:**
> "Let me demonstrate creating new data using POST. I'll send a request with crime data for a new state-year combination. The API validates all fields—state name, year range, numeric values—and returns the created record. The validation ensures data integrity."

---

## Part 11: Django Admin (30 seconds)

**Visual:** Browser showing Django admin

**Script:**
> "Finally, let me show the Django admin interface. I'll log in with the credentials... Here's the CrimeData table where I can view, edit, and delete records. The admin interface is customized with filters for year and state, and the fields are organized into collapsible sections for better usability."

---

## Part 12: Database Design Discussion (45 seconds)

**Visual:** Show models.py in code editor

**Script:**
> "Let me briefly explain the database design. I use a single CrimeData model with the state and year as the key identifiers. Each record stores both crime rates per 100,000 population and absolute totals. This denormalized design is optimal because crime statistics are atomic—each state-year combination is independent.
>
> I've added validators to ensure data integrity—year must be between 1960 and 2025, all numeric values must be non-negative, and population must be realistic. The composite unique constraint on state and year prevents duplicates. Indexes on these fields ensure fast queries."

---

## Conclusion (30 seconds)

**Visual:** Return to home page or terminal

**Script:**
> "To summarize, this Django REST API application provides comprehensive access to US crime statistics through well-designed endpoints. It demonstrates proper use of Django models, migrations, forms, serializers, and REST framework. The six custom endpoints enable meaningful analysis for researchers, policymakers, and the public.
>
> The application is fully tested, well-documented, and ready for deployment. All code follows Django best practices with clear organization and comprehensive comments. Thank you for watching!"

---

## Tips for Recording

1. **Preparation:**
   - Practice the script a few times
   - Have all commands ready to copy-paste
   - Close unnecessary applications
   - Use a clean desktop

2. **Recording Software:**
   - OBS Studio (free, cross-platform)
   - QuickTime (Mac)
   - Windows Game Bar (Windows)
   - Ensure good audio quality

3. **During Recording:**
   - Speak clearly and at a moderate pace
   - If you make a mistake, pause and continue—you can edit later
   - Show your face briefly at the start (optional but personal)
   - Zoom in on important parts (terminal output, code)

4. **Editing:**
   - Cut out long pauses or errors
   - Speed up slow parts (like package installation) with time-lapse
   - Add captions if audio is unclear
   - Keep the video under 8 minutes

5. **Export Settings:**
   - Format: MP4
   - Resolution: 1920×1080 (1080p) or 1280×720 (720p)
   - Frame rate: 30fps
   - Keep file size under 500MB if uploading

---

## Checklist Before Recording

- [ ] Application is unzipped and ready
- [ ] Virtual environment is deactivated (to show clean setup)
- [ ] CSV file is in data/ directory
- [ ] requirements.txt is present
- [ ] Terminal is clear and visible
- [ ] Browser bookmarks are clean
- [ ] Test all endpoints work correctly
- [ ] Admin credentials are correct
- [ ] Recording software is configured
- [ ] Microphone is working

---

## Alternative: Shorter Version (if running over 8 minutes)

If you're running over time, you can:
- Skip the detailed explanation of some endpoints (pick 3-4 main ones)
- Speed through the installation (show but don't narrate every step)
- Combine the database design discussion with the model demonstration
- Cut the POST demonstration if short on time

**Priority order of what to include:**
1. Dataset explanation and justification ✅
2. Installation and setup ✅
3. Data loading script ✅
4. Running tests ✅
5. At least 3-4 endpoint demonstrations ✅
6. Database design explanation ✅
7. Admin interface (if time permits)
8. POST request (if time permits)

Good luck with your video!
