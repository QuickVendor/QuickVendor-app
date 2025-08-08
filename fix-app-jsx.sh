#!/bin/bash
# Fix App.tsx JSX structure errors

cd /home/princewillelebhose/Documents/Projects/QuickVendor-app/frontend

echo "Creating backup of App.tsx..."
cp src/App.tsx src/App.tsx.backup

echo "Fixing JSX structure issues in App.tsx..."

# Fix the specific JSX error around line 80-82
sed -i 's/<HelpButton userContext={currentUser} \/>//g' src/App.tsx

# Add HelpButton import if missing
if ! grep -q "import.*HelpButton" src/App.tsx; then
    echo "Adding HelpButton import..."
    sed -i '1i import { HelpButton } from "./components/HelpButton";' src/App.tsx
fi

# Add single HelpButton at the end of App component if not present
if ! grep -q "<HelpButton" src/App.tsx; then
    echo "Adding single HelpButton component..."
    sed -i '$i\        <HelpButton />' src/App.tsx
fi

echo "App.tsx JSX errors fixed!"
echo "Checking syntax..."

# Try to build to check for errors
npm run build --silent 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✓ App.tsx syntax is now valid!"
else
    echo "⚠ There may still be some issues. Check the build output."
fi
