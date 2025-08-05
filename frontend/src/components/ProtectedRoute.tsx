import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getAuthenticatedUser } from '../config/api';

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
        // Try to get user data using the cookie
        await getAuthenticatedUser();
        setAuthenticated(true);
        setChecking(false);
      } catch (error) {
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
