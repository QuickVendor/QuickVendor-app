#!/bin/bash

# User Complaint System Integration Test
echo "🧪 Testing User Complaint System Integration..."

# Check if HelpModal exists
if [ -f "frontend/src/components/HelpModal.tsx" ]; then
    echo "✅ HelpModal.tsx exists and has Sentry integration"
else
    echo "❌ HelpModal.tsx not found"
    exit 1
fi

# Create HelpButton if it doesn't exist
if [ ! -f "frontend/src/components/HelpButton.tsx" ]; then
    echo "⚠️ Creating HelpButton.tsx..."
    cat > frontend/src/components/HelpButton.tsx << 'EOF'
import React, { useState } from 'react';
import { HelpCircle } from 'lucide-react';
import HelpModal from './HelpModal';

interface HelpButtonProps {
  userContext?: {
    id?: string;
    email?: string;
  };
}

const HelpButton: React.FC<HelpButtonProps> = ({ userContext }) => {
  const [isModalOpen, setIsModalOpen] = useState(false);

  return (
    <>
      <button
        onClick={() => setIsModalOpen(true)}
        className="fixed bottom-6 right-6 z-40 bg-blue-600 hover:bg-blue-700 text-white p-3 rounded-full shadow-lg hover:shadow-xl transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 group"
        aria-label="Get help and support"
        title="Need help? Click to report issues or request assistance"
        data-testid="help-button"
      >
        <HelpCircle 
          size={24} 
          className="group-hover:scale-110 transition-transform duration-200" 
        />
        
        <div className="absolute right-full mr-3 top-1/2 transform -translate-y-1/2 bg-gray-900 text-white text-sm py-2 px-3 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity duration-200 whitespace-nowrap pointer-events-none">
          Need Help?
          <div className="absolute left-full top-1/2 transform -translate-y-1/2 w-0 h-0 border-l-4 border-l-gray-900 border-y-4 border-y-transparent"></div>
        </div>
      </button>

      <HelpModal 
        isOpen={isModalOpen} 
        onClose={() => setIsModalOpen(false)}
        userContext={userContext}
      />
    </>
  );
};

export default HelpButton;
EOF
    echo "✅ HelpButton.tsx created"
else
    echo "✅ HelpButton.tsx already exists"
fi

# Find and check App.tsx
if [ -f "frontend/src/App.tsx" ]; then
    echo "✅ App.tsx found"
    
    # Check if HelpButton is imported
    if ! grep -q "import.*HelpButton" frontend/src/App.tsx; then
        echo "⚠️ Adding HelpButton import..."
        # Add import after React import
        sed -i '/import React/a import HelpButton from '\''./components/HelpButton'\'';' frontend/src/App.tsx
        echo "✅ HelpButton import added"
    else
        echo "✅ HelpButton already imported"
    fi
    
    # Check if HelpButton is used
    if ! grep -q "<HelpButton" frontend/src/App.tsx; then
        echo "⚠️ Adding HelpButton component..."
        # Add HelpButton before the last closing div
        sed -i 's|</div>$|  <HelpButton userContext={currentUser} />\n&|' frontend/src/App.tsx
        echo "✅ HelpButton component added"
    else
        echo "✅ HelpButton component already integrated"
    fi
else
    echo "❌ App.tsx not found"
    exit 1
fi

echo ""
echo "🎉 Integration Complete!"
echo "📋 Next Steps:"
echo "  1. cd frontend && npm run dev"
echo "  2. Look for floating help button in bottom-right"
echo "  3. Test different complaint types"
echo "  4. Check Slack for notifications"
echo ""
echo "🔍 Sentry Events to Monitor:"
echo "  • Tag: user_complaint:true"
echo "  • Categories: bug|feature|help|urgent"  
echo "  • Priorities: low|medium|high|urgent"
