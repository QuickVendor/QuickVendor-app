import React, { useState } from 'react';
import { MessageCircle, X } from 'lucide-react';
import FeedbackModal from './FeedbackModal';

interface FloatingFeedbackButtonProps {
  userContext?: {
    id?: string;
    email?: string;
    username?: string;
  } | null;
}

const FloatingFeedbackButton: React.FC<FloatingFeedbackButtonProps> = ({ userContext }) => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isHovered, setIsHovered] = useState(false);

  // Determine if user is authenticated for better user experience
  const isAuthenticated = Boolean(userContext?.id);

  return (
    <>
      {/* Floating Feedback Button */}
      <div className="fixed bottom-6 right-6 z-50">
        <button
          onClick={() => setIsModalOpen(true)}
          onMouseEnter={() => setIsHovered(true)}
          onMouseLeave={() => setIsHovered(false)}
          className="group bg-blue-600 hover:bg-blue-700 text-white rounded-full p-4 shadow-lg hover:shadow-xl transition-all duration-300 ease-in-out transform hover:scale-110 focus:outline-none focus:ring-4 focus:ring-blue-300 focus:ring-opacity-50"
          aria-label="Share Feedback"
          title="Share your feedback with us"
        >
          <MessageCircle className="w-6 h-6" />
          
          {/* Tooltip */}
          <div className={`absolute bottom-full right-0 mb-2 transition-all duration-200 pointer-events-none ${
            isHovered ? 'opacity-100 visible' : 'opacity-0 invisible'
          }`} data-testid="feedback-tooltip">
            <div className="bg-gray-900 text-white text-sm px-3 py-2 rounded-lg whitespace-nowrap shadow-lg">
              {isAuthenticated ? 'Share your feedback' : 'Share feedback anonymously'}
              <div className="absolute top-full right-4 w-0 h-0 border-l-4 border-l-transparent border-r-4 border-r-transparent border-t-4 border-t-gray-900"></div>
            </div>
          </div>
        </button>

        {/* Pulse animation ring - more subtle */}
        <div className="absolute inset-0 bg-blue-600 rounded-full animate-ping opacity-15 pointer-events-none"></div>
      </div>

      {/* Feedback Modal */}
      <FeedbackModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        userContext={userContext}
      />
    </>
  );
};

export default FloatingFeedbackButton;
