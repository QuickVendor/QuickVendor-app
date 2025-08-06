import React from 'react';
import * as Sentry from '@sentry/react';
import { AlertTriangle, RefreshCw, Home } from 'lucide-react';

interface ErrorFallbackProps {
  error: unknown;
  resetError: () => void;
  componentStack?: string;
  eventId?: string;
}

export const ErrorFallback: React.FC<ErrorFallbackProps> = ({ error, resetError }) => {
  const errorMessage = error instanceof Error ? error.message : String(error);
  const errorStack = error instanceof Error ? error.stack : undefined;
  const goHome = () => {
    window.location.href = '/';
  };

  const reportFeedback = () => {
    Sentry.showReportDialog({
      title: 'Something went wrong',
      subtitle: 'Help us improve by providing additional details',
    });
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
      <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-8 text-center">
        <div className="text-red-500 mb-6">
          <AlertTriangle className="w-16 h-16 mx-auto" />
        </div>
        
        <h1 className="text-2xl font-bold text-gray-900 mb-2">
          Oops! Something went wrong
        </h1>
        
        <p className="text-gray-600 mb-6">
          We're sorry for the inconvenience. Our team has been notified and is working on a fix.
        </p>

        <div className="space-y-3">
          <button
            onClick={resetError}
            className="w-full bg-blue-600 text-white px-4 py-3 rounded-lg hover:bg-blue-700 transition-colors flex items-center justify-center gap-2 font-medium"
          >
            <RefreshCw className="w-4 h-4" />
            Try Again
          </button>
          
          <button
            onClick={goHome}
            className="w-full bg-gray-100 text-gray-700 px-4 py-3 rounded-lg hover:bg-gray-200 transition-colors flex items-center justify-center gap-2 font-medium"
          >
            <Home className="w-4 h-4" />
            Go to Homepage
          </button>
          
          <button
            onClick={reportFeedback}
            className="w-full text-gray-500 hover:text-gray-700 transition-colors text-sm"
          >
            Report this issue
          </button>
        </div>

        {import.meta.env.MODE === 'development' && (
          <details className="mt-6 text-left">
            <summary className="cursor-pointer text-sm text-gray-500 hover:text-gray-700">
              Developer Details
            </summary>
            <div className="mt-3 p-4 bg-red-50 rounded-lg border-l-4 border-red-400">
              <h4 className="text-sm font-medium text-red-800 mb-2">Error Details:</h4>
              <pre className="text-xs text-red-700 overflow-auto whitespace-pre-wrap">
                {errorMessage}
              </pre>
              {errorStack && (
                <>
                  <h4 className="text-sm font-medium text-red-800 mt-3 mb-2">Stack Trace:</h4>
                  <pre className="text-xs text-red-600 overflow-auto whitespace-pre-wrap max-h-32">
                    {errorStack}
                  </pre>
                </>
              )}
            </div>
          </details>
        )}
      </div>
    </div>
  );
};

export default ErrorFallback;
