import React from 'react';
import * as Sentry from '@sentry/react';

interface SentryTestProps {
  className?: string;
}

export const SentryTest: React.FC<SentryTestProps> = ({ className = '' }) => {
  const testJavaScriptError = () => {
    throw new Error('Test JavaScript Error - This is a test error for Sentry monitoring');
  };

  const testAsyncError = async () => {
    try {
      await new Promise((_, reject) => {
        setTimeout(() => reject(new Error('Test Async Error - This is a test async error for Sentry monitoring')), 100);
      });
    } catch (error) {
      Sentry.captureException(error);
      throw error;
    }
  };

  const testManualError = () => {
    Sentry.captureException(new Error('Manual Error Report - This error was manually reported to Sentry'));
    alert('Manual error reported to Sentry!');
  };

  const testPerformance = () => {
    // Use modern Sentry performance API
    Sentry.startSpan({
      name: 'Test Performance Span',
      op: 'test',
    }, () => {
      // Simulate some work
      setTimeout(() => {
        alert('Performance span sent to Sentry!');
      }, 1000);
    });
  };

  const testUserFeedback = () => {
    const eventId = Sentry.captureMessage('User Feedback Test Message');
    
    Sentry.showReportDialog({
      eventId,
      title: 'Test Feedback',
      subtitle: 'This is a test of the Sentry user feedback feature',
      subtitle2: 'Please provide any feedback about this test',
    });
  };

  if (import.meta.env.MODE === 'production') {
    return null; // Don't show in production
  }

  return (
    <div className={`bg-yellow-50 border border-yellow-200 rounded-lg p-4 ${className}`}>
      <h3 className="text-lg font-semibold text-yellow-800 mb-3">
        🧪 Sentry Testing (Development Only)
      </h3>
      <p className="text-sm text-yellow-700 mb-4">
        Use these buttons to test different Sentry features. Make sure you have a valid DSN configured.
      </p>
      
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
        <button
          onClick={testJavaScriptError}
          className="bg-red-500 text-white px-3 py-2 rounded text-sm hover:bg-red-600 transition-colors"
        >
          Test JS Error
        </button>
        
        <button
          onClick={testAsyncError}
          className="bg-orange-500 text-white px-3 py-2 rounded text-sm hover:bg-orange-600 transition-colors"
        >
          Test Async Error
        </button>
        
        <button
          onClick={testManualError}
          className="bg-blue-500 text-white px-3 py-2 rounded text-sm hover:bg-blue-600 transition-colors"
        >
          Manual Report
        </button>
        
        <button
          onClick={testPerformance}
          className="bg-green-500 text-white px-3 py-2 rounded text-sm hover:bg-green-600 transition-colors"
        >
          Test Performance
        </button>
        
        <button
          onClick={testUserFeedback}
          className="bg-purple-500 text-white px-3 py-2 rounded text-sm hover:bg-purple-600 transition-colors"
        >
          User Feedback
        </button>
        
        <button
          onClick={() => {
            Sentry.addBreadcrumb({
              message: 'Test breadcrumb added',
              level: 'info',
              timestamp: Date.now() / 1000,
            });
            alert('Breadcrumb added! This will show up in the next error report.');
          }}
          className="bg-gray-500 text-white px-3 py-2 rounded text-sm hover:bg-gray-600 transition-colors"
        >
          Add Breadcrumb
        </button>
      </div>
      
      <div className="mt-3 text-xs text-yellow-600">
        <strong>Note:</strong> These tests will only work if you have configured a valid Sentry DSN in your environment variables.
      </div>
    </div>
  );
};

export default SentryTest;
