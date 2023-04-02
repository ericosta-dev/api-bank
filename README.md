# Loan Management API

A simple Django REST API to manage loans and their payments.

## Features

- Users can enter loans and their payments.
- Users can view their loans and payments.
- Users can view the outstanding balance of each of their loans.
- Users can't view or edit other users' loans and payments.

## Requirements

- Python 3.8 or higher
- Django 3.2 or higher
- Django REST Framework 3.12 or higher
- djangorestframework_simplejwt 4.7 or higher

## Installation

1. Clone the repository:
```bash
git clone git@github.com:ericosta-dev/api-bank.git
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate
```

3. Install the required dependencies:
```bash
pip install -r requirements.txt
```

4. Environment Configuration

To set up the required environment variables for this project, create a `.env` file in the project root directory. This file will contain the necessary configurations for the Django settings and other services.

Example of a `.env` file:

```bash
SECRET_KEY=mysecretkey
DEBUG=True
```

5. Apply the database migrations:
```bash
python manage.py migrate
```

6. Run the development server:
```bash
python manage.py runserver
```

The API will be accessible at `http://localhost:8000/`.

## API Endpoints

### Authentication

- `POST /api/token/`: Obtain JWT access and refresh tokens.
- `POST /api/token/refresh/`: Refresh the JWT access token.

### Loans

- `GET /api/loans/`: List all loans for the authenticated user.
- `POST /api/loans/`: Create a new loan for the authenticated user.

### Payments

- `GET /api/payments/`: List all payments for the authenticated user's loans.
- `POST /api/payments/`: Create a new payment for the authenticated user's loan.

# Code Coverage - loans/

The following table shows the code coverage report for the files in the `loans/` directory. The report was generated using the coverage tool.

| Name | Stmts | Miss | Cover |
|------|-------|------|-------|
| loans/__init__.py | 0 | 0 | 100% |
| loans/models.py | 40 | 0 | 100% |
| loans/serializers.py | 17 | 0 | 100% |
| loans/tests.py | 85 | 0 | 100% |
| loans/urls.py | 3 | 0 | 100% |
| loans/views.py | 17 | 0 | 100% |
| **Total** | **162** | **0** | **100%** |

As you can see, all the files in the `loans/` directory have a coverage of 100%, indicating that they have been well tested. Keep up the good work!
