#!/bin/bash

# Fix HelpButton import error in App.tsx
echo "🔧 Fixing HelpButton import error..."

cd /home/princewillelebhose/Documents/Projects/QuickVendor-app/frontend/src

# Check if HelpButton import already exists
if ! grep -q "import.*HelpButton" App.tsx; then
    echo "Adding HelpButton import..."
    
    # Add the import after existing imports
    if grep -q "import React" App.tsx; then
        # Add after React import
        sed -i "/import React/a import HelpButton from './components/HelpButton';" App.tsx
    else
        # Add at the beginning of the file
        sed -i "1i import HelpButton from './components/HelpButton';" App.tsx
    fi
    
    echo "✅ HelpButton import added successfully!"
else
    echo "✅ HelpButton import already exists!"
fi

# Verify the fix
echo "Checking for HelpButton import..."
grep -n "HelpButton" App.tsx | head -3

echo "🚀 Restarting development server..."
cd ..
npm run dev
