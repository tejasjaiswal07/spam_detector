# Spam Detection API

A RESTful API for spam detection and contact management, built using Django REST Framework (DRF).

## Features

- User authentication with JWT
- Spam number reporting
- Contact management with search functionality
- Rate limiting for API requests
- Database indexing for performance optimization
- Proper input validation and error handling

---

Setup Instructions

1. Install Dependencies

python -m venv venv

source venv/bin/activate  # On Windows: venv\Scripts\activate

pip install -r requirements.txt


2. Set Up Environment Variables
Create a .env file in the project root with the following content:

DEBUG=True
SECRET_KEY='your-secret-key'
DATABASE_URL=postgresql://postgres:your_passward@127.0.0.1:5432/coding_task_db
ALLOWED_HOSTS=127.0.0.1

3. Apply Database Migrations
python manage.py makemigrations
python manage.py migrate
4. Populate Sample Data
python manage.py populate_data
5. Start the Server

python manage.py runserver


The server will run at http://127.0.0.1:8000/.



API Endpoints


Authentication
POST /api/auth/register/ - Register a new user
POST /api/auth/login/ - Login and get access tokens
POST /api/auth/refresh/ - Refresh access token

Contacts
GET /api/contacts/ - List user’s contacts
POST /api/contacts/ - Add a new contact
GET /api/contacts/{id}/ - Retrieve contact details

Spam Reports
POST /api/spam-reports/ - Report a number as spam
GET /api/spam-reports/ - List all reported spam numbers

Search
GET /api/search/?q={query}&type=name - Search by name
GET /api/search/?q={query}&type=phone - Search by phone number

Project Structure
coding_task/
│── api/                  # API logic
│── settings/             # Django settings
│── manage.py             # Django CLI tool
│── urls.py               # URL routing
│── wsgi.py / asgi.py     # Deployment support
│── requirements.txt      # Dependencies
│── README.md             # Project documentation
│── .env                  # Environment variables
