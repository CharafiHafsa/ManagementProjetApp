# ManagementProjetApp

## Setting up the project

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd <repository-folder>

2. **Create and activate a virtual environment**
    python -m venv env
    env\Scripts\activate

3. **Install dependencies**
    pip install -r requirements.txt

4. **Configure the database in myproject/settings.py and run migrations**

    python manage.py makemigrations
    python manage.py migrate


## Working with Git

**To check the status of your repository**
    >> git status

**To add and commit changes**
    >> git add .
    >> git commit -m "Your commit message"

**To push changes**
    >> git push

**To pull the latest changes**
    >> git pull



## How to work : 
## 🌟 How to Set Up and Contribute to the Project

### **1. 📂 Clone the Repository**

1. 🖥️ Clone the repository to your local machine:
   ```bash
   git clone <repository-url>
   cd <repository-folder>
   ```

2. 🛠️ Create and activate a virtual environment:
   ```bash
   python -m venv env
   source env/bin/activate  # On Windows: env\Scripts\activate
   ```

3. 📥 Install the project dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

### **2. 🚀 Start Working on the Project**

#### **A. 🌿 Create a New Branch**
To avoid conflicts, always create a new branch for your work:

1. ✅ Check which branch you're on:
   ```bash
   git branch
   ```
   If you're on `main`, create a new branch:
   ```bash
   git checkout -b <branch-name>
   ```
   Example:
   ```bash
   git checkout -b feature-add-login
   ```

2. 🔍 Verify you're on your new branch:
   ```bash
   git branch
   ```

---

#### **B. 🛠️ Make Changes**
1. 💻 Work on the codebase, add features, or fix issues.
2. 💾 Save your changes.

---

#### **C. 💾 Save and Commit Your Work**
1. 🔎 Check the status of your changes:
   ```bash
   git status
   ```
2. ➕ Stage the changes:
   ```bash
   git add .
   ```
3. 📝 Commit your changes with a meaningful message:
   ```bash
   git commit -m "Describe what you did"
   ```
   Example:
   ```bash
   git commit -m "Add login functionality with user authentication"
   ```

---

#### **D. 📤 Push Your Branch**
Push your branch to the remote repository:
```bash
git push origin <branch-name>
```
Example:
```bash
git push origin feature-add-login
```

---

### **3. 📩 Submit a Pull Request (PR)**
1. 🌐 Go to the repository on GitHub.
2. 🖱️ You’ll see an option to create a pull request for your branch. Click it.
3. ✏️ Provide a description of the changes you made and submit the PR.

---

### **4. 🔄 Keep Your Branch Up-to-Date**
To avoid conflicts, always pull the latest changes from the main branch into your branch:

1. 🔄 Switch to the `main` branch:
   ```bash
   git checkout main
   ```
2. 📥 Pull the latest changes:
   ```bash
   git pull origin main
   ```
3. 🔀 Switch back to your branch:
   ```bash
   git checkout <branch-name>
   ```
4. 🔗 Merge the main branch into your branch:
   ```bash
   git merge main
   ```

---
## test a teammate bracnh
##1. Make Sure You're in the Right Repository

##2. Clone the repository if you haven't already:
>> git clone <repository_url>
Replace <repository_url> with the actual URL of the GitHub repository.

##3. Navigate to the repository's directory:
>> cd <repository_folder>

##4.  Fetch the Latest Updates
To ensure you have the latest branches and commits, run:
>> git fetch

##5. List All Branches
To see all branches (both local and remote), run:
>> git branch -a
Look for the new branch in the list (e.g., remotes/origin/new-branch-name).

##6. Check Out the New Branch
To switch to the new branch, run:
>> git checkout <branch_name>
Replace <branch_name> with the name of the new branch your friend created.
If the branch exists remotely but not locally, git checkout will automatically track it and bring the branch to your local system.

##7. Pull the Latest Code
To ensure the branch has the most recent changes, run:
>> git pull

##8. Test the Code
After switching to the branch, you can test the code locally on your machine as needed.

### **📝 Best Practices**

- 🌿 Create a new branch for each feature or fix (e.g., `feature-add-login` or `fix-database-connection`).
- 🔖 Commit often with clear messages.
- 🔄 Always pull the latest changes before starting new work.
- 👀 Review pull requests thoroughly before merging.







