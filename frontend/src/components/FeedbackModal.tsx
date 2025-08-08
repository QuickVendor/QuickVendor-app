import React, { useState } from 'react';
import { X, MessageSquare, Send, Loader2 } from 'lucide-react';
import { Modal, Button } from './ui';

interface FeedbackData {
  message: string;
  url: string;
  timestamp: string;
}

interface FeedbackModalProps {
  isOpen: boolean;
  onClose: () => void;
  userContext?: {
    id?: string;
    email?: string;
    username?: string;
  } | null;
}

const FeedbackModal: React.FC<FeedbackModalProps> = ({ isOpen, onClose, userContext }) => {
  const [description, setDescription] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [error, setError] = useState('');

  // Reset form when modal opens
  React.useEffect(() => {
    if (isOpen && !isSubmitted) {
      setDescription('');
      setError('');
      setIsSubmitting(false);
    }
  }, [isOpen]);

  // Reset submission state when modal closes
  React.useEffect(() => {
    if (!isOpen) {
      setIsSubmitted(false);
    }
  }, [isOpen]);

  const submitFeedback = async (feedbackData: FeedbackData): Promise<boolean> => {
    try {
      // Get API base URL from environment or construct it
      const isDevelopment = window.location.hostname === 'localhost';
      let baseUrl = '';
      
      if (isDevelopment) {
        baseUrl = 'http://localhost:8000';
      } else {
        // In production, use environment variable or construct from current domain
        baseUrl = import.meta.env.VITE_API_BASE_URL || 
                 `${window.location.protocol}//quickvendor-backend.onrender.com`;
      }
      
      const url = `${baseUrl}/api/feedback/report`;
      console.log('Submitting feedback to:', url);
      
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          // Add any additional headers if needed
        },
        body: JSON.stringify(feedbackData),
      });

      console.log('Response status:', response.status);
      console.log('Response headers:', Object.fromEntries(response.headers.entries()));

      // Handle different response statuses
      if (!response.ok) {
        let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
        
        try {
          const contentType = response.headers.get('content-type');
          if (contentType && contentType.includes('application/json')) {
            const errorData = await response.json();
            errorMessage = errorData.detail || errorData.message || errorMessage;
          } else {
            const text = await response.text();
            if (text) {
              console.log('Non-JSON error response:', text);
              errorMessage = `${errorMessage}. Response: ${text.substring(0, 100)}`;
            }
          }
        } catch (parseError) {
          console.error('Error parsing error response:', parseError);
        }
        
        throw new Error(errorMessage);
      }

      // Parse successful response
      const contentType = response.headers.get('content-type');
      if (!contentType || !contentType.includes('application/json')) {
        const text = await response.text();
        console.error('Expected JSON response but got:', text);
        throw new Error(`Expected JSON response, got: ${text.substring(0, 100)}...`);
      }

      const result = await response.json();
      console.log('Success response:', result);
      
      if (result.success) {
        return true;
      } else {
        throw new Error(result.message || 'Failed to submit feedback');
      }
    } catch (error) {
      console.error('Error submitting feedback:', error);
      throw error;
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!description.trim()) {
      setError('Please describe your feedback');
      return;
    }

    if (description.trim().length < 5) {
      setError('Please provide more details (at least 5 characters)');
      return;
    }

    setIsSubmitting(true);
    setError('');
    
    try {
      const feedbackData: FeedbackData = {
        message: description.trim(),
        url: window.location.href,
        timestamp: new Date().toISOString()
      };

      await submitFeedback(feedbackData);
      setIsSubmitted(true);
      
      // Auto-close after showing success message
      setTimeout(() => {
        onClose();
      }, 3000);
      
    } catch (error) {
      setError('Failed to submit feedback. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (isSubmitted) {
    return (
      <Modal isOpen={isOpen} onClose={onClose} title="Thank You!" maxWidth="md">
        <div className="text-center py-8">
          <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            Feedback Submitted!
          </h3>
          <p className="text-gray-600 mb-4">
            Thank you for your feedback! We've received it and will review it promptly.
          </p>
          <p className="text-sm text-gray-500">
            Your input helps us improve the application.
          </p>
          <Button 
            onClick={onClose} 
            className="mt-6"
          >
            Close
          </Button>
        </div>
      </Modal>
    );
  }

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Share Your Feedback" maxWidth="md">
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Error Display */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-md p-3">
            <p className="text-sm text-red-600">{error}</p>
          </div>
        )}

        {/* Feedback Description */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            What would you like to share with us? *
          </label>
          <textarea
            className={`w-full px-3 py-3 border rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 resize-none ${
              error && !description.trim() ? 'border-red-300' : 'border-gray-300'
            }`}
            rows={5}
            placeholder="Tell us about your experience, report issues, suggest improvements, or ask questions..."
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            maxLength={1000}
            required
          />
          <div className="flex justify-between items-center mt-2">
            <p className="text-sm text-gray-500">
              Share anything on your mind - we're here to help!
            </p>
            <span className="text-xs text-gray-400">
              {description.length}/1000
            </span>
          </div>
        </div>

        {/* Context Information */}
        <div className="bg-gray-50 rounded-lg p-4">
          <h4 className="text-sm font-medium text-gray-900 mb-2 flex items-center">
            <MessageSquare className="w-4 h-4 mr-2" />
            Automatically Included
          </h4>
          <div className="text-sm text-gray-600 space-y-1">
            <div><strong>Current Page:</strong> {window.location.pathname}</div>
            <div><strong>Timestamp:</strong> {new Date().toLocaleString()}</div>
            <div><strong>User:</strong> {userContext?.email || 'Anonymous'}</div>
          </div>
          <p className="text-xs text-gray-500 mt-2">
            This context helps us understand and address your feedback better.
          </p>
        </div>

        {/* Submit Buttons */}
        <div className="flex gap-3 pt-4 border-t">
          <Button
            type="button"
            variant="secondary"
            onClick={onClose}
            disabled={isSubmitting}
            className="flex-1"
          >
            Cancel
          </Button>
          <Button
            type="submit"
            disabled={isSubmitting || !description.trim()}
            className="flex-1"
          >
            {isSubmitting ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Submitting...
              </>
            ) : (
              <>
                <Send className="w-4 h-4 mr-2" />
                Submit Feedback
              </>
            )}
          </Button>
        </div>
      </form>
    </Modal>
  );
};

export default FeedbackModal;
