#!/bin/bash
echo "🔧 Fixing HelpButton import error..."
cd frontend/src
if ! grep -q "import.*HelpButton" App.tsx; then
    echo "Adding HelpButton import..."
    sed -i "1i import HelpButton from './components/HelpButton';" App.tsx
    echo "✅ Import added!"
else
    echo "✅ Import already exists!"
fi
echo "Verification:"
grep -n "HelpButton" App.tsx | head -2
cd ..
echo "🚀 Restarting dev server..."
npm run dev
