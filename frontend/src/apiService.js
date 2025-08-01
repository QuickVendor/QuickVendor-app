const API_BASE_URL = import.meta.env.VITE_API_BASE_URL

/**
 * Login user with email and password
 * @param {string} email - User email
 * @param {string} password - User password
 * @returns {Promise<{access_token: string, token_type: string}>}
 */
export const login = async (email, password) => {
  const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: new URLSearchParams({
      username: email,
      password: password
    })
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Login failed');
  }

  return response.json();
};

/**
 * Register new user
 * @param {string} email - User email
 * @param {string} password - User password
 * @param {string} whatsapp_number - WhatsApp number
 * @returns {Promise<{id: string, email: string}>}
 */
export const register = async (email, password, whatsapp_number) => {
  const response = await fetch(`${API_BASE_URL}/api/users/register`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      email,
      password,
      whatsapp_number
    })
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Registration failed');
  }

  return response.json();
};

/**
 * Get authenticated user profile
 * @param {string} token - JWT token
 * @returns {Promise<{id: string, email: string, whatsapp_number: string, store_url: string}>}
 */
export const getAuthenticatedUser = async (token) => {
  const response = await fetch(`${API_BASE_URL}/api/users/me`, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    }
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to get user profile');
  }

  return response.json();
};

/**
 * Get all products for authenticated user
 * @param {string} token - JWT token
 * @returns {Promise<Array>} Array of product objects
 */
export const getProducts = async (token) => {
  const response = await fetch(`${API_BASE_URL}/api/products`, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    }
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to get products');
  }

  return response.json();
};

/**
 * Create new product
 * @param {FormData} formData - FormData object with product data and images
 * @param {string} token - JWT token
 * @returns {Promise<Object>} Created product object
 */
export const createProduct = async (formData, token) => {
  const response = await fetch(`${API_BASE_URL}/api/products`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
    },
    body: formData
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to create product');
  }

  return response.json();
};

/**
 * Update existing product
 * @param {string} productId - Product ID
 * @param {FormData} formData - FormData object with updated product data and images
 * @param {string} token - JWT token
 * @returns {Promise<Object>} Updated product object
 */
export const updateProduct = async (productId, formData, token) => {
  const response = await fetch(`${API_BASE_URL}/api/products/${productId}`, {
    method: 'PUT',
    headers: {
      'Authorization': `Bearer ${token}`,
    },
    body: formData
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to update product');
  }

  return response.json();
};

/**
 * Delete product
 * @param {string} productId - Product ID
 * @param {string} token - JWT token
 * @returns {Promise<void>}
 */
export const deleteProduct = async (productId, token) => {
  const response = await fetch(`${API_BASE_URL}/api/products/${productId}`, {
    method: 'DELETE',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    }
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to delete product');
  }
};

/**
 * Get public storefront data for a username
 * @param {string} username - Vendor username
 * @returns {Promise<{vendor_name: string, whatsapp_number: string, products: Array}>}
 */
export const getStorefrontData = async (username) => {
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
 * @param {string} productId - Product ID
 * @returns {Promise<{message: string}>}
 */
export const trackClick = async (productId) => {
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
