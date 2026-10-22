# Smart Workflow System for Enhanced Aluminum Recovery and Sustainable Refinement


## Project Overview

The Smart Workflow System helps manage raw-material processing and by-product tracking for aluminum recovery. Agents can submit raw materials and view yield predictions, administrators can manage user approvals, and Scrap Team members can update by-product processing statuses.

## Features

- **Role-based access:** Separate workflows for Admin, Agent, and Scrap Team users.
- **User approval:** Registration requests require administrator approval before access is granted.
- **Raw-material management:** Submit bauxite or scrap aluminum with material quantities.
- **Yield prediction:** Generate lower, predicted, and upper yield estimates using machine-learning functionality.
- **Product tracking:** Associate submitted raw materials with Product IDs.
- **By-product management:** Generate and track relevant by-products, including Red Mud, Aluminum Dross/Residue, and Manganese Alloy, according to the implemented workflow.
- **Status tracking:** Track by-products through Pending, In Progress, and Completed statuses.
- **Assignment management:** Assign individual by-products to Scrap Team users.
- **Process workflow:** Support process-stage tracking, including the Bayer Process for alumina extraction.

## Technology Stack

| Area | Technologies |
|---|---|
| Frontend | React, JavaScript, HTML, CSS |
| Frontend tooling | Vite, npm |
| Backend | Python, Django |
| API | Django REST Framework |
| Database | MySQL |
| Machine learning and data processing | scikit-learn, NumPy, SciPy, pandas, joblib |
| Version control | Git, GitHub |

## Application Workflow

1. A user registers and waits for administrator approval.
2. An approved Agent logs in and submits raw-material information.
3. The system calculates yield estimates and records the processing details.
4. The workflow generates relevant by-product records.
5. By-products can be assigned to Scrap Team users.
6. Scrap Team members update processing statuses through their dashboard.
7. Administrators manage user approvals and monitor the system.

## Project Structure

```text

intern_project/
│
├── backend/
│   │
│   ├── app/
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── forms.py
│   │   ├── models.py
│   │   ├── tests.py
│   │   ├── urls.py
│   │   ├── views.py
│   │   │
│   │   ├── data/
│   │   │   └── aluminum_training_data.csv
│   │   │
│   │   ├── ml/
│   │   │   ├── __init__.py
│   │   │   ├── quantile_model.py
│   │   │   ├── q_table.json
│   │   │   └── rl_model.py
│   │   │
│   │   └── migrations/
│   │       ├── __init__.py
│   │       ├── 0001_initial.py
│   │       ├── 0002_rawmaterial.py
│   │       ├── 0003_delete_rawmaterial.py
│   │       └── 0004_alter_user_id.py
│   │
│   ├── byproducts/
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py
│   │   ├── tests.py
│   │   ├── urls.py
│   │   ├── views.py
│   │   └── migrations/
│   │       ├── __init__.py
│   │       ├── 0001_initial.py
│   │       └── 0002_byproduct_potential_applications.py
│   │
│   ├── processing/
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── forms.py
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── services.py
│   │   ├── tests.py
│   │   ├── urls.py
│   │   ├── views.py
│   │   └── migrations/
│   │       ├── __init__.py
│   │       ├── 0001_initial.py
│   │       ├── 0002_rawmaterial_process_stage.py
│   │       ├── 0003_alter_rawmaterial_material_type_and_more.py
│   │       ├── 0004_rawmaterial_product_id.py
│   │       ├── 0005_alter_rawmaterial_product_id.py
│   │       ├── 0006_alter_rawmaterial_product_id.py
│   │       ├── 0007_alter_rawmaterial_process_stage.py
│   │       ├── 0008_rawmaterial_lower_yield_rawmaterial_upper_yield.py
│   │       ├── 0009_rlfeedback.py
│   │       ├── 0010_rawmaterial_actual_yield_rawmaterial_rl_processed_and_more.py
│   │       └── 0011_rawmaterial_rl_action_rawmaterial_rl_state.py
│   │
│   ├── intern_project/
│   │   ├── __init__.py
│   │   ├── asgi.py
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   │
│   ├── static/
│   │   ├── css/
│   │   │   ├── admin.css
│   │   │   ├── homepage.css
│   │   │   ├── manage_operations.css
│   │   │   ├── manage_users.css
│   │   │   ├── registeration.css
│   │   │   ├── registersuccess.css
│   │   │   └── userlogin.css
│   │   │
│   │   └── react/
│   │       ├── assets/
│   │       │   ├── index-D2XvHyP_.css
│   │       │   └── index-N9cl0yZy.js
│   │       ├── favicon.svg
│   │       ├── icons.svg
│   │       └── index.html
│   │
│   ├── template/
│   │   ├── admin_dashboard.html
│   │   ├── homepage.html
│   │   ├── manage_operations.html
│   │   ├── manage_users.html
│   │   ├── registeration.html
│   │   ├── registersuccess.html
│   │   └── userlogin.html
│   │
│   └── manage.py
│
├── frontend/
│   ├── public/
│   │   ├── favicon.svg
│   │   └── icons.svg
│   │
│   ├── src/
│   │   ├── assets/
│   │   │   └── hero.png
│   │   ├── AgentDashboard.css
│   │   ├── AgentDashboard.jsx
│   │   ├── App.css
│   │   ├── App.jsx
│   │   ├── index.css
│   │   ├── main.jsx
│   │   ├── ScrapDashboard.jsx
│   │   └── scrap_dashboard.css
│   │
│   ├── .gitignore
│   ├── eslint.config.js
│   ├── index.html
│   ├── package-lock.json
│   ├── package.json
│   ├── README.md
│   └── vite.config.js
│
├── .gitignore                 (add/check at repository root)
├── README.md                  (add/check at repository root)
└── backend/requirements.txt   (you created this locally)

```

## Prerequisites

- Python compatible with the installed Django and machine-learning dependencies
- Node.js and npm
- MySQL Server
- Git

## Local Setup

### 1. Clone the repository

```bash
git clone https://github.com/YOUR-USERNAME/smart-aluminum-recovery.git
cd smart-aluminum-recovery
```

Replace `YOUR-USERNAME` with your GitHub username.

### 2. Configure the MySQL database

Create a MySQL database named `intern_db`, or update the database name to match your configuration.

Configure Django to connect to MySQL using environment variables or another secure configuration method. Do not commit database passwords or secret keys to GitHub.

### 3. Set up the Django backend

```bash
cd backend
python -m venv venv
```

Activate the virtual environment.

**Windows PowerShell:**

```powershell
.\venv\Scripts\Activate.ps1
```

Install the dependencies:

```bash
python -m pip install -r requirements.txt
```

Apply database migrations:

```bash
python manage.py migrate
```

Start the development server:

```bash
python manage.py runserver
```


