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
  return apiCall(endpoint, { 
    ...options,
    credentials: 'include', // Ensure cookies are sent
  });
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
