import React, { useState, useEffect } from 'react';
import { Button, Input, Textarea, Toggle } from './ui';
import { Modal } from './ui/Modal';
import { Upload, Image as ImageIcon } from 'lucide-react';
import { createProduct, updateProduct } from '../apiService';

interface Product {
  id: string;
  name: string;
  price: number;
  image: string;
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
  image: File | null;
  imagePreview: string;
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
    image: null,
    imagePreview: ''
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
        image: null,
        imagePreview: product.image || ''
      });
    } else {
      setFormData({
        name: '',
        price: '',
        description: '',
        inStock: true,
        image: null,
        imagePreview: ''
      });
    }
    setErrors({});
  }, [product, isOpen]);

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};
    
    if (!formData.name.trim()) {
      newErrors.name = 'Product name is required';
    }
    
    if (!formData.price.trim()) {
      newErrors.price = 'Price is required';
    } else if (isNaN(Number(formData.price)) || Number(formData.price) <= 0) {
      newErrors.price = 'Price must be a valid positive number';
    }
    
    if (!formData.description.trim()) {
      newErrors.description = 'Description is required';
    }
    
    if (!product && !formData.image && !formData.imagePreview) {
      newErrors.image = 'Product image is required';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      if (file.size > 5 * 1024 * 1024) { // 5MB limit
        setErrors({ ...errors, image: 'Image size must be less than 5MB' });
        return;
      }
      
      if (!file.type.startsWith('image/')) {
        setErrors({ ...errors, image: 'Please select a valid image file' });
        return;
      }
      
      setFormData({ ...formData, image: file });
      
      // Create preview
      const reader = new FileReader();
      reader.onload = (e) => {
        setFormData(prev => ({ ...prev, imagePreview: e.target?.result as string }));
      };
      reader.readAsDataURL(file);
      
      // Clear image error
      if (errors.image) {
        const newErrors = { ...errors };
        delete newErrors.image;
        setErrors(newErrors);
      }
    }
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
      
      // Transform form data to match API format
      const productData = {
        name: formData.name,
        description: formData.description,
        price: parseFloat(formData.price),
        is_available: formData.inStock,
        ...(formData.image && { image: formData.image })
      };
      
      if (product) {
        // Update existing product
        await updateProduct(product.id, productData, token);
      } else {
        // Create new product
        await createProduct(productData, token);
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
          value={formData.price}
          onChange={(e) => setFormData({ ...formData, price: e.target.value })}
          error={errors.price}
          helperText="Enter price in Nigerian Naira"
          disabled={loading}
        />

        {/* Description */}
        <Textarea
          label="Description"
          placeholder="Describe your product..."
          value={formData.description}
          onChange={(e) => setFormData({ ...formData, description: e.target.value })}
          error={errors.description}
          helperText="Provide a detailed description of your product"
          disabled={loading}
        />

        {/* Image Upload */}
        <div className="space-y-2">
          <label className="block text-sm font-medium text-gray-700">
            Product Image
          </label>
          
          {/* Image Preview */}
          {formData.imagePreview && (
            <div className="relative w-32 h-32 rounded-lg overflow-hidden border border-gray-200">
              <img
                src={formData.imagePreview}
                alt="Product preview"
                className="w-full h-full object-cover"
              />
            </div>
          )}
          
          {/* Upload Button */}
          <div className="flex items-center gap-4">
            <label className="cursor-pointer">
              <input
                type="file"
                accept="image/*"
                onChange={handleImageChange}
                className="hidden"
                disabled={loading}
              />
              <div className="flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-lg hover:border-gray-400 transition-colors duration-200">
                <Upload className="w-4 h-4 text-gray-600" />
                <span className="text-sm text-gray-700">
                  {formData.imagePreview ? 'Change Image' : 'Upload Image'}
                </span>
              </div>
            </label>
            
            {!formData.imagePreview && (
              <div className="flex items-center gap-2 text-gray-400">
                <ImageIcon className="w-4 h-4" />
                <span className="text-sm">No image selected</span>
              </div>
            )}
          </div>
          
          {errors.image && (
            <p className="text-sm text-red-600">{errors.image}</p>
          )}
          
          <p className="text-sm text-gray-500">
            Supported formats: JPG, PNG, GIF. Max size: 5MB
          </p>
        </div>

        {/* Stock Status */}
        <Toggle
          label="Product Availability"
          checked={formData.inStock}
          onChange={(checked) => setFormData({ ...formData, inStock: checked })}
          disabled={loading}
        />
        
        <div className="flex items-center gap-2 text-sm">
          <div className={`w-2 h-2 rounded-full ${formData.inStock ? 'bg-green-500' : 'bg-red-500'}`} />
          <span className={formData.inStock ? 'text-green-700' : 'text-red-700'}>
            {formData.inStock ? 'In Stock' : 'Out of Stock'}
          </span>
        </div>

        {/* Action Buttons */}
        <div className="flex gap-3 pt-4 border-t border-gray-200">
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
            {loading 
              ? (product ? 'Updating...' : 'Creating...') 
              : (product ? 'Update Product' : 'Create Product')
            }
          </Button>
        </div>
      </form>
    </Modal>
  );
};