import { useEffect, useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { checkSession } from '../../shared/config/api';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const [checking, setChecking] = useState(true);
  const [authenticated, setAuthenticated] = useState(false);

  useEffect(() => {
    const checkAuth = async () => {
      try {
        console.log('ProtectedRoute: Checking authentication for route:', location.pathname);
        
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
          console.warn('ProtectedRoute: Authentication failed, preserving intended route');
          
          // Clear any invalid debug token
          localStorage.removeItem('temp_debug_token');
          
          // Redirect to login with current location as state to preserve the intended route
          navigate('/login', { 
            replace: true, 
            state: { from: location }
          });
        }
      } catch (error) {
        console.error('ProtectedRoute: Authentication check failed', error);
        
        // Clear any invalid debug token
        localStorage.removeItem('temp_debug_token');
        
        // Redirect to login with current location as state to preserve the intended route
        navigate('/login', { 
          replace: true, 
          state: { from: location }
        });
      }
    };
    
    checkAuth();
  }, [navigate, location]);

  if (checking) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        <span className="ml-3 text-gray-600">Checking authentication...</span>
      </div>
    );
  }

  return authenticated ? <>{children}</> : null;
};
