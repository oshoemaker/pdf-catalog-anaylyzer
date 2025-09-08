# Complete Setup Guide for PDF Catalog Analyzer

This guide will help you set up the PDF Catalog Analyzer project from scratch, even if you have no prior experience with Python, Jupyter, Docker, or virtual environments.

## 🚀 Quick Start (Recommended for This Project)

If you just want to get started quickly with this specific project:

### Step 1: Clone and Navigate to the Project
```bash
# If you haven't cloned the repository yet
git clone <repository-url>
cd pdf-catalog-anaylyzer
```

### Step 2: Automated Setup
```bash
# Make the setup script executable and run it
chmod +x setup_project.sh
./setup_project.sh
```

### Step 3: Start Jupyter
```bash
# Activate the environment (if not already active)
source activate_venv.sh

# Start Jupyter Lab
jupyter lab
```

That's it! The automated setup will handle everything for you. Jump to the [Using the Project](#using-the-project) section below.

---

## 📚 Detailed Setup Options

Choose the method that best fits your experience level and preferences:

### Option 1: Python Virtual Environment (Recommended)
### Option 2: macOS with Homebrew
### Option 3: Docker (Cross-Platform)

---

## Option 1: Python Virtual Environment Setup (Recommended)

This is the recommended approach for this project as it isolates dependencies and matches the project structure.

### Prerequisites
- Python 3.8 or higher installed on your system
- Basic command line familiarity

### Step-by-Step Instructions

#### 1. Check Python Installation
```bash
python3 --version
```
If this doesn't work, you need to install Python first:
- **macOS**: Install via Homebrew: `brew install python3`
- **Windows**: Download from [python.org](https://python.org)
- **Linux**: Use your package manager: `sudo apt install python3 python3-pip python3-venv`

#### 2. Navigate to Project Directory
```bash
cd /path/to/pdf-catalog-anaylyzer
```

#### 3. Use the Project's Automated Setup
```bash
# Option A: Full automated setup
chmod +x setup_project.sh
./setup_project.sh

# Option B: Manual virtual environment setup
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

#### 4. Activate Environment (for future sessions)
```bash
# Use the project's activation script
source activate_venv.sh

# Or manually activate
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

#### 5. Start Jupyter
```bash
jupyter lab
```

### Environment Variables Setup
1. Create your environment file:
   ```bash
   # The setup script will create .env.example for you, then copy it
   cp .env.example .env
   ```
2. Edit `.env` with your API keys:
   ```bash
   # Add your API keys here
   OPENAI_API_KEY=your_openai_key_here
   GOOGLE_API_KEY=your_google_key_here
   ```

---

## Option 2: macOS with Homebrew

### Prerequisites
- macOS with Homebrew installed
- No prior Python/Jupyter experience needed

### Complete Installation Steps

#### 1. Install Homebrew (if not installed)
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

#### 2. Install Python and Package Manager
```bash
# Install Python 3
brew install python3

# Install pipx for Python application management
brew install pipx
```

#### 3. Install Jupyter with Dependencies
```bash
# Install Jupyter with all scientific computing packages
pipx install --include-deps jupyter

# Add pipx to your PATH
pipx ensurepath
```

#### 4. Restart Terminal
```bash
# Restart your terminal or run:
source ~/.bashrc  # or ~/.zshrc depending on your shell
```

#### 5. Navigate to Project and Install Dependencies
```bash
cd /path/to/pdf-catalog-anaylyzer

# Install project-specific dependencies
pip3 install -r requirements.txt
```

#### 6. Start Jupyter
```bash
jupyter lab
```

---

## Option 3: Docker Setup (Cross-Platform)

Perfect if you want a completely isolated environment or have issues with Python installation.

### Prerequisites
- Docker Desktop installed and running
- No Python knowledge required

### Step-by-Step Docker Setup

#### 1. Install Docker Desktop
- Download from [docker.com](https://www.docker.com/products/docker-desktop/)
- Install and start Docker Desktop
- Verify installation: `docker --version`

#### 2. Navigate to Project Directory
```bash
cd /path/to/pdf-catalog-anaylyzer
```

#### 3. Run Jupyter in Docker
```bash
# Pull and run Jupyter with scientific packages
docker run -p 8888:8888 \
  -v "$(pwd)":/home/jovyan/work \
  --name jupyter-pdf-analyzer \
  jupyter/scipy-notebook:latest
```

#### 4. Access Jupyter Lab
1. Watch the terminal output for a line like:
   ```
   http://127.0.0.1:8888/lab?token=abc123...
   ```
2. Copy this URL and open it in your browser
3. Your project files will be in the `work` directory

#### 5. Managing the Docker Container
```bash
# Stop the container
docker stop jupyter-pdf-analyzer

# Start existing container
docker start jupyter-pdf-analyzer

# View logs (to get the access token again)
docker logs jupyter-pdf-analyzer

# Remove container (when done)
docker rm jupyter-pdf-analyzer
```

---

## Using the Project

Once Jupyter is running, you can access the project notebooks:

### Available Notebooks
1. **`01_pdf_catalog_analyzer.ipynb`** - Basic PDF analysis
2. **`02_simple_pdf_analyzer.ipynb`** - Simplified analysis workflow  
3. **`03_production_ai_agent.ipynb`** - Advanced AI-powered analysis

### Getting Started
1. Open Jupyter Lab in your browser
2. Navigate to the `notebooks/` folder
3. Start with `01_pdf_catalog_analyzer.ipynb` for a basic introduction
4. Place your PDF files in the `pdfs/` directory
5. Run the cells in order by pressing `Shift + Enter`

### Project Structure
```
pdf-catalog-anaylyzer/
├── notebooks/          # Jupyter notebooks
├── pdfs/              # Place your PDF files here
├── extracted_data/    # Analysis results (tracked in git)
├── output/            # CSV exports and reports
├── docs/              # Documentation
├── requirements.txt   # Python dependencies
└── .env              # Your API keys (copy from .env.example)
```

---

## Troubleshooting

### Common Issues and Solutions

#### "Command not found: jupyter"
- **Virtual Environment**: Make sure you activated it: `source activate_venv.sh`
- **macOS/Homebrew**: Run `pipx ensurepath` and restart terminal
- **Docker**: Use the docker command instead of local jupyter

#### "Module not found" errors
```bash
# Virtual Environment
source activate_venv.sh
pip install -r requirements.txt

# System-wide installation
pip3 install -r requirements.txt
```

#### Port 8888 already in use
```bash
# Find and kill the process
lsof -ti:8888 | xargs kill -9

# Or use a different port
jupyter lab --port 8889
```

#### Docker permission issues
```bash
# On Linux, you might need to add your user to docker group
sudo usermod -aG docker $USER
# Then logout and login again
```

#### Can't access files in Docker
- Make sure you're running docker from the project directory
- Files should appear in the `work` folder within Jupyter
- Use absolute paths in the volume mount if needed

### Getting Help

If you encounter issues:
1. Check the error messages carefully
2. Ensure all prerequisites are installed
3. Try the automated setup script: `./setup_project.sh`
4. For Docker issues, restart Docker Desktop
5. For Python issues, try creating a fresh virtual environment

---

## Verification Steps

Test that everything works:

### 1. Create a Test Notebook
1. In Jupyter, create a new Python 3 notebook
2. Run these test commands:

```python
# Test 1: Basic Python
print("Hello, PDF Analyzer!")

# Test 2: Import core libraries
import pandas as pd
import numpy as np
print("✅ Core libraries imported successfully")

# Test 3: Import PDF processing libraries
import PyMuPDF as fitz
import pdfplumber
print("✅ PDF libraries imported successfully")

# Test 4: Check project structure
import os
print("Current directory:", os.getcwd())
print("Available files:", os.listdir('.'))
```

### 2. Verify Environment
```python
# Check Python version and packages
import sys
print("Python version:", sys.version)

# List installed packages
import pkg_resources
packages = [d.project_name for d in pkg_resources.working_set]
print(f"✅ {len(packages)} packages installed")
```

If all commands run without errors, your setup is complete! 🎉

---

## Next Steps

1. **Set up API keys** in your `.env` file
2. **Add PDF files** to the `pdfs/` directory  
3. **Start with** `notebooks/01_pdf_catalog_analyzer.ipynb`
4. **Explore** the other notebooks for advanced features

Happy analyzing! 📊