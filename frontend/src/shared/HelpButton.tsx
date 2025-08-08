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
