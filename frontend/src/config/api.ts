// API Configuration for QuickVendor Frontend
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || (import.meta.env.MODE === 'production' ? 'https://quickvendor-app.onrender.com' : 'http://localhost:8000');

// Export the configured API base URL
export { API_BASE_URL };

// Helper function for making API calls
export const apiCall = async (endpoint: string, options: RequestInit = {}) => {
  const url = `${API_BASE_URL}${endpoint}`;
  const defaultHeaders = { 'Content-Type': 'application/json', 'Accept': 'application/json', };
  const config: RequestInit = { ...options, headers: { ...defaultHeaders, ...options.headers, }, };
  
  console.log(`Making API call to: ${url}`, { method: config.method || 'GET', headers: config.headers });
  
  const response = await fetch(url, config);
  
  console.log(`API response status: ${response.status} for ${url}`);
  
  return response;
};

// Helper for authenticated API calls
export const authenticatedApiCall = async (endpoint: string, options: RequestInit = {}) => {
  const token = localStorage.getItem('token');
  const authHeaders: Record<string, string> = token ? { 'Authorization': `Bearer ${token}`, } : {};
  return apiCall(endpoint, { ...options, headers: { ...authHeaders, ...options.headers, }, });
};

// New functions
export const getAuthenticatedUser = async (token: string) => {
  const response = await authenticatedApiCall('/api/users/me', { headers: { 'Authorization': `Bearer ${token}` }, });
  if (response.ok) {
    return response.json();
  }
  throw new Error('Failed to fetch authenticated user');
};

export const getProducts = async (token: string) => {
  const response = await authenticatedApiCall('/api/products', { headers: { 'Authorization': `Bearer ${token}` }, });
  if (response.ok) {
    return response.json();
  }
  throw new Error('Failed to fetch products');
};

export const deleteProduct = async (productId: string, token: string) => {
  const response = await authenticatedApiCall(`/api/products/${productId}`, { method: 'DELETE', headers: { 'Authorization': `Bearer ${token}` }, });
  if (!response.ok) {
    throw new Error('Failed to delete product');
  }
};
