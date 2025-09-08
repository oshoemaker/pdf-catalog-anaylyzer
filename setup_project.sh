#!/bin/bash

# PDF Catalog Analyzer - Complete Project Setup Script
# This script sets up the entire development environment

set -e  # Exit on any error

PROJECT_NAME="PDF Catalog Analyzer"
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PATH="$PROJECT_ROOT/.venv"

echo "🚀 $PROJECT_NAME - Project Setup"
echo "📁 Project Root: $PROJECT_ROOT"
echo "=" * 60

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check Python version
echo "🐍 Checking Python installation..."
if ! command_exists python3; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo "✅ Python version: $PYTHON_VERSION"

# Create virtual environment if it doesn't exist
echo "🔧 Setting up virtual environment..."
if [[ ! -d "$VENV_PATH" ]]; then
    echo "Creating virtual environment at $VENV_PATH"
    python3 -m venv "$VENV_PATH"
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🚀 Activating virtual environment..."
source "$VENV_PATH/bin/activate"

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install requirements if they exist
if [[ -f "$PROJECT_ROOT/requirements.txt" ]]; then
    echo "📋 Installing project dependencies..."
    pip install -r "$PROJECT_ROOT/requirements.txt"
    echo "✅ Dependencies installed"
else
    echo "⚠️  No requirements.txt found. Installing basic packages..."
    pip install jupyter notebook ipython python-dotenv pandas numpy
fi

# Create necessary directories
echo "📁 Creating project directories..."
mkdir -p "$PROJECT_ROOT"/{pdfs,output,extracted_data,temp,docs}
echo "✅ Directories created"

# Create .env.example if it doesn't exist
if [[ ! -f "$PROJECT_ROOT/.env.example" ]]; then
    echo "🔐 Creating .env.example template..."
    cat > "$PROJECT_ROOT/.env.example" << 'EOF'
# PDF Catalog Analyzer - Environment Variables
# Copy this file to .env and fill in your actual API keys

# OpenAI API Key (required for GPT-based analysis)
# Get your key from: https://platform.openai.com/api-keys
OPENAI_API_KEY=your_openai_api_key_here

# Google Gemini API Key (optional, for Google AI features)
# Get your key from: https://makersuite.google.com/app/apikey
GOOGLE_API_KEY=your_google_api_key_here

# Project Configuration
PROJECT_NAME="PDF Catalog Analyzer"
LOG_LEVEL=INFO

# Output Settings
OUTPUT_FORMAT=json
SAVE_EXTRACTED_TEXT=true
SAVE_ANALYSIS_RESULTS=true

# Processing Settings
MAX_PAGES_PER_PDF=100
CHUNK_SIZE=1000
OVERLAP_SIZE=200
EOF
    echo "✅ .env.example created"
fi

# Create .env file if it doesn't exist
if [[ ! -f "$PROJECT_ROOT/.env" ]]; then
    echo "🔐 Creating .env file from template..."
    cp "$PROJECT_ROOT/.env.example" "$PROJECT_ROOT/.env"
    echo "✅ .env file created. Please edit it with your API keys."
fi

# Set up direnv if available
if command_exists direnv; then
    echo "🔄 Setting up direnv auto-activation..."
    cd "$PROJECT_ROOT"
    direnv allow
    echo "✅ direnv configured"
else
    echo "💡 Consider installing direnv for automatic venv activation:"
    echo "   brew install direnv"
    echo "   echo 'eval \"\$(direnv hook zsh)\"' >> ~/.zshrc"
fi

# Final verification
echo "🔍 Verifying setup..."
echo "Python: $(which python)"
echo "Pip: $(which pip)"
echo "Virtual env: $VIRTUAL_ENV"

if [[ "$VIRTUAL_ENV" == "$VENV_PATH" ]]; then
    echo "✅ Setup complete! Virtual environment is active."
else
    echo "⚠️  Setup complete, but virtual environment activation may have failed."
fi

echo ""
echo "🎉 $PROJECT_NAME setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Edit .env file with your API keys"
echo "2. Run: jupyter lab"
echo "3. Open notebooks/03_production_ai_agent.ipynb"
echo ""
echo "🔧 To activate the environment in the future:"
echo "   source activate_venv.sh"
echo ""

