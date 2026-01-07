# Spam Email Classification Web Application

A machine learning-powered web application built with Flask that classifies emails as spam or not spam (ham) using Natural Language Processing (NLP) and the Multinomial Naive Bayes algorithm.

## 📋 Table of Contents

- [Features](#features)
- [Technology Stack](#technology-stack)
- [Prerequisites](#prerequisites)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Database Setup](#database-setup)
- [Model Training](#model-training)
- [Running the Application](#running-the-application)
- [Usage](#usage)
- [Model Details](#model-details)
- [API Endpoints](#api-endpoints)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)

## ✨ Features

- **User Authentication**: Sign up and sign in functionality
- **Email Classification**: Real-time spam detection for email messages
- **Machine Learning Model**: Pre-trained Multinomial Naive Bayes classifier
- **Web Interface**: Modern, responsive UI built with Bootstrap
- **Session Management**: Secure user sessions with Flask sessions

## 🛠 Technology Stack

### Backend
- **Python**: 3.11.9
- **Flask**: Web framework for building the application
- **scikit-learn**: Machine learning library for model training and prediction
- **pandas**: Data manipulation and analysis
- **MySQL**: Database for user management

### Frontend
- **HTML/CSS**: Frontend templates and styling
- **Bootstrap**: Responsive UI framework
- **JavaScript**: Client-side interactivity

### Machine Learning
- **Algorithm**: Multinomial Naive Bayes
- **Vectorization**: TF-IDF (Term Frequency-Inverse Document Frequency)
- **Text Processing**: Custom preprocessing pipeline

## 📦 Prerequisites

Before you begin, ensure you have the following installed:

1. **Python 3.11.9** (or compatible version)
   - Check your Python version: `python3 --version`
   - If you need to install Python 3.11.9, visit [python.org](https://www.python.org/downloads/)

2. **MySQL Server**
   - Install MySQL Server on your system
   - Ubuntu/Debian: `sudo apt-get install mysql-server`
   - macOS: `brew install mysql`
   - Windows: Download from [MySQL Downloads](https://dev.mysql.com/downloads/mysql/)

3. **pip** (Python package manager)
   - Usually comes with Python installation

4. **Git** (for cloning the repository)
   - Install from [git-scm.com](https://git-scm.com/downloads)

## 📁 Project Structure

```
Spam-Email-Classification/
├── app.py                 # Main Flask application
├── train.py              # Model training script
├── spam.csv              # Training dataset
├── model.pkl             # Trained ML model (generated after training)
├── vectorizer.pkl        # TF-IDF vectorizer (generated after training)
├── .python-version       # Python version specification
├── templates/            # HTML templates
│   ├── home.html
│   ├── index.html
│   ├── about.html
│   ├── signin.html
│   ├── signup.html
│   └── result.html
├── static/               # Static files (CSS, JS, images)
│   ├── bootstrap.css
│   ├── home.css
│   ├── index.css
│   ├── signin.css
│   ├── signup.css
│   ├── index.js
│   ├── signin.js
│   ├── signup.js
│   └── images/
└── venv/                 # Virtual environment (not included in repo)
```

## 🚀 Installation

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd Spam-Email-Classification
```

If you don't have a Git repository, you can download the project files directly.

### Step 2: Create Virtual Environment

It's recommended to use a virtual environment to isolate project dependencies:

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### Step 3: Install Dependencies

Install all required Python packages:

```bash
pip install flask pandas scikit-learn mysql-connector-python
```

Or install from a requirements file (if available):

```bash
pip install -r requirements.txt
```

**Required Packages:**
- `flask==3.1.2` - Web framework
- `pandas==2.3.3` - Data manipulation
- `scikit-learn==1.8.0` - Machine learning library
- `mysql-connector-python==9.5.0` - MySQL database connector

### Step 4: Verify Installation

Verify that all packages are installed correctly:

```bash
python3 -c "import flask, pandas, sklearn, mysql.connector; print('All packages installed successfully!')"
```

## 🗄 Database Setup

### Step 1: Start MySQL Service

```bash
# Linux
sudo systemctl start mysql
sudo systemctl enable mysql

# macOS
brew services start mysql

# Windows
# Start MySQL from Services or MySQL Workbench
```

### Step 2: Create Database and User

Log in to MySQL as root:

```bash
mysql -u root -p
```

Then run the following SQL commands:

```sql
-- Create database
CREATE DATABASE smc;

-- Create user
CREATE USER 'smc_user'@'localhost' IDENTIFIED BY 'Smc@1234';

-- Grant privileges
GRANT ALL PRIVILEGES ON smc.* TO 'smc_user'@'localhost';
FLUSH PRIVILEGES;

-- Use the database
USE smc;

-- Create users table
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20),
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Exit MySQL
EXIT;
```

**Note**: You can modify the database credentials in `app.py` if you prefer different settings.

## 🤖 Model Training

Before running the application, you need to train the machine learning model:

### Step 1: Ensure Dataset is Available

Make sure `spam.csv` is present in the project root directory. The dataset should contain:
- Column `v1`: Email labels ('ham' or 'spam')
- Column `v2`: Email text content

### Step 2: Run Training Script

```bash
python3 train.py
```

This will:
1. Load and preprocess the dataset
2. Create TF-IDF vectorizer
3. Train the Multinomial Naive Bayes model
4. Evaluate model accuracy
5. Save `model.pkl` and `vectorizer.pkl` files

**Expected Output:**
```
🚀 Training started
📂 Loading dataset...
🧠 Processing text...
🔢 Vectorizing...
🤖 Training model...
🎯 Accuracy: 0.XXXX
💾 Saving model files...
✅ Training complete
📦 Files saved: model.pkl, vectorizer.pkl
```

**Note**: The training process may take a few minutes depending on your system. The model files (`model.pkl` and `vectorizer.pkl`) must be present in the project root for the application to work.

## ▶️ Running the Application

### Step 1: Activate Virtual Environment

```bash
# Linux/macOS
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### Step 2: Start Flask Application

```bash
python3 app.py
```

Or:

```bash
flask run
```

### Step 3: Access the Application

Open your web browser and navigate to:

```
http://localhost:5000
```

or

```
http://127.0.0.1:5000
```

The application should now be running!

## 📖 Usage

### 1. Home Page
- Visit `http://localhost:5000/` to see the home page
- Navigate to "About" to learn more about the application

### 2. User Registration
- Click on "Sign Up" or navigate to `/signup`
- Fill in the registration form:
  - Full Name
  - Username
  - Email
  - Phone Number
  - Password
  - Confirm Password
- Submit the form to create an account

### 3. User Login
- Click on "Sign In" or navigate to `/signin`
- Enter your email and password
- Click "Login" to access the classification interface

### 4. Email Classification
- After logging in, you'll be redirected to the classification page (`/index`)
- Enter an email message in the text area
- Click "Check" to classify the email
- View the result: "Spam" or "Not Spam"

### 5. Logout
- Click "Logout" to end your session

## 🔬 Model Details

### Algorithm
- **Multinomial Naive Bayes**: A probabilistic classifier based on Bayes' theorem, well-suited for text classification tasks.

### Text Preprocessing
The model uses the following preprocessing steps:
1. **Lowercasing**: Convert all text to lowercase
2. **URL Replacement**: Replace URLs with "url"
3. **Number Replacement**: Replace numbers with "number"
4. **Special Character Removal**: Remove all special characters except alphanumeric and spaces

### Vectorization
- **TF-IDF Vectorizer** with the following parameters:
  - `max_features=5000`: Maximum number of features
  - `ngram_range=(1, 2)`: Unigrams and bigrams
  - `stop_words='english'`: Remove English stop words
  - `min_df=2`: Minimum document frequency

### Model Parameters
- **Alpha (Smoothing)**: 0.1
- **Test Split**: 20% of the dataset
- **Random State**: 42 (for reproducibility)

### Performance
The model accuracy is displayed during training. Typical accuracy ranges from 95-98% depending on the dataset.

## 🌐 API Endpoints

| Method | Endpoint | Description | Authentication Required |
|--------|----------|-------------|------------------------|
| GET | `/` | Home page | No |
| GET | `/about` | About page | No |
| GET | `/index` | Classification interface | Yes |
| POST | `/predict` | Classify email message | Yes |
| GET | `/signin` | Sign in page | No |
| GET | `/signup` | Sign up page | No |
| POST | `/register` | Register new user | No |
| POST | `/login` | User login | No |
| GET | `/logout` | User logout | Yes |

## ⚙️ Configuration

### Database Configuration

Edit the `get_db()` function in `app.py` to modify database settings:

```python
def get_db():
    return mysql.connector.connect(
        host="localhost",          # Database host
        user="smc_user",           # Database user
        password="Smc@1234",       # Database password
        database="smc",             # Database name
        auth_plugin="mysql_native_password"
    )
```

### Flask Secret Key

Change the secret key in `app.py` for production:

```python
app.secret_key = "change_this_secret_key"  # Change this!
```

Generate a secure secret key:

```python
import secrets
print(secrets.token_hex(32))
```

### Debug Mode

For production, disable debug mode in `app.py`:

```python
if __name__ == "__main__":
    app.run(debug=False)  # Set to False in production
```

## 🔧 Troubleshooting

### Issue: ModuleNotFoundError

**Solution**: Ensure all dependencies are installed:
```bash
pip install flask pandas scikit-learn mysql-connector-python
```

### Issue: Model files not found

**Error**: `FileNotFoundError: model.pkl` or `vectorizer.pkl`

**Solution**: Run the training script first:
```bash
python3 train.py
```

### Issue: Database connection error

**Error**: `mysql.connector.errors.InterfaceError` or `Access denied`

**Solutions**:
1. Verify MySQL service is running
2. Check database credentials in `app.py`
3. Ensure database and user are created (see Database Setup)
4. Verify user has proper privileges

### Issue: Port already in use

**Error**: `Address already in use`

**Solution**: Use a different port:
```python
app.run(port=5001, debug=True)
```

### Issue: Import errors

**Solution**: Ensure you're using the correct Python version (3.11.9) and virtual environment is activated.

### Issue: Training script fails

**Solutions**:
1. Verify `spam.csv` exists in the project root
2. Check CSV file encoding (should be 'latin-1')
3. Ensure sufficient disk space for model files

## 📝 Notes

- The model files (`model.pkl` and `vectorizer.pkl`) are generated after training and should be included in version control or regenerated when deploying.
- For production deployment, consider:
  - Using environment variables for sensitive data (database credentials, secret keys)
  - Implementing password hashing (currently passwords are stored in plain text)
  - Using a production WSGI server (e.g., Gunicorn)
  - Setting up proper error logging
  - Implementing HTTPS/SSL

## 🙏 Acknowledgments

- Dataset: Spam SMS Collection Dataset
- Flask: Web framework
- scikit-learn: Machine learning library

---
