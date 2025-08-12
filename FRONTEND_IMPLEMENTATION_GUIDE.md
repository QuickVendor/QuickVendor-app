# Frontend Implementation Guide for Store Customization Features

## ⚠️ CRITICAL: Banner Upload Troubleshooting

The backend is currently returning 422 errors when trying to upload banners. The issue is that **no file is being received** by the backend.

### Frontend Requirements:
1. **MUST use field name "banner" or "image"** in the FormData
2. **Ensure proper multipart/form-data headers** - Let the browser set the Content-Type header automatically (do NOT manually set it)
3. **Example working code:**

```javascript
// CORRECT Implementation
const uploadBanner = async (file) => {
  const formData = new FormData();
  formData.append('banner', file); // MUST be 'banner' or 'image'
  
  const response = await fetch('/api/users/me/banner', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`
      // DO NOT set 'Content-Type' - let browser handle it
    },
    body: formData
  });
  
  return response.json();
};
```

### Common Mistakes to Avoid:
- ❌ Using wrong field name (e.g., `formData.append('file', file)`)
- ❌ Manually setting Content-Type header
- ❌ Sending JSON instead of FormData
- ❌ Not including the actual file in FormData

### Debug Steps:
1. Check browser DevTools Network tab to see what's being sent
2. Verify the field name in the multipart form data
3. Ensure the file is actually attached to the request

## Overview
This guide provides all the frontend changes needed to support the new store customization features:
1. Custom store names
2. Custom store URLs (slugs)
3. Store banner images

## 1. API Service Updates

### Update User Service
Add these new endpoints to your API service:

```javascript
// services/api.js or userService.js

// Get current user profile (updated to include new fields)
export const getUserProfile = async () => {
  const response = await fetch(`${API_BASE_URL}/api/users/me`, {
    headers: {
      'Authorization': `Bearer ${getToken()}`,
    },
  });
  return response.json();
  // Returns: { id, email, whatsapp_number, store_name, store_slug, banner_url }
};

// Update store information
export const updateStoreInfo = async (storeData) => {
  const response = await fetch(`${API_BASE_URL}/api/users/me/store`, {
    method: 'PUT',
    headers: {
      'Authorization': `Bearer ${getToken()}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(storeData),
  });
  return response.json();
};

// Upload store banner
export const uploadStoreBanner = async (file) => {
  const formData = new FormData();
  formData.append('banner', file);
  
  const response = await fetch(`${API_BASE_URL}/api/users/me/banner`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${getToken()}`,
    },
    body: formData,
  });
  return response.json();
};

// Delete store banner
export const deleteStoreBanner = async () => {
  const response = await fetch(`${API_BASE_URL}/api/users/me/banner`, {
    method: 'DELETE',
    headers: {
      'Authorization': `Bearer ${getToken()}`,
    },
  });
  return response.ok;
};

// Get public storefront (updated to support custom slugs)
export const getStorefront = async (storeIdentifier) => {
  const response = await fetch(`${API_BASE_URL}/api/store/${storeIdentifier}`);
  return response.json();
  // Returns: { vendor_name, whatsapp_number, products, banner_url, store_slug }
};
```

## 2. Store Settings Component

Create a new component for store customization:

```jsx
// components/StoreSettings.jsx
import React, { useState, useEffect } from 'react';
import { getUserProfile, updateStoreInfo, uploadStoreBanner, deleteStoreBanner } from '../services/api';

const StoreSettings = () => {
  const [profile, setProfile] = useState(null);
  const [storeName, setStoreName] = useState('');
  const [storeSlug, setStoreSlug] = useState('');
  const [bannerUrl, setBannerUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [uploadingBanner, setUploadingBanner] = useState(false);

  useEffect(() => {
    loadProfile();
  }, []);

  const loadProfile = async () => {
    try {
      const data = await getUserProfile();
      setProfile(data);
      setStoreName(data.store_name || '');
      setStoreSlug(data.store_slug || '');
      setBannerUrl(data.banner_url || '');
    } catch (error) {
      console.error('Failed to load profile:', error);
    }
  };

  const handleUpdateStoreInfo = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage('');

    try {
      const data = await updateStoreInfo({
        store_name: storeName,
        store_slug: storeSlug,
      });
      
      setProfile(data);
      setMessage('Store information updated successfully!');
    } catch (error) {
      setMessage('Failed to update store information. Make sure the URL is unique.');
    } finally {
      setLoading(false);
    }
  };

  const handleBannerUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    // Validate file size (5MB max)
    if (file.size > 5 * 1024 * 1024) {
      setMessage('Banner image must be less than 5MB');
      return;
    }

    setUploadingBanner(true);
    setMessage('');

    try {
      const data = await uploadStoreBanner(file);
      setBannerUrl(data.banner_url);
      setMessage('Banner uploaded successfully!');
      loadProfile(); // Refresh profile
    } catch (error) {
      setMessage('Failed to upload banner');
    } finally {
      setUploadingBanner(false);
    }
  };

  const handleDeleteBanner = async () => {
    if (!confirm('Are you sure you want to delete your banner?')) return;

    try {
      await deleteStoreBanner();
      setBannerUrl('');
      setMessage('Banner deleted successfully');
      loadProfile();
    } catch (error) {
      setMessage('Failed to delete banner');
    }
  };

  const generateSlug = (name) => {
    return name
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, '-')
      .replace(/^-+|-+$/g, '');
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h2 className="text-2xl font-bold mb-6">Store Settings</h2>

      {message && (
        <div className={`p-4 rounded mb-4 ${
          message.includes('Failed') ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'
        }`}>
          {message}
        </div>
      )}

      {/* Store Information Section */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <h3 className="text-lg font-semibold mb-4">Store Information</h3>
        
        <form onSubmit={handleUpdateStoreInfo}>
          <div className="mb-4">
            <label className="block text-sm font-medium mb-2">
              Store Name
            </label>
            <input
              type="text"
              value={storeName}
              onChange={(e) => setStoreName(e.target.value)}
              placeholder="John's Fashion Store"
              className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              maxLength={100}
            />
            <p className="text-xs text-gray-500 mt-1">
              This is how your store name will appear to customers
            </p>
          </div>

          <div className="mb-4">
            <label className="block text-sm font-medium mb-2">
              Store URL
            </label>
            <div className="flex items-center">
              <span className="text-gray-500 mr-2">yoursite.com/store/</span>
              <input
                type="text"
                value={storeSlug}
                onChange={(e) => setStoreSlug(e.target.value.toLowerCase().replace(/[^a-z0-9-]/g, ''))}
                placeholder="johns-fashion"
                className="flex-1 px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                pattern="^[a-z0-9-]+$"
                maxLength={50}
              />
            </div>
            <p className="text-xs text-gray-500 mt-1">
              Only lowercase letters, numbers, and hyphens allowed
            </p>
            {storeName && !storeSlug && (
              <button
                type="button"
                onClick={() => setStoreSlug(generateSlug(storeName))}
                className="text-xs text-blue-600 hover:underline mt-1"
              >
                Generate from store name
              </button>
            )}
          </div>

          <button
            type="submit"
            disabled={loading}
            className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? 'Saving...' : 'Save Changes'}
          </button>
        </form>

        {/* Store Link Display */}
        {storeSlug && (
          <div className="mt-4 p-4 bg-gray-50 rounded">
            <p className="text-sm font-medium mb-2">Your Store Link:</p>
            <div className="flex items-center gap-2">
              <code className="bg-white px-3 py-1 rounded border">
                {window.location.origin}/store/{storeSlug}
              </code>
              <button
                onClick={() => {
                  navigator.clipboard.writeText(`${window.location.origin}/store/${storeSlug}`);
                  setMessage('Link copied to clipboard!');
                }}
                className="text-sm bg-gray-200 px-3 py-1 rounded hover:bg-gray-300"
              >
                Copy
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Banner Section */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4">Store Banner</h3>
        
        {bannerUrl ? (
          <div className="mb-4">
            <img
              src={bannerUrl}
              alt="Store banner"
              className="w-full h-48 object-cover rounded-lg mb-4"
            />
            <button
              onClick={handleDeleteBanner}
              className="text-red-600 hover:underline"
            >
              Delete Banner
            </button>
          </div>
        ) : (
          <div className="mb-4">
            <div className="w-full h-48 bg-gray-100 rounded-lg flex items-center justify-center mb-4">
              <p className="text-gray-500">No banner uploaded</p>
            </div>
          </div>
        )}

        <div>
          <label className="block text-sm font-medium mb-2">
            Upload New Banner
          </label>
          <input
            type="file"
            accept="image/*"
            onChange={handleBannerUpload}
            disabled={uploadingBanner}
            className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
          />
          <p className="text-xs text-gray-500 mt-1">
            Recommended: 1200x300px, Max size: 5MB
          </p>
          {uploadingBanner && (
            <p className="text-sm text-blue-600 mt-2">Uploading banner...</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default StoreSettings;
```

## 3. Update Dashboard Component

Add a link to the store settings:

```jsx
// In your Dashboard component
<Link to="/settings/store" className="btn">
  <Settings className="w-5 h-5 mr-2" />
  Store Settings
</Link>

// Show store URL if available
{profile?.store_slug && (
  <div className="mb-4">
    <p className="text-sm text-gray-600">Your store URL:</p>
    <a 
      href={`/store/${profile.store_slug}`}
      target="_blank"
      className="text-blue-600 hover:underline"
    >
      {window.location.origin}/store/{profile.store_slug}
    </a>
  </div>
)}
```

## 4. Update Public Storefront Component

Update the storefront to display the banner and use the custom name:

```jsx
// components/Storefront.jsx
import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { getStorefront } from '../services/api';

const Storefront = () => {
  const { storeIdentifier } = useParams(); // Can be slug or username
  const [store, setStore] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadStore();
  }, [storeIdentifier]);

  const loadStore = async () => {
    try {
      const data = await getStorefront(storeIdentifier);
      setStore(data);
    } catch (error) {
      console.error('Failed to load store:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div>Loading store...</div>;
  if (!store) return <div>Store not found</div>;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Store Banner */}
      {store.banner_url ? (
        <div className="w-full h-64 relative">
          <img
            src={store.banner_url}
            alt={`${store.vendor_name} banner`}
            className="w-full h-full object-cover"
          />
          <div className="absolute inset-0 bg-black bg-opacity-40 flex items-end">
            <div className="p-8 text-white">
              <h1 className="text-4xl font-bold">{store.vendor_name}</h1>
            </div>
          </div>
        </div>
      ) : (
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-8">
          <h1 className="text-4xl font-bold">{store.vendor_name}</h1>
        </div>
      )}

      {/* Store Content */}
      <div className="container mx-auto px-4 py-8">
        {/* WhatsApp Contact */}
        <div className="mb-8">
          <a
            href={`https://wa.me/${store.whatsapp_number}`}
            className="inline-flex items-center bg-green-500 text-white px-6 py-3 rounded-lg hover:bg-green-600"
          >
            <WhatsApp className="w-5 h-5 mr-2" />
            Contact on WhatsApp
          </a>
        </div>

        {/* Products Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-6">
          {store.products.map(product => (
            <ProductCard key={product.id} product={product} />
          ))}
        </div>
      </div>
    </div>
  );
};
```

## 5. Update Routes

Add the store settings route:

```jsx
// In your main App or Routes component
import StoreSettings from './components/StoreSettings';

// Add this route
<Route path="/settings/store" element={
  <ProtectedRoute>
    <StoreSettings />
  </ProtectedRoute>
} />

// Update store route to use identifier instead of username
<Route path="/store/:storeIdentifier" element={<Storefront />} />
```

## 6. Form Validation

Add validation for store slug:

```javascript
// utils/validation.js
export const validateStoreSlug = (slug) => {
  if (!slug) return 'Store URL is required';
  if (slug.length < 3) return 'Store URL must be at least 3 characters';
  if (slug.length > 50) return 'Store URL must be less than 50 characters';
  if (!/^[a-z0-9-]+$/.test(slug)) {
    return 'Store URL can only contain lowercase letters, numbers, and hyphens';
  }
  return null;
};

export const validateStoreName = (name) => {
  if (!name) return 'Store name is required';
  if (name.length < 3) return 'Store name must be at least 3 characters';
  if (name.length > 100) return 'Store name must be less than 100 characters';
  return null;
};
```

## 7. Share Store Feature

Add a share button component:

```jsx
// components/ShareStore.jsx
const ShareStore = ({ storeSlug, storeName }) => {
  const storeUrl = `${window.location.origin}/store/${storeSlug}`;
  
  const shareOnWhatsApp = () => {
    const text = `Check out my store: ${storeName}`;
    window.open(`https://wa.me/?text=${encodeURIComponent(text + ' ' + storeUrl)}`);
  };
  
  const shareOnTwitter = () => {
    const text = `Check out my store: ${storeName}`;
    window.open(`https://twitter.com/intent/tweet?text=${encodeURIComponent(text)}&url=${encodeURIComponent(storeUrl)}`);
  };
  
  const copyLink = () => {
    navigator.clipboard.writeText(storeUrl);
    alert('Link copied to clipboard!');
  };
  
  return (
    <div className="flex gap-2">
      <button onClick={shareOnWhatsApp} className="btn-share">
        Share on WhatsApp
      </button>
      <button onClick={shareOnTwitter} className="btn-share">
        Share on Twitter
      </button>
      <button onClick={copyLink} className="btn-share">
        Copy Link
      </button>
    </div>
  );
};
```

## 8. Error Handling

Handle slug conflicts:

```javascript
// When updating store info
try {
  await updateStoreInfo({ store_name, store_slug });
} catch (error) {
  if (error.status === 409) {
    setError('This store URL is already taken. Please choose another.');
  } else {
    setError('Failed to update store information.');
  }
}
```

## 9. Migration for Existing Users

Show a prompt for users without a custom slug:

```jsx
// In Dashboard component
{!profile.store_slug && (
  <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-4">
    <h3 className="font-semibold text-yellow-800 mb-2">
      🎉 New Feature: Custom Store URL
    </h3>
    <p className="text-yellow-700 mb-3">
      You can now customize your store URL and add a banner image!
    </p>
    <Link to="/settings/store" className="btn btn-primary">
      Customize Your Store
    </Link>
  </div>
)}
```

## 10. CSS Styles

Add these styles for the components:

```css
/* Store Settings Styles */
.store-settings-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem;
}

.banner-preview {
  width: 100%;
  height: 300px;
  object-fit: cover;
  border-radius: 8px;
  margin-bottom: 1rem;
}

.banner-upload-area {
  border: 2px dashed #cbd5e0;
  border-radius: 8px;
  padding: 2rem;
  text-align: center;
  cursor: pointer;
  transition: border-color 0.3s;
}

.banner-upload-area:hover {
  border-color: #4299e1;
}

.store-url-preview {
  background: #f7fafc;
  padding: 1rem;
  border-radius: 8px;
  font-family: monospace;
  word-break: break-all;
}
```

## Testing Checklist

- [ ] Test store name update
- [ ] Test store slug validation (unique, format)
- [ ] Test banner upload (size limit, formats)
- [ ] Test banner deletion
- [ ] Test accessing store via custom slug
- [ ] Test backward compatibility with username
- [ ] Test sharing functionality
- [ ] Test on mobile devices
- [ ] Test error handling for duplicate slugs

## Notes

1. **Backward Compatibility**: The API supports both custom slugs and usernames, so existing links will still work.
2. **SEO**: Consider adding meta tags for the custom store names and banners.
3. **Performance**: Implement image optimization for banners before upload.
4. **Analytics**: Track store views and which access method is used (slug vs username).

This implementation will give your vendors a professional storefront with custom branding!
