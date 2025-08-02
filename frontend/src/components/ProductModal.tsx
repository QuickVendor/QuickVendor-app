import React, { useState, useEffect } from 'react';
import { Button, Input, Textarea, Toggle } from './ui';
import { Modal } from './ui/Modal';
import { Upload, X } from 'lucide-react';
import { createProduct, updateProduct } from '../apiService';
import { API_BASE_URL } from '../config/api';

// Helper function to get full image URL
const getImageUrl = (imagePath: string | null | undefined): string => {
  if (!imagePath) {
    return '';
  }
  
  // If it's already a full URL, return as is
  if (imagePath.startsWith('http')) {
    return imagePath;
  }
  
  // If it's a relative path, prepend the API base URL
  return `${API_BASE_URL}${imagePath}`;
};

interface Product {
  id: string;
  name: string;
  price: number;
  image_urls: string[];
  clickCount: number;
  description?: string;
  inStock?: boolean;
}

interface ProductModalProps {
  isOpen: boolean;
  onClose: () => void;
  product?: Product | null;
  onSave: () => void;
}

interface ProductFormData {
  name: string;
  price: string;
  description: string;
  inStock: boolean;
  images: (File | null)[];
  imagePreviews: string[];
}

export const ProductModal: React.FC<ProductModalProps> = ({
  isOpen,
  onClose,
  product,
  onSave
}) => {
  const [formData, setFormData] = useState<ProductFormData>({
    name: '',
    price: '',
    description: '',
    inStock: true,
    images: [null, null, null, null, null],
    imagePreviews: ['', '', '', '', '']
  });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (product) {
      setFormData({
        name: product.name,
        price: product.price.toString(),
        description: product.description || '',
        inStock: product.inStock ?? true,
        images: [null, null, null, null, null],
        imagePreviews: [...product.image_urls.map(url => getImageUrl(url)), '', '', '', '', ''].slice(0, 5)
      });
    } else {
      setFormData({
        name: '',
        price: '',
        description: '',
        inStock: true,
        images: [null, null, null, null, null],
        imagePreviews: ['', '', '', '', '']
      });
    }
    setErrors({});
  }, [product, isOpen]);

  const handleImageUpload = (index: number, file: File | null) => {
    const newImages = [...formData.images];
    const newPreviews = [...formData.imagePreviews];
    
    newImages[index] = file;
    
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        newPreviews[index] = e.target?.result as string;
        setFormData(prev => ({ ...prev, imagePreviews: newPreviews }));
      };
      reader.readAsDataURL(file);
    } else {
      newPreviews[index] = '';
    }
    
    setFormData(prev => ({
      ...prev,
      images: newImages,
      imagePreviews: newPreviews
    }));
  };

  const removeImage = (index: number) => {
    handleImageUpload(index, null);
  };

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.name.trim()) {
      newErrors.name = 'Product name is required';
    }

    if (!formData.price.trim()) {
      newErrors.price = 'Price is required';
    } else {
      const price = parseFloat(formData.price);
      if (isNaN(price) || price <= 0) {
        newErrors.price = 'Price must be a valid number greater than 0';
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validateForm()) return;
    
    setLoading(true);
    
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        setErrors({ general: 'Authentication required. Please login again.' });
        setLoading(false);
        return;
      }
      
      // Create FormData for multipart form submission
      const formDataToSend = new FormData();
      formDataToSend.append('name', formData.name);
      formDataToSend.append('description', formData.description);
      formDataToSend.append('price', formData.price);
      formDataToSend.append('is_available', formData.inStock.toString());
      
      // Add images
      formData.images.forEach((image, index) => {
        if (image) {
          formDataToSend.append(`image_${index + 1}`, image);
        }
      });
      
      if (product) {
        // Update existing product
        await updateProduct(product.id, formDataToSend, token);
      } else {
        // Create new product
        await createProduct(formDataToSend, token);
      }
      
      onSave();
      onClose();
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to save product';
      setErrors({ general: errorMessage });
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    if (!loading) {
      onClose();
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={handleClose}
      title={product ? 'Edit Product' : 'Add New Product'}
      maxWidth="lg"
    >
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Error Message */}
        {errors.general && (
          <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-sm text-red-600">{errors.general}</p>
          </div>
        )}

        {/* Product Name */}
        <Input
          label="Product Name"
          type="text"
          placeholder="Enter product name"
          value={formData.name}
          onChange={(e) => setFormData({ ...formData, name: e.target.value })}
          error={errors.name}
          disabled={loading}
        />

        {/* Price */}
        <Input
          label="Price (₦)"
          type="number"
          placeholder="0.00"
          step="0.01"
          min="0"
          value={formData.price}
          onChange={(e) => setFormData({ ...formData, price: e.target.value })}
          error={errors.price}
          disabled={loading}
        />

        {/* Description */}
        <Textarea
          label="Description"
          placeholder="Enter product description (optional)"
          value={formData.description}
          onChange={(e) => setFormData({ ...formData, description: e.target.value })}
          rows={3}
          disabled={loading}
        />

        {/* Multiple Images */}
        <div className="space-y-4">
          <label className="block text-sm font-medium text-gray-700">
            Product Images (up to 5)
            <span className="text-gray-500 font-normal ml-1">- Optional</span>
          </label>
          
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            {[0, 1, 2, 3, 4].map((index) => (
              <div key={index} className="space-y-2">
                <div className="relative">
                  {formData.imagePreviews[index] ? (
                    <div className="relative group">
                      <img
                        src={getImageUrl(formData.imagePreviews[index])}
                        alt={`Product image ${index + 1}`}
                        className="w-full h-32 object-cover rounded-lg border-2 border-gray-200"
                      />
                      <button
                        type="button"
                        onClick={() => removeImage(index)}
                        disabled={loading}
                        aria-label={`Remove image ${index + 1}`}
                        title={`Remove image ${index + 1}`}
                        className="absolute top-2 right-2 p-1 bg-red-500 text-white rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-200 hover:bg-red-600 disabled:opacity-50"
                      >
                        <X className="w-4 h-4" />
                      </button>
                    </div>
                  ) : (
                    <label className="flex flex-col items-center justify-center w-full h-32 border-2 border-gray-300 border-dashed rounded-lg cursor-pointer bg-gray-50 hover:bg-gray-100 transition-colors duration-200">
                      <div className="flex flex-col items-center justify-center pt-5 pb-6">
                        <Upload className="w-6 h-6 mb-2 text-gray-400" />
                        <p className="text-xs text-gray-500">
                          Image {index + 1}
                        </p>
                      </div>
                      <input
                        type="file"
                        className="hidden"
                        accept="image/*"
                        onChange={(e) => {
                          const file = e.target.files?.[0] || null;
                          handleImageUpload(index, file);
                        }}
                        disabled={loading}
                      />
                    </label>
                  )}
                </div>
              </div>
            ))}
          </div>
          
          <p className="text-xs text-gray-500">
            Tip: Upload high-quality images to showcase your product better. First image will be the main product image.
          </p>
        </div>

        {/* Stock Status */}
        <div className="flex items-center justify-between">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Stock Status
            </label>
            <p className="text-sm text-gray-500">
              Control whether this product appears in your storefront
            </p>
          </div>
          <Toggle
            label="In Stock"
            checked={formData.inStock}
            onChange={(checked) => setFormData({ ...formData, inStock: checked })}
            disabled={loading}
          />
        </div>

        {/* Form Actions */}
        <div className="flex gap-3 pt-4">
          <Button
            type="button"
            variant="secondary"
            onClick={handleClose}
            disabled={loading}
            className="flex-1"
          >
            Cancel
          </Button>
          <Button
            type="submit"
            loading={loading}
            disabled={loading}
            className="flex-1"
          >
            {product ? 'Update Product' : 'Create Product'}
          </Button>
        </div>
      </form>
    </Modal>
  );
};