import React, { createContext, useContext, useEffect, useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';

interface User {
  id?: string;
  email?: string;
  username?: string;
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (userData: User) => void;
  logout: () => void;
  checkAuth: () => Promise<boolean>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: React.ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();
  const location = useLocation();

  const checkAuth = async (): Promise<boolean> => {
    try {
      // Check if we have authentication tokens
      const hasToken = document.cookie.includes('access_token') || 
                      localStorage.getItem('auth_token') ||
                      localStorage.getItem('temp_debug_token');
      
      if (!hasToken) {
        return false;
      }

      const { getAuthenticatedUser } = await import('../shared/config/api');
      const userData = await getAuthenticatedUser();
      
      setUser({
        id: userData.id,
        email: userData.email,
        username: userData.username
      });
      
      return true;
    } catch (error) {
      console.warn('Auth check failed:', error);
      setUser(null);
      // Clear any invalid tokens
      localStorage.removeItem('auth_token');
      localStorage.removeItem('temp_debug_token');
      return false;
    }
  };

  const login = (userData: User) => {
    setUser(userData);
    
    // Get the intended route from location state or default to dashboard
    const from = (location.state as any)?.from?.pathname || '/dashboard';
    navigate(from, { replace: true });
  };

  const logout = () => {
    setUser(null);
    // Clear all auth-related data
    localStorage.removeItem('auth_token');
    localStorage.removeItem('temp_debug_token');
    document.cookie = 'access_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
    navigate('/login', { replace: true });
  };

  // Initialize auth state on app load
  useEffect(() => {
    const initAuth = async () => {
      setLoading(true);
      await checkAuth();
      setLoading(false);
    };

    initAuth();
  }, []);

  const value: AuthContextType = {
    user,
    loading,
    login,
    logout,
    checkAuth
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
