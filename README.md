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
exEco/
│── 
│── 
│── 
│── 
│── manage.py        # Django project management script
│── exEco/           # Project settings and configuration
│── accounts/        # User authentication (if applicable)
│── static/          # Static files (CSS, JS, Images)
│── templates/       # HTML templates
│── db.sqlite3       # SQLite database (auto-generated)
│── requirements.txt # Python dependencies
│── README.md        # Project documentation
```

## **License**

This project is licensed under the GPL-3.0 Public License.
