# exEco

exEco is a Django-based sustainability application designed for the University of Exeter. It promotes and tracks sustainable practices in an engaging and interactive way, combining gamification elements with educational content.

---

## **Features**

- **Forum**: A discussion board for users to share ideas and engage in sustainability-related conversations.
- **Garden**: A 9x9 grid-based feature where users can design and maintain a virtual garden, reflecting their sustainability efforts.
- **Bin Game**: A fun and educational game to teach proper waste segregation.
- **Transport Tracking**: Strava-linked functionality to track eco-friendly transport activities like walking, cycling, and running.
- **QR Scanner**: Scan QR codes at specific locations to learn about sustainability efforts and earn rewards.
- **Shop**: An in-game shop for users to redeem rewards.
- **Leaderboard**: Compete with others by earning points through sustainable actions.

---

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

#### **5. Load Fixtures**

```sh
python manage.py load_fixtures
```

#### **6. Run the Development Server**

```sh
python manage.py runserver
```

The app will be available at **<https://execo-production.up.railway.app>**.

---

## **Project Structure**

```
EXEco/
├── .github/         # GitHub-specific files (workflows, issue templates, etc.)
├── .vscode/         # VS Code settings
├── accounts/        # User authentication and account management
├── bingame/         # Bingo game-related functionality
├── challenges/      # Challenge-related features
├── contact/         # Contact page or support-related functionality
├── dashboard/       # User dashboard and main navigation
├── EXEco/           # Core Django project settings and configuration
├── fixtures/        # Predefined database data for testing
├── forum/           # Forum or discussion board
├── gamekeeper/      # Game-related state management
├── garden/          # Garden feature (9x9 grid persistence)
├── inventory/       # User inventory management
├── media/           # Media file storage (uploads, images, etc.)
├── qrscanner/       # QR code scanning functionality
├── shop/            # In game shop
├── static/          # Static files (CSS, JS, Images)
├── templates/       # HTML templates for rendering views
├── transport/       # Strava-linked transport tracking features
├── .gitignore       # Git ignore file
├── db.sqlite3       # SQLite database file
├── LICENSE          # Project license
├── manage.py        # Django project management script
├── README.md        # Project documentation
└── requirements.txt # Python dependencies
```

---

## **License**

This project is licensed under the GPL-3.0 Public License.
