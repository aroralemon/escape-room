#!/bin/bash
# Move to the script's directory (handles spaces in paths)
cd "$(dirname "$0")" || exit 1

echo "========================================="
echo "   Starting Escape Room Game..."
echo "========================================="

# Candidate Python interpreters to check
CANDIDATES=(
    "/Library/Frameworks/Python.framework/Versions/3.13/bin/python3"
    "/Library/Frameworks/Python.framework/Versions/3.12/bin/python3"
    "/Library/Frameworks/Python.framework/Versions/3.11/bin/python3"
    "/Library/Frameworks/Python.framework/Versions/3.10/bin/python3"
    "/usr/local/bin/python3"
    "/opt/homebrew/bin/python3"
    "/opt/anaconda3/bin/python3"
    "$(which python3 2>/dev/null)"
    "/usr/bin/python3"
)

PYTHON_CMD=""

# 1. First pass: look for an interpreter that has both required packages installed
for candidate in "${CANDIDATES[@]}"; do
    if [ -n "$candidate" ] && [ -x "$candidate" ]; then
        if "$candidate" -c "import mysql.connector, PIL" >/dev/null 2>&1; then
            PYTHON_CMD="$candidate"
            break
        fi
    fi
done

# 2. Second pass: fallback to any working python3 if none had packages preinstalled
if [ -z "$PYTHON_CMD" ]; then
    for candidate in "${CANDIDATES[@]}"; do
        if [ -n "$candidate" ] && [ -x "$candidate" ]; then
            PYTHON_CMD="$candidate"
            echo "⚠️  Found Python at $PYTHON_CMD but required packages may be missing."
            echo "Attempting to install dependencies from requirements.txt..."
            "$PYTHON_CMD" -m pip install -r requirements.txt
            break
        fi
    done
fi

if [ -z "$PYTHON_CMD" ]; then
    echo "❌ Error: A valid python3 interpreter could not be found."
    echo "Please install Python 3.10+ and ensure it is installed properly."
    read -p "Press Enter to exit..."
    exit 1
fi

echo "Using Python: $($PYTHON_CMD --version) at $PYTHON_CMD"

# Run main.py
$PYTHON_CMD main.py

EXIT_CODE=$?
if [ $EXIT_CODE -ne 0 ]; then
    echo ""
    echo "❌ Application exited with error code: $EXIT_CODE"
    echo "Press Enter to close this window..."
    read -r
fi
