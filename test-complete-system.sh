#!/bin/bash

# User Complaint System - Final Integration and Testing
echo "🎯 Final Integration and Testing of User Complaint System"
echo "========================================================"

PROJECT_DIR="/home/princewillelebhose/Documents/Projects/QuickVendor-app"
cd "$PROJECT_DIR"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
PURPLE='\033[0;35m'
NC='\033[0m'

echo -e "\n${BLUE}🔍 System Verification${NC}"

# Check HelpModal
if [ -f "frontend/src/components/HelpModal.tsx" ]; then
    echo -e "${GREEN}✅ HelpModal.tsx exists${NC}"
    if grep -q "Sentry.captureUserFeedback\|complaint_category" frontend/src/components/HelpModal.tsx; then
        echo -e "${GREEN}✅ Sentry integration confirmed in HelpModal${NC}"
    fi
else
    echo -e "${RED}❌ HelpModal.tsx missing${NC}"
    exit 1
fi

# Check HelpButton
if [ -f "frontend/src/components/HelpButton.tsx" ]; then
    echo -e "${GREEN}✅ HelpButton.tsx exists${NC}"
else
    echo -e "${RED}❌ HelpButton.tsx missing${NC}"
    exit 1
fi

echo -e "\n${BLUE}🚀 Starting Development Server${NC}"
cd frontend

# Kill any existing servers
pkill -f "npm.*dev\|vite\|node.*vite" 2>/dev/null

# Start development server
echo -e "${YELLOW}Starting development server...${NC}"
npm run dev &
SERVER_PID=$!

# Wait for server to start
sleep 8

# Check if server is running
if ps -p $SERVER_PID > /dev/null; then
    echo -e "${GREEN}✅ Development server started successfully${NC}"
    
    # Try to detect the server URL
    SERVER_URL="http://localhost:5173"
    echo -e "${BLUE}📍 Server running at: ${SERVER_URL}${NC}"
    
    echo -e "\n${YELLOW}🧪 MANUAL TESTING REQUIRED${NC}"
    echo -e "=============================================="
    echo -e "1. Open browser and visit: ${BLUE}${SERVER_URL}${NC}"
    echo -e "2. Look for floating help button in bottom-right corner"
    echo -e "3. Click the help button to open the modal"
    echo -e "4. Test each complaint category:"
    echo -e "   ${RED}• 🐛 Bug Report${NC} - Should alert development team"
    echo -e "   ${YELLOW}• 🚨 Urgent Issue${NC} - Should trigger immediate notification"
    echo -e "   ${BLUE}• 💡 Feature Request${NC} - Should notify product team"
    echo -e "   ${GREEN}• ❓ General Help${NC} - Should alert support team"
    
    echo -e "\n${PURPLE}📊 Expected Sentry Events:${NC}"
    echo -e "• Tag: ${BLUE}user_complaint:true${NC}"
    echo -e "• Categories: ${BLUE}complaint_category:bug|feature|help|urgent${NC}"
    echo -e "• Priorities: ${BLUE}complaint_priority:low|medium|high|urgent${NC}"
    
    echo -e "\n${PURPLE}🔔 Slack Notifications:${NC}"
    echo -e "• Check your configured Slack channels for alerts"
    echo -e "• Urgent complaints should trigger immediate notifications"
    echo -e "• Bug reports should alert development team"
    
    echo -e "\n${YELLOW}Press Ctrl+C to stop the development server${NC}"
    echo -e "${YELLOW}Or close this terminal when testing is complete${NC}"
    
    # Keep server running
    wait $SERVER_PID
    
else
    echo -e "${RED}❌ Failed to start development server${NC}"
    exit 1
fi
