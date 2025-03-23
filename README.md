# exEco

exEco is a Django-based sustainability application for the University of Exeter, designed to promote and track sustainable practices in a fun and engaging way.

## **Project Setup**

### **Prerequisites**

Ensure you have the following installed:

- Python (>=3.12)
- Git
- Virtual Environment (venv)

### **Installation**

#### **1. Clone the Repository**

```sh
git clone https://github.com/W3r5l3y/exEco.git
cd exEco
```

#### **2. Set Up a Virtual Environment**

```sh
python -m venv venv  # Create virtual environment
venv\Scripts\activate  # Activate on Windows
source venv/bin/activate  # Activate on macOS/Linux
```

#### **3. Install Dependencies**

```sh
pip install -r requirements.txt
```

#### **4. Apply Migrations**

```sh
python manage.py migrate
```

#### **5. Load Fixtures

````sh
python manage.py load_fixtures
````

#### **6. Run the Development Server**

```sh
python manage.py runserver
```

The app will be available at **http://127.0.0.1:8000/**.

---

## **Project Structure WIP**

```
EXEco/
│── .github/         # GitHub-specific files (workflows, issue templates, etc.)
│── .vscode/         # VS Code settings
│── accounts/        # User authentication and account management
│── bingame/         # Bingo game-related functionality
│── challenges/      # Challenge-related features
│── contact/         # Contact page or support-related functionality
│── dashboard/       # User dashboard and main navigation
│── EXEco/           # Core Django project settings and configuration
│── fixtures/        # Predefined database data for testing
│── forum/           # Forum or discussion board
│── gamekeeper/      # Game-related state management
│── garden/          # Garden feature (9x9 grid persistence)
│── inventory/       # User inventory management
│── media/           # Media file storage (uploads, images, etc.)
│── qrscanner/       # QR code scanning functionality
│── shop/            # In-game or e-commerce shop features
│── static/          # Static files (CSS, JS, Images)
│── templates/       # HTML templates for rendering views
│── transport/       # Strava-linked transport tracking features
│── venv/            # Virtual environment (dependencies)
│── .env             # Environment variables (not tracked in Git)
│── .gitignore       # Git ignore file
│── db.sqlite3       # SQLite database file
│── LICENSE          # Project license
│── manage.py        # Django project management script
│── README.md        # Project documentation
│── requirements.txt # Python dependencies
```

## **License**

This project is licensed under the GPL-3.0 Public License.
