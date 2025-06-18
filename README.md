# 📚 ManagementProjetApp – TeamStudy

A collaborative platform for managing educational projects.

---

## 🚀 Project Setup

### 1. Clone the repository

```bash
git clone <repository-url>
cd <repository-folder>
```

### 2. Create and activate a virtual environment

```bash
python -m venv env
# Sur Windows :
env\Scripts\activate
# Sur Mac/Linux :
source env/bin/activate
```

### 3.  Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure the database
In myproject/settings.py, configure your PostgreSQL credentials.
Then run the migrations:

```bash
python manage.py makemigrations
python manage.py migrate
```


