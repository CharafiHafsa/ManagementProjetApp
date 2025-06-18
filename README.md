# 📚 ManagementProjetApp – TeamStudy

Plateforme collaborative pour la gestion de projets éducatifs.

---

##  Mise en place du projet

### 1. Cloner le dépôt

```bash
git clone <repository-url>
cd <repository-folder>
```

### 2. Créer et activer un environnement virtuel

```bash
python -m venv env
# Sur Windows :
env\Scripts\activate
# Sur Mac/Linux :
source env/bin/activate
```

### 3.  Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Configurer la base de données
Dans myproject/settings.py, configurez les identifiants PostgreSQL.
Puis lancez les migrations :

```bash
python manage.py makemigrations
python manage.py migrate
```


