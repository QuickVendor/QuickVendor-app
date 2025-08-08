import React, { useState, useEffect } from 'react';
import { X, HelpCircle, Bug, MessageSquare, Lightbulb, AlertTriangle } from 'lucide-react';
import * as Sentry from '@sentry/react';
import { Modal } from '../components/ui/Modal';
import { Button } from '../components/ui';
import { Input } from '../components/ui';

interface ComplaintData {
  category: 'bug' | 'feature' | 'help' | 'urgent';
  title: string;
  description: string;
  contactEmail: string;
  priority: 'low' | 'medium' | 'high' | 'urgent';
  currentRoute: string;
  userContext?: {
    id?: string;
    email?: string;
  };
}

interface HelpModalProps {
  isOpen: boolean;
  onClose: () => void;
  userContext?: {
    id?: string;
    email?: string;
  };
}

const HelpModal: React.FC<HelpModalProps> = ({ isOpen, onClose, userContext }) => {
  const [formData, setFormData] = useState<Partial<ComplaintData>>({
    category: 'help',
    title: '',
    description: '',
    contactEmail: userContext?.email || '',
    priority: 'medium',
    currentRoute: window.location.pathname,
    userContext: userContext
  });
  
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSubmitted, setIsSubmitted] = useState(false);

  // Reset form when modal opens
  useEffect(() => {
    if (isOpen && !isSubmitted) {
      setFormData({
        category: 'help',
        title: '',
        description: '',
        contactEmail: userContext?.email || '',
        priority: 'medium',
        currentRoute: window.location.pathname,
        userContext: userContext
      });
      setErrors({});
      setIsSubmitting(false);
    }
  }, [isOpen, userContext]);

  // Reset submission state when modal closes
  useEffect(() => {
    if (!isOpen) {
      setIsSubmitted(false);
    }
  }, [isOpen]);

  const categoryOptions = [
    { value: 'bug' as const, label: '🐛 Bug Report', icon: Bug, description: 'Something is not working correctly' },
    { value: 'feature' as const, label: '💡 Feature Request', icon: Lightbulb, description: 'Suggest a new feature or improvement' },
    { value: 'help' as const, label: '❓ General Help', icon: MessageSquare, description: 'Need help using the application' },
    { value: 'urgent' as const, label: '🚨 Urgent Issue', icon: AlertTriangle, description: 'Critical issue affecting business operations' }
  ];

  const priorityOptions = [
    { value: 'low' as const, label: 'Low', color: 'text-green-600', description: 'Minor issue, no rush' },
    { value: 'medium' as const, label: 'Medium', color: 'text-yellow-600', description: 'Normal priority' },
    { value: 'high' as const, label: 'High', color: 'text-orange-600', description: 'Important, needs attention soon' },
    { value: 'urgent' as const, label: 'Urgent', color: 'text-red-600', description: 'Critical, needs immediate attention' }
  ];

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.title?.trim()) {
      newErrors.title = 'Please provide a brief title for your issue';
    }

    if (!formData.description?.trim()) {
      newErrors.description = 'Please describe your issue or request';
    } else if (formData.description.length < 10) {
      newErrors.description = 'Please provide more details (at least 10 characters)';
    }

    if (!formData.contactEmail?.trim()) {
      newErrors.contactEmail = 'Please provide your email for follow-up';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.contactEmail)) {
      newErrors.contactEmail = 'Please enter a valid email address';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const submitComplaint = async (complaintData: ComplaintData): Promise<string | null> => {
    try {
      // Create rich context for Sentry
      const sentryContext = {
        category: complaintData.category,
        priority: complaintData.priority,
        route: complaintData.currentRoute,
        userAgent: navigator.userAgent,
        timestamp: new Date().toISOString(),
        url: window.location.href,
        referrer: document.referrer,
        viewport: {
          width: window.innerWidth,
          height: window.innerHeight
        }
      };

      // Set user context if available
      if (complaintData.userContext?.id) {
        Sentry.setUser({
          id: complaintData.userContext.id,
          email: complaintData.userContext.email,
        });
      } else if (complaintData.contactEmail) {
        Sentry.setUser({
          email: complaintData.contactEmail,
        });
      }

      // Add tags for filtering and alerts
      Sentry.setTag('complaint_category', complaintData.category);
      Sentry.setTag('complaint_priority', complaintData.priority);
      Sentry.setTag('page_route', complaintData.currentRoute);
      Sentry.setTag('user_complaint', 'true');

      // Set context for rich debugging
      Sentry.setContext('complaint_details', sentryContext);
      
      // Add breadcrumb for the complaint submission
      Sentry.addBreadcrumb({
        message: `User submitted ${complaintData.category} complaint: ${complaintData.title}`,
        level: complaintData.priority === 'urgent' ? 'error' : 'info',
        category: 'user_feedback',
        timestamp: Date.now() / 1000,
      });

      // Submit user feedback to Sentry
      const eventId = Sentry.captureFeedback({
        name: complaintData.userContext?.email || complaintData.contactEmail.split('@')[0],
        email: complaintData.contactEmail,
        message: `[${complaintData.category.toUpperCase()}] ${complaintData.title}\n\n${complaintData.description}`
      });

      // Also capture as a custom event for better tracking
      Sentry.captureMessage(`User Complaint: ${complaintData.title}`, {
        level: complaintData.priority === 'urgent' ? 'error' : 'info',
        tags: {
          complaint_category: complaintData.category,
          complaint_priority: complaintData.priority,
        },
        contexts: {
          complaint: sentryContext
        }
      });

      return eventId;
    } catch (error) {
      console.error('Failed to submit complaint to Sentry:', error);
      // Even if Sentry fails, we don't want to break the user experience
      return null;
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) return;

    setIsSubmitting(true);
    
    try {
      const eventId = await submitComplaint(formData as ComplaintData);
      
      if (eventId) {
        console.log('Complaint submitted successfully with ID:', eventId);
      }
      
      setIsSubmitted(true);
      
      // Auto-close after showing success message
      setTimeout(() => {
        onClose();
      }, 3000);
      
    } catch (error) {
      console.error('Error submitting complaint:', error);
      setErrors({ general: 'Failed to submit your request. Please try again.' });
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
            Your request has been submitted!
          </h3>
          <p className="text-gray-600 mb-4">
            We've received your {formData.category} report and will review it promptly. 
            {formData.priority === 'urgent' ? ' Due to the urgent priority, our team will respond as soon as possible.' : ''}
          </p>
          <p className="text-sm text-gray-500">
            You'll receive a follow-up email at <strong>{formData.contactEmail}</strong> if needed.
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
    <Modal isOpen={isOpen} onClose={onClose} title="Need Help?" maxWidth="lg">
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* General Error */}
        {errors.general && (
          <div className="bg-red-50 border border-red-200 rounded-md p-3">
            <p className="text-sm text-red-600">{errors.general}</p>
          </div>
        )}

        {/* Category Selection */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-3">
            What type of help do you need?
          </label>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {categoryOptions.map((option) => {
              const Icon = option.icon;
              return (
                <button
                  key={option.value}
                  type="button"
                  onClick={() => setFormData({ ...formData, category: option.value })}
                  className={`p-3 rounded-lg border-2 text-left transition-colors ${
                    formData.category === option.value
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <div className="flex items-start space-x-3">
                    <Icon className="w-5 h-5 text-gray-600 mt-0.5" />
                    <div>
                      <div className="font-medium text-gray-900">{option.label}</div>
                      <div className="text-sm text-gray-500">{option.description}</div>
                    </div>
                  </div>
                </button>
              );
            })}
          </div>
        </div>

        {/* Title */}
        <Input
          label="Brief Title"
          placeholder="Describe your issue in a few words"
          value={formData.title || ''}
          onChange={(e) => setFormData({ ...formData, title: e.target.value })}
          error={errors.title}
          required
        />

        {/* Description */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Detailed Description *
          </label>
          <textarea
            className={`w-full px-3 py-2 border rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 ${
              errors.description ? 'border-red-300' : 'border-gray-300'
            }`}
            rows={4}
            placeholder="Please provide as much detail as possible about your issue or request. Include what you were trying to do, what happened, and what you expected to happen."
            value={formData.description || ''}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            required
          />
          {errors.description && (
            <p className="mt-1 text-sm text-red-600">{errors.description}</p>
          )}
          <p className="mt-1 text-sm text-gray-500">
            The more details you provide, the better we can help you.
          </p>
        </div>

        {/* Contact Email */}
        <Input
          label="Contact Email"
          type="email"
          placeholder="your.email@example.com"
          value={formData.contactEmail || ''}
          onChange={(e) => setFormData({ ...formData, contactEmail: e.target.value })}
          error={errors.contactEmail}
          required
          helperText="We'll use this to follow up if needed"
        />

        {/* Priority Level */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-3">
            Priority Level
          </label>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
            {priorityOptions.map((option) => (
              <button
                key={option.value}
                type="button"
                onClick={() => setFormData({ ...formData, priority: option.value })}
                className={`p-2 rounded-md border text-center transition-colors ${
                  formData.priority === option.value
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <div className={`font-medium ${option.color}`}>{option.label}</div>
                <div className="text-xs text-gray-500 mt-1">{option.description}</div>
              </button>
            ))}
          </div>
        </div>

        {/* Context Information */}
        <div className="bg-gray-50 rounded-lg p-4">
          <h4 className="text-sm font-medium text-gray-900 mb-2">
            Context Information (Automatically Captured)
          </h4>
          <div className="text-sm text-gray-600 space-y-1">
            <div><strong>Current Page:</strong> {formData.currentRoute}</div>
            <div><strong>User:</strong> {userContext?.email || 'Not logged in'}</div>
            <div><strong>Browser:</strong> {navigator.userAgent}</div>
          </div>
          <p className="text-xs text-gray-500 mt-2">
            This information helps us understand the context of your request.
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
            loading={isSubmitting}
            disabled={isSubmitting}
            className="flex-1"
          >
            {isSubmitting ? 'Submitting...' : 'Submit Request'}
          </Button>
        </div>
      </form>
    </Modal>
  );
};

export default HelpModal;
