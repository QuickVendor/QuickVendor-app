const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

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
 * Create new product
 */
export const createProduct = async (formData: FormData, token: string) => {
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
 */
export const updateProduct = async (productId: string, formData: FormData, token: string) => {
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
