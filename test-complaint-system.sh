#!/bin/bash

# User Complaint System Integration Test Script
echo "🧪 Testing User Complaint System Integration..."

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "\n${BLUE}Test 1: Checking HelpModal Component${NC}"
if [ -f "frontend/src/components/HelpModal.tsx" ]; then
    echo -e "${GREEN}✅ HelpModal.tsx exists${NC}"
    if grep -q "Sentry.captureUserFeedback" frontend/src/components/HelpModal.tsx; then
        echo -e "${GREEN}✅ Sentry integration found${NC}"
    fi
    if grep -q "complaint_category" frontend/src/components/HelpModal.tsx; then
        echo -e "${GREEN}✅ Complaint categories tagged${NC}"
    fi
else
    echo -e "${RED}❌ HelpModal.tsx not found${NC}"
fi

echo -e "\n${BLUE}Test 2: Checking HelpButton Component${NC}"
if [ -f "frontend/src/components/HelpButton.tsx" ]; then
    echo -e "${GREEN}✅ HelpButton.tsx exists${NC}"
else
    echo -e "${YELLOW}⚠️ Creating HelpButton.tsx...${NC}"
    cat > frontend/src/components/HelpButton.tsx << 'HELPBUTTON'
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
HELPBUTTON
    echo -e "${GREEN}✅ HelpButton.tsx created${NC}"
fi

echo -e "\n${BLUE}Test 3: Checking App.tsx Integration${NC}"
if [ -f "frontend/src/App.tsx" ]; then
    echo -e "${GREEN}✅ App.tsx exists${NC}"
    if grep -q "HelpButton" frontend/src/App.tsx; then
        echo -e "${GREEN}✅ HelpButton already integrated${NC}"
    else
        echo -e "${YELLOW}⚠️ HelpButton needs integration${NC}"
        echo -e "${BLUE}Add this to your App.tsx:${NC}"
        echo -e "import HelpButton from './components/HelpButton';"
        echo -e "// Add <HelpButton userContext={currentUser} /> before closing </div>"
    fi
fi

echo -e "\n${BLUE}Test 4: Starting Development Server${NC}"
cd frontend
if [ -f "package.json" ]; then
    echo -e "${GREEN}✅ Starting dev server...${NC}"
    echo -e "${YELLOW}The server will start on http://localhost:5173${NC}"
    echo -e "${YELLOW}Look for the floating help button in bottom-right corner${NC}"
    npm run dev
else
    echo -e "${RED}❌ package.json not found${NC}"
fi
