import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      // Redirect to auth page if no token found
      navigate('/auth', { replace: true });
    }
  }, [navigate]);

  // Check if user has token
  const token = localStorage.getItem('token');
  if (!token) {
    return null; // Return nothing while redirecting
  }

  return <>{children}</>;
};
