import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import * as Sentry from '@sentry/react';
import App from './App.tsx';
import './index.css';

// Simple error fallback component
const ErrorFallback = ({ error, resetError }: { error: unknown; resetError: () => void }) => (
  <div role="alert" className="p-5 text-center">
    <h2>Something went wrong:</h2>
    <pre className="text-red-600">{error instanceof Error ? error.message : String(error)}</pre>
    <button onClick={resetError}>Try again</button>
  </div>
);
Sentry.init({
  dsn: import.meta.env.VITE_SENTRY_DSN,
  environment: import.meta.env.MODE || 'development',
  integrations: [
    Sentry.browserTracingIntegration(),
    Sentry.replayIntegration({
      maskAllText: false,
      blockAllMedia: false,
    }),
  ],
  // Performance Monitoring
  tracesSampleRate: import.meta.env.MODE === 'production' ? 0.1 : 1.0,
  // Session Replay
  replaysSessionSampleRate: 0.1,
  replaysOnErrorSampleRate: 1.0,
});

// Sentry Error Boundary component
const SentryErrorBoundary = Sentry.withErrorBoundary(
  ({ children }: { children: React.ReactNode }) => <>{children}</>,
  {
    fallback: (errorData) => <ErrorFallback {...errorData} />,
    showDialog: false,
  }
);

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <SentryErrorBoundary>
      <BrowserRouter>
        <App />
      </BrowserRouter>
    </SentryErrorBoundary>
  </StrictMode>
);
