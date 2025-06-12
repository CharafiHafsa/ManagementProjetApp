#!/bin/bash

# Script d'automatisation pour la création de projets Django - Version complète et corrigée

set -e  # Arrêter le script en cas d'erreur

# Variables globales
SCRIPT_NAME=$(basename "$0")
PROJECT_NAME=""
LOG_DIR="/var/log"
RESET_PROJECT=false
INIT_GIT=false
GENERATE_DOCKERFILE=false
FORK_MODE=false
THREAD_MODE=false
SUBSHELL_MODE=false
GUI_MODE=false
GUI_TOOL=""

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction d'affichage de l'aide
show_help() {
    cat << EOF
Usage: $SCRIPT_NAME [OPTIONS] -n <nom_projet>

Script d'automatisation pour la création de projets Django.

OPTIONS:
    -h              Affiche cette aide détaillée
    -f              Exécute la création du projet via un sous-processus fork
    -t              Exécute en thread/background (avec &)
    -s              Exécute dans un sous-shell (create_project)
    -l <chemin>     Spécifie le répertoire de log personnalisé (défaut: /var/log)
    -r              Réinitialise le projet (supprime s'il existe déjà)
    -n <nom>        Spécifie le nom du projet Django (OBLIGATOIRE)
    -d              Génère un Dockerfile dans le projet
    -g              Initialise Git dans le projet
    --gui           Active le mode interface graphique (boîtes de dialogue)

EXEMPLES:
    $SCRIPT_NAME -n monprojet
    $SCRIPT_NAME -n monprojet -g -d -l ./logs
    $SCRIPT_NAME -f -n monprojet -r -g -d
    $SCRIPT_NAME --gui -n monprojet -g -d

EOF
}

# Fonction de vérification des privilèges
check_privileges() {
    local option=$1
    # Cette fonction peut être étendue selon les besoins de sécurité
    return 0
}

# Fonction de base pour demander confirmation à l'utilisateur
ask_user() {
    local question=$1
    local response
    
    while true; do
        read -p "$question (o/n): " response
        case $response in
            [Oo]|[Oo][Uu][Ii]|[Yy]|[Yy][Ee][Ss])
                return 0
                ;;
            [Nn]|[Nn][Oo][Nn])
                return 1
                ;;
            *)
                echo "Veuillez répondre par 'o' (oui) ou 'n' (non)."
                ;;
        esac
    done
}

# Fonction de détection et initialisation de l'outil GUI
init_gui_tool() {
    if [ "$GUI_MODE" = false ]; then
        return 0
    fi
    
    # Vérifier les outils GUI disponibles par ordre de préférence
    if command -v zenity &> /dev/null; then
        GUI_TOOL="zenity"
        log_message "INFO" "Utilisation de Zenity pour l'interface graphique"
    elif command -v kdialog &> /dev/null; then
        GUI_TOOL="kdialog"
        log_message "INFO" "Utilisation de KDialog pour l'interface graphique"
    elif command -v whiptail &> /dev/null; then
        GUI_TOOL="whiptail"
        log_message "INFO" "Utilisation de Whiptail pour l'interface graphique"
    elif command -v dialog &> /dev/null; then
        GUI_TOOL="dialog"
        log_message "INFO" "Utilisation de Dialog pour l'interface graphique"
    else
        log_message "WARNING" "Aucun outil GUI disponible. Tentative d'installation..."
        
        # Tentative d'installation automatique
        if command -v apt-get &> /dev/null; then
            if sudo apt-get update && sudo apt-get install -y zenity; then
                GUI_TOOL="zenity"
                log_message "INFO" "Zenity installé avec succès"
            else
                log_message "WARNING" "Impossible d'installer zenity. Basculement en mode console."
                GUI_MODE=false
                return 1
            fi
        elif command -v yum &> /dev/null; then
            if sudo yum install -y zenity; then
                GUI_TOOL="zenity"
                log_message "INFO" "Zenity installé avec succès"
            else
                log_message "WARNING" "Impossible d'installer zenity. Basculement en mode console."
                GUI_MODE=false
                return 1
            fi
        else
            log_message "WARNING" "Gestionnaire de paquets non supporté. Basculement en mode console."
            GUI_MODE=false
            return 1
        fi
    fi
    
    return 0
}

# Fonction d'affichage de message GUI
gui_message() {
    local type=$1
    local title=$2
    local message=$3
    
    if [ "$GUI_MODE" = false ]; then
        echo "$message"
        return
    fi
    
    case $GUI_TOOL in
        "zenity")
            case $type in
                "info")
                    zenity --info --title="$title" --text="$message" --width=400
                    ;;
                "warning")
                    zenity --warning --title="$title" --text="$message" --width=400
                    ;;
                "error")
                    zenity --error --title="$title" --text="$message" --width=400
                    ;;
            esac
            ;;
        "kdialog")
            case $type in
                "info")
                    kdialog --msgbox "$message" --title "$title"
                    ;;
                "warning")
                    kdialog --sorry "$message" --title "$title"
                    ;;
                "error")
                    kdialog --error "$message" --title "$title"
                    ;;
            esac
            ;;
        "whiptail"|"dialog")
            $GUI_TOOL --title "$title" --msgbox "$message" 10 60
            ;;
    esac
}

# Fonction de question GUI
gui_ask_user() {
    local question=$1
    local title=${2:-"Confirmation"}
    
    if [ "$GUI_MODE" = false ]; then
        ask_user "$question"
        return $?
    fi
    
    case $GUI_TOOL in
        "zenity")
            zenity --question --title="$title" --text="$question" --width=400
            return $?
            ;;
        "kdialog")
            kdialog --yesno "$question" --title "$title"
            return $?
            ;;
        "whiptail"|"dialog")
            $GUI_TOOL --title "$title" --yesno "$question" 8 60
            return $?
            ;;
    esac
}

# Fonction de confirmation GUI
gui_confirm() {
    gui_ask_user "$1" "Confirmation"
    return $?
}

# Fonction de saisie de texte GUI
gui_input() {
    local prompt=$1
    local title=${2:-"Saisie"}
    local default=${3:-""}
    
    if [ "$GUI_MODE" = false ]; then
        local input
        read -p "$prompt" input
        echo "$input"
        return
    fi
    
    local result=""
    case $GUI_TOOL in
        "zenity")
            result=$(zenity --entry --title="$title" --text="$prompt" --entry-text="$default" --width=400)
            ;;
        "kdialog")
            result=$(kdialog --inputbox "$prompt" "$default" --title "$title")
            ;;
        "whiptail"|"dialog")
            result=$($GUI_TOOL --title "$title" --inputbox "$prompt" 8 60 "$default" 3>&1 1>&2 2>&3)
            ;;
    esac
    echo "$result"
}

# Fonction de logging
log_message() {
    local level=$1
    local message=$2
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    local log_file="$LOG_DIR/django_automation.log"
    
    # Créer le répertoire de log s'il n'existe pas et vérifier les permissions
    if [ ! -d "$LOG_DIR" ]; then
        if ! mkdir -p "$LOG_DIR" 2>/dev/null; then
            LOG_DIR="./logs"
            mkdir -p "$LOG_DIR" 2>/dev/null || true
            log_file="$LOG_DIR/django_automation.log"
        fi
    fi
    
    # Écrire dans le fichier de log si possible
    echo "[$timestamp] [$$] [$level] $message" >> "$log_file" 2>/dev/null || true
    
    # Affichage coloré selon le niveau
    case $level in
        "ERROR")
            echo -e "${RED}[ERROR]${NC} $message" >&2
            ;;
        "WARNING")
            echo -e "${YELLOW}[WARNING]${NC} $message"
            ;;
        "INFO")
            echo -e "${BLUE}[INFO]${NC} $message"
            ;;
        "SUCCESS")
            echo -e "${GREEN}[SUCCESS]${NC} $message"
            ;;
    esac
}

# Fonction de création du répertoire de logs
create_log_directory() {
    if [ ! -d "$LOG_DIR" ]; then
        if ! mkdir -p "$LOG_DIR" 2>/dev/null; then
            LOG_DIR="./logs"
            mkdir -p "$LOG_DIR" 2>/dev/null || true
        fi
    fi
    log_message "INFO" "Répertoire de logs: $LOG_DIR"
}

# Fonction de vérification des dépendances système
check_system_dependencies() {
    log_message "INFO" "Vérification des dépendances système..."
    
    local missing_deps=()
    
    # Vérifier Python 3
    if ! command -v python3 &> /dev/null; then
        missing_deps+=("python3")
    fi
    
    # Vérifier pip3
    if ! command -v pip3 &> /dev/null; then
        missing_deps+=("python3-pip")
    fi
    
    # Vérifier git
    if ! command -v git &> /dev/null; then
        missing_deps+=("git")
    fi
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        log_message "WARNING" "Dépendances manquantes: ${missing_deps[*]}"
        install_system_dependencies "${missing_deps[@]}"
    else
        log_message "SUCCESS" "Toutes les dépendances système sont présentes"
    fi
}

# Fonction d'installation des dépendances système
install_system_dependencies() {
    local deps=("$@")
    log_message "INFO" "Installation des dépendances: ${deps[*]}"
    
    if command -v apt-get &> /dev/null; then
        sudo apt-get update
        sudo apt-get install -y "${deps[@]}"
    elif command -v yum &> /dev/null; then
        sudo yum install -y "${deps[@]}"
    elif command -v pacman &> /dev/null; then
        sudo pacman -S --noconfirm "${deps[@]}"
    else
        log_message "ERROR" "Gestionnaire de paquets non supporté"
        return 1
    fi
}

# Fonction de reset du projet
reset_project() {
    local project_name=$1
    if [ -d "$project_name" ]; then
        log_message "WARNING" "Suppression du projet existant: $project_name"
        rm -rf "$project_name"
        log_message "SUCCESS" "Projet $project_name supprimé"
    fi
}

# Fonction de vérification des dépendances
check_dependencies() {
    log_message "INFO" "Vérification des dépendances..."
    
    local deps=("python3" "pip3" "git")
    local missing_deps=()
    
    for dep in "${deps[@]}"; do
        if ! command -v "$dep" &> /dev/null; then
            missing_deps+=("$dep")
        fi
    done
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        log_message "WARNING" "Dépendances manquantes détectées: ${missing_deps[*]}"
        log_message "INFO" "Installation des dépendances manquantes..."
        
        # Détection du gestionnaire de paquets
        if command -v apt-get &> /dev/null; then
            sudo apt-get update
            for dep in "${missing_deps[@]}"; do
                case $dep in
                    "python3")
                        sudo apt-get install -y python3 python3-venv
                        ;;
                    "pip3")
                        sudo apt-get install -y python3-pip
                        ;;
                    "git")
                        sudo apt-get install -y git
                        ;;
                esac
            done
        elif command -v yum &> /dev/null; then
            for dep in "${missing_deps[@]}"; do
                case $dep in
                    "python3")
                        sudo yum install -y python3 python3-venv
                        ;;
                    "pip3")
                        sudo yum install -y python3-pip
                        ;;
                    "git")
                        sudo yum install -y git
                        ;;
                esac
            done
        elif command -v pacman &> /dev/null; then
            for dep in "${missing_deps[@]}"; do
                case $dep in
                    "python3")
                        sudo pacman -S --noconfirm python python-virtualenv
                        ;;
                    "pip3")
                        sudo pacman -S --noconfirm python-pip
                        ;;
                    "git")
                        sudo pacman -S --noconfirm git
                        ;;
                esac
            done
        else
            log_message "ERROR" "Gestionnaire de paquets non supporté. Veuillez installer manuellement: ${missing_deps[*]}"
            return 1
        fi
    fi
    
    # Vérifier Django
    if ! python3 -c "import django" 2>/dev/null; then
        log_message "INFO" "Installation de Django..."
        if ! pip3 install django; then
            log_message "ERROR" "Échec de l'installation de Django"
            return 1
        fi
    fi
    
    log_message "SUCCESS" "Toutes les dépendances sont installées"
    return 0
}

# Fonction de création du projet Django
create_django_project() {
    log_message "INFO" "Création du projet Django: $PROJECT_NAME"
    
    # Vérifier si le projet existe déjà
    if [ -d "$PROJECT_NAME" ]; then
        if [ "$RESET_PROJECT" = true ]; then
            log_message "WARNING" "Suppression du projet existant: $PROJECT_NAME"
            rm -rf "$PROJECT_NAME"
        else
            log_message "ERROR" "Le projet $PROJECT_NAME existe déjà. Utilisez -r pour le réinitialiser."
            return 1
        fi
    fi
    
    # Créer le projet Django
    if ! django-admin startproject "$PROJECT_NAME"; then
        log_message "ERROR" "Échec de la création du projet Django"
        return 1
    fi
    
    if ! cd "$PROJECT_NAME"; then
        log_message "ERROR" "Impossible d'accéder au répertoire du projet"
        return 1
    fi
    
    log_message "SUCCESS" "Projet Django créé avec succès"
    return 0
}

# Fonction de configuration du projet
configure_project() {
    log_message "INFO" "Configuration du projet Django..."
    
    # Créer un environnement virtuel
    if ! python3 -m venv venv; then
        log_message "ERROR" "Échec de la création de l'environnement virtuel"
        return 1
    fi
    
    # Activer l'environnement virtuel et installer les dépendances
    if ! source venv/bin/activate; then
        log_message "ERROR" "Échec de l'activation de l'environnement virtuel"
        return 1
    fi
    
    if ! pip install django; then
        log_message "ERROR" "Échec de l'installation de Django dans l'environnement virtuel"
        return 1
    fi
    
    # Créer requirements.txt
    pip freeze > requirements.txt
    
    # Effectuer les migrations initiales
    if ! python manage.py migrate; then
        log_message "WARNING" "Échec des migrations initiales"
    fi
    
    log_message "SUCCESS" "Configuration du projet terminée"
    return 0
}

# Vérifie et configure l'identité Git si absente
check_git_identity() {
    local git_name
    local git_email

    git_name=$(git config --global user.name 2>/dev/null || echo "")
    git_email=$(git config --global user.email 2>/dev/null || echo "")

    if [ -z "$git_name" ] || [ -z "$git_email" ]; then
        log_message "WARNING" "Identité Git non configurée"

        if [ "$GUI_MODE" = true ]; then
            git_name=$(gui_input "Entrez votre nom pour Git (ex: Leila Nineflas):" "Nom Git")
            git_email=$(gui_input "Entrez votre email pour Git (ex: leila@example.com):" "Email Git")
        else
            read -p "Nom pour Git (ex: Leila Nineflas) : " git_name
            read -p "Email pour Git (ex: leila@example.com) : " git_email
        fi

        if [ -n "$git_name" ] && [ -n "$git_email" ]; then
            git config --global user.name "$git_name"
            git config --global user.email "$git_email"
            log_message "INFO" "Identité Git configurée : $git_name <$git_email>"
        else
            log_message "ERROR" "Nom ou email Git vide. Abandon de la configuration Git."
            return 1
        fi
    else
        log_message "INFO" "Identité Git détectée : $git_name <$git_email>"
    fi
    return 0
}

# Fonction d'initialisation Git avec push vers GitHub
git_push_with_token() {
    if [ "$INIT_GIT" = false ]; then
        return 0
    fi
    
    log_message "INFO" "Initialisation du dépôt Git"
    
    if ! git init; then
        log_message "ERROR" "Échec de l'initialisation Git"
        return 1
    fi
    
    # Configurer la branche principale
    git config init.defaultBranch main 2>/dev/null || true
    if ! git checkout -b main 2>/dev/null; then
        # Si on est déjà sur main ou si checkout échoue, continuer
        true
    fi

    log_message "INFO" "Création du .gitignore"
    cat > .gitignore << 'EOF'
# Python
*.pyc
_pycache_/
*.pyo
*.pyd
.Python
env/
venv/
ENV/
env.bak/
venv.bak/

# Django
db.sqlite3
media/
staticfiles/
.env
local_settings.py

# IDEs
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log
EOF

    log_message "INFO" "Ajout des fichiers et commit initial"
    git add .
    if ! git commit -m "Initial commit - Django project setup"; then
        log_message "ERROR" "Échec du commit initial"
        return 1
    fi

    # AJOUT DE LA DEMANDE DE CONFIRMATION POUR LE PUSH
    log_message "INFO" "Dépôt Git initialisé localement avec succès"
    
    local should_push=false
    if [ "$GUI_MODE" = true ]; then
        if gui_ask_user "Voulez-vous pousser le projet vers un dépôt GitHub distant ?"; then
            should_push=true
        fi
    else
        if ask_user "Voulez-vous pousser le projet vers un dépôt GitHub distant ?"; then
            should_push=true
        fi
    fi
    
    # Si l'utilisateur ne veut pas pousser, arrêter ici
    if [ "$should_push" = false ]; then
        log_message "INFO" "Projet Git initialisé localement seulement (pas de push vers GitHub)"
        return 0
    fi

    # Demander l'URL du dépôt GitHub
    local github_url
    if [ "$GUI_MODE" = true ]; then
        github_url=$(gui_input "Entrez l'URL HTTPS du dépôt GitHub (ex: https://github.com/user/repo.git):" "URL GitHub")
    else
        read -p "Entrez l'URL HTTPS du dépôt GitHub (ex: https://github.com/user/repo.git): " github_url
    fi
    
    if [ -z "$github_url" ]; then
        log_message "INFO" "Aucune URL fournie. Git initialisé localement seulement."
        return 0
    fi
    
    if ! git remote add origin "$github_url"; then
        log_message "ERROR" "Échec de l'ajout du dépôt distant"
        return 1
    fi

    echo ""
    echo "=== Instructions pour le Personal Access Token ==="
    echo "1. Allez sur https://github.com/settings/tokens"
    echo "2. Cliquez sur 'Generate new token (classic)'"
    echo "3. Cochez 'repo', puis générez le token"
    echo "4. Copiez le token généré"
    echo ""
    echo "   Lors du push, entrez :"
    echo "   - Username: votre nom d'utilisateur GitHub"
    echo "   - Password: le token (PAS votre mot de passe)"
    echo ""

    if [ "$GUI_MODE" = false ]; then
        read -p "Appuyez sur Entrée lorsque vous êtes prêt(e) à pousser..."
    else
        gui_message "info" "GitHub Token" "Configurez votre token GitHub selon les instructions affichées dans le terminal, puis cliquez OK pour continuer."
    fi

    log_message "INFO" "Poussée vers GitHub"
    if git push -u origin main; then
        log_message "SUCCESS" "Projet déployé avec succès sur GitHub"
    else
        log_message "ERROR" "Push échoué. Vérifiez l'URL du dépôt et votre token"
        return 1
    fi
    
    return 0
}

# Fonction de génération du Dockerfile
generate_dockerfile() {
    # Si l'option -d n'est pas activée, ne pas proposer la dockerisation
    if [ "$GENERATE_DOCKERFILE" = false ]; then
        return 0  # Sortir silencieusement sans rien faire
    fi
    
    log_message "INFO" "Génération du Dockerfile..."
    
    cat > Dockerfile << 'EOF'
FROM python:3.9-slim

WORKDIR /app

# Installer les dépendances système
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copier les fichiers de requirements
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code de l'application
COPY . .

# Collecter les fichiers statiques
RUN python manage.py collectstatic --noinput || true

# Exposer le port
EXPOSE 8000

# Commande par défaut
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
EOF
    
    # Créer docker-compose.yml
    cat > docker-compose.yml << EOF
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - .:/app
    environment:
      - DEBUG=1
      - DJANGO_SETTINGS_MODULE=$PROJECT_NAME.settings
EOF
    
    log_message "SUCCESS" "Dockerfile et docker-compose.yml générés avec succès"
    return 0
}

# Fonction pour lancer l'application
launch_app() {
    local should_launch=false
    
    if [ "$GUI_MODE" = true ]; then
        if gui_ask_user "Voulez-vous lancer l'application Django maintenant ?"; then
            should_launch=true
        fi
    else
        if ask_user "Voulez-vous lancer l'application Django maintenant ?"; then
            should_launch=true
        fi
    fi
    
    if [ "$should_launch" = true ]; then
        log_message "INFO" "Lancement de l'application Django..."
        echo -e "${GREEN}L'application sera accessible sur http://127.0.0.1:8000${NC}"
        echo -e "${YELLOW}Appuyez sur Ctrl+C pour arrêter le serveur${NC}"
        
        # Activer l'environnement virtuel si disponible
        if [ -f "venv/bin/activate" ]; then
            source venv/bin/activate
        fi
        
        python manage.py runserver
    fi
}

# Fonction utilitaire pour vérifier le statut d'un processus
check_process_status() {
    local pid=$1
    local description=$2
    
    if kill -0 "$pid" 2>/dev/null; then
        echo "[INFO] $description (PID $pid) est en cours d'exécution"
        return 0
    else
        echo "[INFO] $description (PID $pid) est terminé"
        return 1
    fi
}

# Fonction pour nettoyer les fichiers temporaires
cleanup_temp_files() {
    local project_name=$1
    rm -f "./${project_name}_fork.log" "./${project_name}_thread.log" 
    rm -f "./${project_name}_fork_status" "./${project_name}_thread.pid"
}

# Fonction pour suivre les logs en temps réel
follow_logs() {
    local log_file=$1
    local pid=$2
    
    echo "=== Suivi des logs en temps réel ==="
    echo "Tapez 'q' puis Entrée pour quitter le suivi"
    echo "==================================="
    
    # Suivre les logs en arrière-plan
    tail -f "$log_file" &
    tail_pid=$!
    
    # Attendre l'input utilisateur
    while read -r key; do
        if [[ $key == "q" ]]; then
            kill $tail_pid 2>/dev/null
            break
        fi
    done
    
    # Vérifier si le processus principal est toujours actif
    if ! kill -0 "$pid" 2>/dev/null; then
        echo "[INFO] Processus terminé"
        kill $tail_pid 2>/dev/null
    fi
}

# Gestionnaire de signaux pour nettoyage
cleanup_on_exit() {
    echo "[INFO] Nettoyage en cours..."
    cleanup_temp_files "$PROJECT_NAME"
    exit 0
}

# Fonction principale de création de projet
create_project() {
    log_message "INFO" "Début de la création du projet Django: $PROJECT_NAME"
    
    # Vérification des dépendances
    if ! check_dependencies; then
        log_message "ERROR" "Échec de la vérification des dépendances"
        return 1
    fi
    
    # Création du projet Django
    if ! create_django_project; then
        log_message "ERROR" "Échec de la création du projet Django"
        return 1
    fi
    
    # Configuration du projet
    if ! configure_project; then
        log_message "ERROR" "Échec de la configuration du projet"
        return 1
    fi
    
    # Vérification de l'identité Git
    if ! check_git_identity; then
        log_message "WARNING" "Problème avec l'identité Git, mais continuation du processus"
    fi

    # Initialisation Git et push
    if ! git_push_with_token; then
        log_message "WARNING" "Problème avec Git/GitHub, mais projet créé localement"
    fi
    
    # Génération du Dockerfile
    if ! generate_dockerfile; then
        log_message "WARNING" "Problème avec la génération Docker, mais projet fonctionnel"
    fi
    
    # Lancement de l'application
    launch_app
    
    local success_msg="Création du projet terminée avec succès!\n\nProjet: $PROJECT_NAME\nEmplacement: $(pwd)"
    if [ "$GUI_MODE" = true ]; then
        gui_message "info" "Succès" "$success_msg"
    fi
    log_message "SUCCESS" "Création du projet terminée avec succès!"
    return 0
}

# Fonction d'exécution en mode fork
run_in_fork_mode() {
    log_message "INFO" "Exécution en mode fork"
    
    # Créer un fichier de log spécifique
    local fork_log="${PROJECT_NAME}_fork.log"
    local fork_status="${PROJECT_NAME}_fork_status"
    
    # Lancer le processus en fork
    (
        create_project > "$fork_log" 2>&1
        echo $? > "$fork_status"
    ) &
    
    local fork_pid=$!
    log_message "INFO" "Processus fork lancé avec PID: $fork_pid"
    
    # Suivre les logs
    follow_logs "$fork_log" "$fork_pid"
    
    # Attendre la fin du processus
    wait $fork_pid
    local exit_code=$(cat "$fork_status" 2>/dev/null || echo "1")
    
    if [ "$exit_code" -eq 0 ]; then
        log_message "SUCCESS" "Processus fork terminé avec succès"
    else
        log_message "ERROR" "Processus fork échoué"
    fi
    
    # Nettoyage
    rm -f "$fork_log" "$fork_status"
}

# Fonction d'exécution en mode thread
run_in_thread_mode() {
    log_message "INFO" "Exécution en mode thread (arrière-plan)"
    
    # Créer un fichier de log spécifique
    local thread_log="${PROJECT_NAME}_thread.log"
    local thread_pid_file="${PROJECT_NAME}_thread.pid"
    
    # Lancer le processus en arrière-plan
    (
        echo $ > "$thread_pid_file"
        create_project > "$thread_log" 2>&1
        local exit_code=$?
        rm -f "$thread_pid_file"
        exit $exit_code
    ) &
    
    local thread_pid=$!
    log_message "INFO" "Processus thread lancé avec PID: $thread_pid"
    log_message "INFO" "Logs disponibles: tail -f $thread_log"
    
    # Proposer de suivre les logs
    if [ "$GUI_MODE" = true ]; then
        if gui_ask_user "Voulez-vous suivre les logs en temps réel ?"; then
            follow_logs "$thread_log" "$thread_pid"
        else
            log_message "INFO" "Le processus continue en arrière-plan"
        fi
    else
        if ask_user "Voulez-vous suivre les logs en temps réel ?"; then
            follow_logs "$thread_log" "$thread_pid"
        else
            log_message "INFO" "Le processus continue en arrière-plan"
            log_message "INFO" "Commandes utiles:"
            echo "  - Suivre les logs: tail -f $thread_log"
            echo "  - Arrêter le processus: kill $thread_pid"
            echo "  - Vérifier le statut: kill -0 $thread_pid && echo 'En cours' || echo 'Terminé'"
        fi
    fi
}

# Fonction d'exécution en mode subshell
run_in_subshell_mode() {
    log_message "INFO" "Exécution en mode sous-shell"
    
    # Exécuter dans un sous-shell isolé
    (
        log_message "INFO" "Démarrage du sous-shell (PID $)"
        create_project
        local exit_code=$?
        
        if [ $exit_code -eq 0 ]; then
            log_message "SUCCESS" "Sous-shell terminé avec succès"
        else
            log_message "ERROR" "Sous-shell échoué avec le code $exit_code"
        fi
        
        exit $exit_code
    )
    
    local subshell_exit_code=$?
    
    if [ $subshell_exit_code -eq 0 ]; then
        log_message "SUCCESS" "Mode sous-shell terminé avec succès"
    else
        log_message "ERROR" "Mode sous-shell a échoué"
        exit $subshell_exit_code
    fi
}

# Fonction pour créer un script de démarrage rapide
create_startup_script() {
    local project_dir="$1"
    local script_path="$project_dir/start.sh"
    
    log_message "INFO" "Création du script de démarrage: $script_path"
    
    cat > "$script_path" << EOF
#!/bin/bash
# Script de démarrage rapide pour $PROJECT_NAME

set -e

PROJECT_DIR="\$(cd "\$(dirname "\${BASH_SOURCE[0]}")" && pwd)"
cd "\$PROJECT_DIR"

echo "Démarrage du projet Django: $PROJECT_NAME"
echo "Répertoire: \$PROJECT_DIR"

# Activer l'environnement virtuel
if [ -f "venv/bin/activate" ]; then
    echo "Activation de l'environnement virtuel..."
    source venv/bin/activate
else
    echo "ATTENTION: Environnement virtuel non trouvé"
fi

# Vérifier les migrations
echo "Vérification des migrations..."
python manage.py showmigrations --plan | grep -q "\[ \]" && {
    echo "Migrations en attente détectées, application..."
    python manage.py migrate
}

# Collecter les fichiers statiques en production
if [ "\$1" = "prod" ]; then
    echo "Mode production - Collecte des fichiers statiques..."
    python manage.py collectstatic --noinput
fi

# Démarrer le serveur
echo "Démarrage du serveur Django..."
echo "Accès: http://127.0.0.1:8000"
echo "Arrêt: Ctrl+C"
echo ""

if [ "\$1" = "prod" ]; then
    python manage.py runserver 0.0.0.0:8000
else
    python manage.py runserver
fi
EOF
    
    chmod +x "$script_path"
    log_message "SUCCESS" "Script de démarrage créé: $script_path"
}

# Fonction pour créer un README.md détaillé
create_project_readme() {
    local project_dir="$1"
    local readme_path="$project_dir/README.md"
    
    log_message "INFO" "Création du README.md: $readme_path"
    
    cat > "$readme_path" << EOF
# $PROJECT_NAME

Projet Django créé automatiquement le $(date '+%d/%m/%Y à %H:%M').

## Description

Ce projet Django a été généré avec le script d'automatisation django_automation.sh.

## Structure du projet

\\\`
$PROJECT_NAME/
├── $PROJECT_NAME/          # Configuration principale Django
│   ├── _init_.py
│   ├── settings.py         # Paramètres Django
│   ├── urls.py            # URLs principales
│   └── wsgi.py            # Interface WSGI
├── manage.py              # Utilitaire de gestion Django
├── venv/                  # Environnement virtuel Python
├── requirements.txt       # Dépendances Python
$([ -f "$project_dir/Dockerfile" ] && echo "├── Dockerfile             # Configuration Docker")
$([ -f "$project_dir/docker-compose.yml" ] && echo "├── docker-compose.yml     # Orchestration Docker")
├── start.sh              # Script de démarrage rapide
└── README.md             # Ce fichier
\\\`

## Installation et démarrage

### Méthode 1: Script de démarrage rapide
\\\`bash
./start.sh
\\\`

### Méthode 2: Manuelle
\\\`bash
# Activer l'environnement virtuel
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt

# Effectuer les migrations
python manage.py migrate

# Démarrer le serveur de développement
python manage.py runserver
\\\`

$([ -f "$project_dir/Dockerfile" ] && cat << 'DOCKER_SECTION'
### Méthode 3: Avec Docker
bash
# Construction de l'image
docker build -t $PROJECT_NAME .

# Lancement du conteneur
docker run -p 8000:8000 $PROJECT_NAME

# Ou avec docker-compose
docker-compose up

DOCKER_SECTION
)

## Accès à l'application

Une fois démarré, le projet est accessible sur:
- *Développement*: http://127.0.0.1:8000
- *Docker*: http://localhost:8000

## Commandes utiles

\\\`bash
# Créer une nouvelle application Django
python manage.py startapp nom_app

# Créer des migrations
python manage.py makemigrations

# Appliquer les migrations
python manage.py migrate

# Créer un superutilisateur
python manage.py createsuperuser

# Collecter les fichiers statiques
python manage.py collectstatic

# Lancer les tests
python manage.py test
\\\`

## Interface d'administration

Pour accéder à l'interface d'administration Django:
1. Créez un superutilisateur: \python manage.py createsuperuser\
2. Accédez à: http://127.0.0.1:8000/admin

## Développement

### Ajout d'une nouvelle application
\\\`bash
python manage.py startapp nom_app
\\\`

N'oubliez pas d'ajouter votre application dans \INSTALLED_APPS\ dans \settings.py\.

### Configuration de la base de données

Par défaut, le projet utilise SQLite. Pour changer de base de données, modifiez la section \DATABASES\ dans \settings.py\.

## Déploiement

### Variables d'environnement recommandées
- \DEBUG=False\ en production
- \SECRET_KEY\ unique et sécurisée
- Configuration de base de données de production
- \ALLOWED_HOSTS\ configuré correctement

$([ -d "$project_dir/.git" ] && cat << 'GIT_SECTION'
## Git

Ce projet est configuré avec Git. Commands utiles:

bash
# Voir le statut
git status

# Ajouter des modifications
git add .

# Faire un commit
git commit -m "Description des modifications"

# Pousser vers le dépôt distant
git push origin main

GIT_SECTION
)

## Support

Pour plus d'informations sur Django:
- [Documentation officielle Django](https://docs.djangoproject.com/)
- [Tutorial Django](https://docs.djangoproject.com/en/stable/intro/tutorial01/)

---

Projet généré avec django_automation.sh
EOF

    log_message "SUCCESS" "README.md créé: $readme_path"
}

# Fonction pour afficher les statistiques du projet
show_project_stats() {
    local project_dir="$1"
    
    if [ ! -d "$project_dir" ]; then
        log_message "WARNING" "Impossible d'afficher les statistiques - répertoire non trouvé"
        return 1
    fi
    
    log_message "INFO" "Statistiques du projet $PROJECT_NAME:"
    echo "=================================="
    echo "Répertoire: $(realpath "$project_dir")"
    echo "Taille totale: $(du -sh "$project_dir" 2>/dev/null | cut -f1 || echo "N/A")"
    echo "Nombre de fichiers: $(find "$project_dir" -type f 2>/dev/null | wc -l || echo "N/A")"
    
    if [ -f "$project_dir/requirements.txt" ]; then
        echo "Dépendances Python: $(wc -l < "$project_dir/requirements.txt" 2>/dev/null || echo "N/A") packages"
    fi
    
    if [ -d "$project_dir/.git" ]; then
        echo "Git initialisé: ✓"
        if git -C "$project_dir" remote get-url origin 2>/dev/null; then
            echo "Dépôt distant: $(git -C "$project_dir" remote get-url origin 2>/dev/null)"
        fi
    else
        echo "Git initialisé: ✗"
    fi
    
    if [ -f "$project_dir/Dockerfile" ]; then
        echo "Docker configuré: ✓"
    else
        echo "Docker configuré: ✗"
    fi
    
    echo "=================================="
}

# Fonction principale mise à jour pour inclure les nouvelles fonctionnalités
enhanced_create_project() {
    log_message "INFO" "Début de la création du projet Django enrichi: $PROJECT_NAME"
    
    # Sauvegarder le répertoire initial
    local initial_dir=$(pwd)
    
    # Exécuter la création de base
    if ! create_project; then
        log_message "ERROR" "Échec de la création du projet de base"
        return 1
    fi
    
    # Retourner dans le répertoire du projet pour les améliorations
    if ! cd "$initial_dir/$PROJECT_NAME"; then
        log_message "WARNING" "Impossible d'accéder au répertoire du projet pour les améliorations"
        return 0
    fi
    
    # Créer les fichiers supplémentaires
    create_startup_script "$(pwd)"
    create_project_readme "$(pwd)"
    
    # Afficher les statistiques
    show_project_stats "$(pwd)"
    
    log_message "SUCCESS" "Projet Django enrichi créé avec succès!"
    return 0
}

# Fonction principale
main() {
    # Installer le gestionnaire de signaux
    trap cleanup_on_exit EXIT INT TERM
    
    # Parser les options
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -f|--fork)
                FORK_MODE=true
                shift
                ;;
            -t|--thread)
                THREAD_MODE=true
                shift
                ;;
            -s|--subshell)
                SUBSHELL_MODE=true
                shift
                ;;
            -l|--log-dir)
                if [ -n "$2" ] && [[ "$2" != -* ]]; then
                    LOG_DIR="$2"
                    shift 2
                else
                    log_message "ERROR" "Option -l|--log-dir nécessite un argument."
                    exit 1
                fi
                ;;
            -r|--reset)
                RESET_PROJECT=true
                shift
                ;;
            -n|--name)
                if [ -n "$2" ] && [[ "$2" != -* ]]; then
                    PROJECT_NAME="$2"
                    shift 2
                else
                    log_message "ERROR" "Option -n|--name nécessite un argument."
                    exit 1
                fi
                ;;
            -d|--docker)
                GENERATE_DOCKERFILE=true
                shift
                ;;
            -g|--git)
                INIT_GIT=true
                shift
                ;;
            --gui)
                GUI_MODE=true
                shift
                ;;
            -*)
                log_message "ERROR" "Option invalide: $1"
                show_help
                exit 1
                ;;
            *)
                log_message "ERROR" "Argument invalide: $1"
                show_help
                exit 1
                ;;
        esac
    done

    # Initialiser l'interface GUI si demandée
    if [ "$GUI_MODE" = true ]; then
        if ! init_gui_tool; then
            log_message "WARNING" "Échec de l'initialisation GUI, passage en mode console"
            GUI_MODE=false
        fi
    fi

    # Vérification des modes exclusifs
    mode_count=0
    [ "$FORK_MODE" = true ] && ((mode_count++))
    [ "$THREAD_MODE" = true ] && ((mode_count++))
    [ "$SUBSHELL_MODE" = true ] && ((mode_count++))

    if [ "$mode_count" -gt 1 ]; then
        log_message "ERROR" "Vous ne pouvez pas choisir plusieurs modes d'exécution simultanément (-f, -t, -s)."
        exit 1
    fi

    # Vérifier le nom du projet
    if [ -z "$PROJECT_NAME" ]; then
        log_message "ERROR" "Le nom du projet est obligatoire. Utilisez -n <nom_projet>"
        show_help
        exit 1
    fi

    # Valider le nom du projet
    if [[ ! "$PROJECT_NAME" =~ ^[a-zA-Z][a-zA-Z0-9_]*$ ]]; then
        log_message "ERROR" "Le nom du projet doit commencer par une lettre et ne contenir que des lettres, chiffres et underscores."
        exit 1
    fi

    # Créer le répertoire de logs
    create_log_directory

    # ================= EXÉCUTION SELON LE MODE =================
    
    if [ "$FORK_MODE" = true ]; then
        run_in_fork_mode
    elif [ "$THREAD_MODE" = true ]; then
        run_in_thread_mode
    elif [ "$SUBSHELL_MODE" = true ]; then
        run_in_subshell_mode
    else
        # Mode normal - exécution directe avec fonctionnalités enrichies
        log_message "INFO" "Mode d'exécution normal"
        enhanced_create_project
        exit_code=$?
        
        if [ $exit_code -eq 0 ]; then
            log_message "SUCCESS" "Script terminé avec succès"
        else
            log_message "ERROR" "Script terminé avec des erreurs"
        fi
        
        exit $exit_code
    fi
}

# Fonction de validation des arguments
validate_arguments() {
    # Vérifier que le nom du projet est fourni
    if [ -z "$PROJECT_NAME" ]; then
        return 1
    fi
    
    # Vérifier la validité du nom du projet
    if [[ ! "$PROJECT_NAME" =~ ^[a-zA-Z][a-zA-Z0-9_]*$ ]]; then
        return 1
    fi
    
    # Vérifier que le répertoire de logs est accessible
    if [ ! -w "$(dirname "$LOG_DIR")" ] 2>/dev/null; then
        LOG_DIR="./logs"
    fi
    
    return 0
}

# Fonction d'affichage de la version
show_version() {
    echo "$SCRIPT_NAME version 2.0.0"
    echo "Script d'automatisation pour la création de projets Django"
    echo "Auteur: Assistant IA"
    echo "Dernière mise à jour: $(date '+%Y-%m-%d')"
}

# Point d'entrée principal du script
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    # Vérifier si une option version est demandée
    if [[ "$1" == "--version" ]] || [[ "$1" == "-v" ]]; then
        show_version
        exit 0
    fi
    
    # Lancer la fonction principale avec tous les arguments
    main "$@"
fi