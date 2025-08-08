#!/bin/bash
echo "🚀 User Complaint System - Final Integration and Testing"
echo "========================================================"

# Check components
echo "Checking HelpModal..."
if [ -f "frontend/src/components/HelpModal.tsx" ]; then
    echo "✅ HelpModal.tsx exists"
    if grep -q "Sentry.captureUserFeedback" "frontend/src/components/HelpModal.tsx"; then
        echo "✅ Sentry integration confirmed"
    fi
else
    echo "❌ HelpModal.tsx missing"
    exit 1
fi

echo "Checking HelpButton..."
if [ -f "frontend/src/components/HelpButton.tsx" ]; then
    echo "✅ HelpButton.tsx exists"
else
    echo "❌ HelpButton.tsx missing"
    exit 1
fi

echo "Checking App.tsx integration..."
if [ -f "frontend/src/App.tsx" ]; then
    echo "✅ App.tsx found"
    if grep -q "HelpButton" "frontend/src/App.tsx"; then
        echo "✅ HelpButton integrated in App.tsx"
    else
        echo "⚠️ HelpButton not yet integrated in App.tsx"
    fi
else
    echo "❌ App.tsx not found"
    exit 1
fi

echo "Testing build..."
cd frontend
if npm run build; then
    echo "✅ Build successful"
else
    echo "❌ Build failed"
    exit 1
fi

echo "🎉 Integration check complete!"
echo "🚀 Starting development server for testing..."
npm run dev
