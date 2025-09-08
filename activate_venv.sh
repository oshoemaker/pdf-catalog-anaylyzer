#!/bin/bash

# Auto-activate virtual environment for PDF Catalog Analyzer project
# Usage: source activate_venv.sh

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PATH="$PROJECT_ROOT/.venv"

echo "🔍 PDF Catalog Analyzer - Virtual Environment Activator"
echo "📁 Project Root: $PROJECT_ROOT"

# Check if we're already in the virtual environment
if [[ "$VIRTUAL_ENV" != "" ]]; then
    if [[ "$VIRTUAL_ENV" == "$VENV_PATH" ]]; then
        echo "✅ Already using correct virtual environment: $VIRTUAL_ENV"
        return 0 2>/dev/null || exit 0
    else
        echo "⚠️  Currently in different virtual environment: $VIRTUAL_ENV"
        echo "🔄 Switching to project venv..."
        deactivate
    fi
fi

# Check if venv exists
if [[ ! -d "$VENV_PATH" ]]; then
    echo "❌ Virtual environment not found at: $VENV_PATH"
    echo "🔧 Creating virtual environment..."
    python3 -m venv "$VENV_PATH"
    echo "✅ Virtual environment created"
fi

# Activate the virtual environment
echo "🚀 Activating virtual environment..."
source "$VENV_PATH/bin/activate"

# Verify activation
if [[ "$VIRTUAL_ENV" == "$VENV_PATH" ]]; then
    echo "✅ Virtual environment activated successfully!"
    echo "🐍 Python: $(which python)"
    echo "📦 Pip: $(which pip)"
    
    # Check if requirements are installed
    if [[ -f "$PROJECT_ROOT/requirements.txt" ]]; then
        echo "📋 Checking dependencies..."
        if ! pip check > /dev/null 2>&1; then
            echo "⚠️  Some dependencies may be missing or incompatible"
            echo "💡 Consider running: pip install -r requirements.txt"
        else
            echo "✅ All dependencies satisfied"
        fi
    fi
    
    # Change to project directory
    cd "$PROJECT_ROOT"
    echo "📁 Changed to project directory: $(pwd)"
    
else
    echo "❌ Failed to activate virtual environment"
    return 1 2>/dev/null || exit 1
fi






