import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { checkSession } from '../config/api';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  const navigate = useNavigate();
  const [checking, setChecking] = useState(true);
  const [authenticated, setAuthenticated] = useState(false);

  useEffect(() => {
    const checkAuth = async () => {
      try {
        console.log('ProtectedRoute: Checking authentication...');
        
        // Check if we have a debug token
        const debugToken = localStorage.getItem('temp_debug_token');
        console.log('ProtectedRoute: Debug token available:', !!debugToken);
        
        // Use the new session check endpoint for more reliable authentication
        const sessionResult = await checkSession();
        console.log('ProtectedRoute: Session check result', sessionResult);
        
        if (sessionResult.authenticated) {
          setAuthenticated(true);
          setChecking(false);
        } else {
          console.warn('ProtectedRoute: Authentication failed, redirecting to auth');
          
          // Clear any invalid debug token
          localStorage.removeItem('temp_debug_token');
          
          // If authentication fails, redirect to auth page
          navigate('/auth', { replace: true });
        }
      } catch (error) {
        console.error('ProtectedRoute: Authentication check failed', error);
        
        // Clear any invalid debug token
        localStorage.removeItem('temp_debug_token');
        
        // If authentication fails, redirect to auth page
        navigate('/auth', { replace: true });
      }
    };
    
    checkAuth();
  }, [navigate]);

  if (checking) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return authenticated ? <>{children}</> : null;
};
