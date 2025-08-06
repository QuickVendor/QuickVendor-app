// API Configuration for QuickVendor Frontend
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || (import.meta.env.MODE === 'production' ? 'https://quickvendor-app.onrender.com' : 'http://localhost:8000');

// Export the configured API base URL
export { API_BASE_URL };

// Helper function for making API calls
export const apiCall = async (endpoint: string, options: RequestInit = {}) => {
  const url = `${API_BASE_URL}${endpoint}`;
  const defaultHeaders = { 'Content-Type': 'application/json', 'Accept': 'application/json', };
  const config: RequestInit = { 
    ...options, 
    headers: { ...defaultHeaders, ...options.headers, },
    credentials: 'include', // Always include cookies for authentication
  };
  
  console.log(`Making API call to: ${url}`, { method: config.method || 'GET', headers: config.headers });
  
  const response = await fetch(url, config);
  
  console.log(`API response status: ${response.status} for ${url}`);
  
  return response;
};

// Helper for authenticated API calls (now uses cookies instead of headers)
export const authenticatedApiCall = async (endpoint: string, options: RequestInit = {}) => {
  // TEMPORARY DEBUG: Get fallback token from localStorage if available
  const debugToken = localStorage.getItem('temp_debug_token');
  
  // Prepare headers with potential Authorization fallback
  const headers: Record<string, string> = {
    ...(options.headers as Record<string, string> || {})
  };
  
  // If we have a debug token, include it as Authorization header for fallback
  if (debugToken) {
    headers['Authorization'] = `Bearer ${debugToken}`;
    console.log('Using debug token from localStorage as fallback');
  } else {
    console.log('No debug token found, relying on cookies only');
  }
  
  console.log('Making authenticated API call:', { endpoint, hasDebugToken: !!debugToken });
  
  const response = await apiCall(endpoint, { 
    ...options,
    headers,
    credentials: 'include', // Ensure cookies are sent (primary method)
  });
  
  // If we get 401 and have a debug token, it might be expired
  if (response.status === 401 && debugToken) {
    console.warn('Authentication failed with debug token, removing it');
    localStorage.removeItem('temp_debug_token');
  }
  
  return response;
};

// New functions - now using cookies for authentication
export const getAuthenticatedUser = async () => {
  const response = await authenticatedApiCall('/api/users/me');
  if (response.ok) {
    return response.json();
  }
  throw new Error('Failed to fetch authenticated user');
};

export const getProducts = async () => {
  const response = await authenticatedApiCall('/api/products');
  if (response.ok) {
    return response.json();
  }
  throw new Error('Failed to fetch products');
};

export const deleteProduct = async (productId: string) => {
  const response = await authenticatedApiCall(`/api/products/${productId}`, { method: 'DELETE' });
  if (!response.ok) {
    throw new Error('Failed to delete product');
  }
};

export const logout = async () => {
  const response = await apiCall('/api/auth/logout', { method: 'POST' });
  if (!response.ok) {
    throw new Error('Failed to logout');
  }
  return response.json();
};

// New session check function for better authentication reliability
export const checkSession = async () => {
  try {
    const response = await authenticatedApiCall('/api/auth/check-session');
    if (response.ok) {
      const data = await response.json();
      console.log('Session check result:', data);
      return data;
    }
    return { authenticated: false, source: 'api-error' };
  } catch (error) {
    console.error('Session check failed:', error);
    return { authenticated: false, source: 'network-error' };
  }
};
