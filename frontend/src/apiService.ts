import { API_BASE_URL } from './config/api';

/**
 * Get public storefront data for a username
 */
export const getStorefrontData = async (username: string) => {
  const response = await fetch(`${API_BASE_URL}/api/store/${username}`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    }
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to get storefront data');
  }

  return response.json();
};

/**
 * Track click on a product (public endpoint)
 */
export const trackClick = async (productId: string) => {
  const response = await fetch(`${API_BASE_URL}/api/products/${productId}/track-click`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    }
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to track click');
  }

  return response.json();
};

/**
 * Create new product - now uses cookie-based authentication
 */
export const createProduct = async (formData: FormData) => {
  // Get debug token from localStorage for Authorization header fallback
  const debugToken = localStorage.getItem('temp_debug_token');
  
  const headers: Record<string, string> = {};
  
  // Add Authorization header as fallback if debug token exists
  if (debugToken) {
    headers['Authorization'] = `Bearer ${debugToken}`;
    console.log('Creating product with debug token as fallback');
  }
  
  const response = await fetch(`${API_BASE_URL}/api/products`, {
    method: 'POST',
    headers,
    credentials: 'include', // Send cookies for authentication
    body: formData
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to create product');
  }

  return response.json();
};

/**
 * Update existing product - now uses cookie-based authentication
 */
export const updateProduct = async (productId: string, formData: FormData) => {
  // Get debug token from localStorage for Authorization header fallback
  const debugToken = localStorage.getItem('temp_debug_token');
  
  const headers: Record<string, string> = {};
  
  // Add Authorization header as fallback if debug token exists
  if (debugToken) {
    headers['Authorization'] = `Bearer ${debugToken}`;
    console.log('Updating product with debug token as fallback');
  }
  
  const response = await fetch(`${API_BASE_URL}/api/products/${productId}`, {
    method: 'PUT',
    headers,
    credentials: 'include', // Send cookies for authentication
    body: formData
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to update product');
  }

  return response.json();
};
