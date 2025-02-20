# EpicEvents
12th OC project "Develop a securized bakend architecture using Python and Sql"

## Installation Guide

### Prerequisites
Ensure you have the following installed on your system:
- Python 3.9 or later
- pip (Python package manager)
- virtualenv (optional but recommended)
- PostgreSQL (or your preferred database)

### Setting Up the Project

#### 1. Clone the Repository
```sh
git clone https://github.com/HDanDev/EpicEvents.git
cd EpicEvents
```

#### 2. Create and Activate Virtual Environment

```sh
python -m venv venv
```
On Windows:
```sh
venv\Scripts\activate
```
On macOS/Linux:
```sh
source venv/bin/activate
```

#### 3. Install Dependencies
```sh
pip install -r requirements.txt
```

#### 4. Configure Environment Variables
Create a `.env` file at the root of the project and add the necessary configurations:
```ini
DB_USERNAME=
DB_PASSWORD=
DB_NAME=
DB_HOST=
HASH_SECRET_KEY=
MAIN_MANAGER_EMAIL=
MAIN_MANAGER_PASSWORD=
MAIN_MANAGER_HASHED_PASSWORD=
SENTRY_URL=
```

#### 5. Initialize Database
```sh
flask db init
flask db migrate
flask db upgrade
```

#### 6. Run the Application
```sh
flask run
```

The application will be accessible at `http://127.0.0.1:5000/`.

## Features
- User Authentication and Role-Based Access Control
- Manage Collaborators, Clients, Contracts, and Events
- Secure Data Handling with SQLAlchemy
- Logging and Error Tracking with Sentry



