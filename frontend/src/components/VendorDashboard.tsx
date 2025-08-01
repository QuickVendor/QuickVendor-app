import React, { useState, useEffect } from 'react';
import { ProductModal } from './ProductModal';
import { authenticatedApiCall } from '../config/api';
import { 
  PageLayout, 
  PageHeader, 
  PageTitle, 
  Button, 
  Card, 
  CardHeader, 
  CardTitle, 
  CardContent 
} from './ui';
import { 
  LogOut, 
  Copy, 
  Plus, 
  Edit3, 
  Trash2, 
  ExternalLink, 
  Eye, 
  Package,
  CheckCircle,
  MousePointer,
  TrendingUp
} from 'lucide-react';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

// Helper function to get full image URL
const getImageUrl = (imagePath: string | null | undefined): string => {
  if (!imagePath) {
    return 'https://images.pexels.com/photos/90946/pexels-photo-90946.jpeg?auto=compress&cs=tinysrgb&w=400';
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
  click_count: number;
  description?: string | null;
  is_available: boolean;
  user_id: string;
  created_at: string;
  updated_at?: string | null;
}

interface ModalProduct {
  id: string;
  name: string;
  price: number;
  image_urls: string[];
  clickCount: number;
  description?: string;
  inStock?: boolean;
}

interface VendorData {
  username: string;
  email: string;
  storefrontUrl: string;
}

export const VendorDashboard: React.FC = () => {
  const [vendor, setVendor] = useState<VendorData | null>(null);
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [copySuccess, setCopySuccess] = useState(false);
  const [showProductModal, setShowProductModal] = useState(false);
  const [editingProduct, setEditingProduct] = useState<ModalProduct | null>(null);

  useEffect(() => {
    fetchVendorData();
    fetchProducts();
  }, []);

  const fetchVendorData = async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        console.error('No token found');
        return;
      }
      
      const data = await getAuthenticatedUser(token);
      setVendor({
        username: data.email.split('@')[0], // Extract username from email
        email: data.email,
        storefrontUrl: `${window.location.origin}/store/${data.email.split('@')[0]}`
      });
    } catch (error) {
      console.error('Failed to fetch vendor data:', error);
    }
  };

  const fetchProducts = async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        console.error('No token found');
        return;
      }
      
      const data = await getProducts(token);
      setProducts(data);
    } catch (error) {
      console.error('Failed to fetch products:', error);
    } finally {
      setLoading(false);
    }
  };

  const refreshProducts = () => {
    fetchProducts();
  };

  const handleLogout = async () => {
    try {
      const token = localStorage.getItem('token');
      await fetch('/api/auth/logout', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      localStorage.removeItem('token');
      window.location.href = '/';
    }
  };

  const copyStorefrontLink = async () => {
    if (vendor?.storefrontUrl) {
      try {
        await navigator.clipboard.writeText(vendor.storefrontUrl);
        setCopySuccess(true);
        setTimeout(() => setCopySuccess(false), 2000);
      } catch (error) {
        console.error('Failed to copy link:', error);
      }
    }
  };

  const handleAddProduct = () => {
    setEditingProduct(null);
    setShowProductModal(true);
  };

  const handleEditProduct = (product: Product) => {
    // Transform backend product format to frontend format for modal
    const transformedProduct: ModalProduct = {
      id: product.id,
      name: product.name,
      price: product.price,
      image_urls: product.image_urls || [],
      clickCount: product.click_count,
      description: product.description || '',
      inStock: product.is_available
    };
    setEditingProduct(transformedProduct);
    setShowProductModal(true);
  };

  const handleDeleteProduct = async (productId: string) => {
    if (!confirm('Are you sure you want to delete this product?')) return;
    
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        console.error('No token found');
        return;
      }
      
      await deleteProduct(productId, token);
      
      // Remove the deleted product from local state for instant UI update
      setProducts(products.filter(p => p.id !== productId));
    } catch (error) {
      console.error('Failed to delete product:', error);
      alert('Failed to delete product. Please try again.');
    }
  };

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('en-NG', {
      style: 'currency',
      currency: 'NGN',
    }).format(price);
  };

  if (loading) {
    return (
      <PageLayout>
        <div className="flex items-center justify-center min-h-96">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      </PageLayout>
    );
  }

  return (
    <PageLayout>
      {/* Header Section */}
      <PageHeader>
        <div className="flex items-center justify-between">
          <div>
            <PageTitle>Welcome, {vendor?.username || 'Vendor'}!</PageTitle>
            <p className="text-gray-600 mt-2">Manage your products and track your storefront performance</p>
          </div>
          <Button
            variant="secondary"
            onClick={handleLogout}
            className="flex items-center gap-2"
          >
            <LogOut className="w-4 h-4" />
            Logout
          </Button>
        </div>
      </PageHeader>

      {/* Storefront Link Section */}
      <Card className="mb-8 bg-gradient-to-r from-blue-50 to-indigo-50 border-blue-200">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-blue-900">
            <ExternalLink className="w-5 h-5" />
            Your Storefront
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-center gap-3 flex-wrap">
              <div className="flex-1 min-w-0">
                <p className="text-sm text-blue-700 mb-1">Share this link with your customers:</p>
                <div className="bg-white border border-blue-200 rounded-lg px-4 py-3 font-mono text-sm text-gray-800 break-all">
                  {vendor?.storefrontUrl || 'yourapp.com/vendor-username'}
                </div>
              </div>
              <Button
                onClick={copyStorefrontLink}
                variant={copySuccess ? 'primary' : 'secondary'}
                className={`flex items-center gap-2 transition-all duration-200 ${
                  copySuccess ? 'bg-green-600 hover:bg-green-700' : ''
                }`}
              >
                {copySuccess ? (
                  <>
                    <CheckCircle className="w-4 h-4" />
                    Copied!
                  </>
                ) : (
                  <>
                    <Copy className="w-4 h-4" />
                    Copy Link
                  </>
                )}
              </Button>
            </div>
            
            {/* Quick Share Options */}
            <div className="flex items-center gap-2 pt-2 border-t border-blue-200">
              <span className="text-sm text-blue-700 font-medium">Quick Share:</span>
              <Button
                variant="secondary"
                size="sm"
                onClick={() => {
                  const url = encodeURIComponent(vendor?.storefrontUrl || '');
                  const text = encodeURIComponent(`Check out my online store! Browse my products and place orders via WhatsApp: ${vendor?.storefrontUrl}`);
                  window.open(`https://wa.me/?text=${text}`, '_blank');
                }}
                className="text-green-600 border-green-300 hover:bg-green-50"
              >
                WhatsApp
              </Button>
              <Button
                variant="secondary"
                size="sm"
                onClick={() => {
                  const url = encodeURIComponent(vendor?.storefrontUrl || '');
                  const text = encodeURIComponent('Check out my online store!');
                  window.open(`https://www.facebook.com/sharer/sharer.php?u=${url}&quote=${text}`, '_blank');
                }}
                className="text-blue-600 border-blue-300 hover:bg-blue-50"
              >
                Facebook
              </Button>
              <Button
                variant="secondary"
                size="sm"
                onClick={() => {
                  const url = encodeURIComponent(vendor?.storefrontUrl || '');
                  const text = encodeURIComponent('Check out my online store!');
                  window.open(`https://twitter.com/intent/tweet?url=${url}&text=${text}`, '_blank');
                }}
                className="text-sky-600 border-sky-300 hover:bg-sky-50"
              >
                Twitter
              </Button>
            </div>
            
            {/* Preview Button */}
            <div className="pt-2">
              <Button
                variant="outline"
                onClick={() => window.open(vendor?.storefrontUrl, '_blank')}
                className="w-full flex items-center gap-2 justify-center"
              >
                <ExternalLink className="w-4 h-4" />
                Preview Your Storefront
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Analytics Summary Section */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {/* Total Products */}
        <Card className="bg-white border-l-4 border-l-blue-500">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Products</p>
                <p className="text-2xl font-bold text-gray-900">{products.length}</p>
              </div>
              <Package className="w-8 h-8 text-blue-500" />
            </div>
          </CardContent>
        </Card>

        {/* In Stock Products */}
        <Card className="bg-white border-l-4 border-l-green-500">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">In Stock</p>
                <p className="text-2xl font-bold text-gray-900">
                  {products.filter(p => p.is_available).length}
                </p>
              </div>
              <CheckCircle className="w-8 h-8 text-green-500" />
            </div>
          </CardContent>
        </Card>

        {/* Total Clicks */}
        <Card className="bg-white border-l-4 border-l-purple-500">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Clicks</p>
                <p className="text-2xl font-bold text-gray-900">
                  {products.reduce((sum, product) => sum + product.click_count, 0)}
                </p>
              </div>
              <MousePointer className="w-8 h-8 text-purple-500" />
            </div>
          </CardContent>
        </Card>

        {/* Top Product */}
        <Card className="bg-white border-l-4 border-l-orange-500">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Top Product</p>
                <p className="text-lg font-bold text-gray-900 truncate">
                  {products.length > 0 
                    ? products.reduce((top, product) => 
                        product.click_count > top.click_count ? product : top
                      ).name
                    : 'No products'
                  }
                </p>
              </div>
              <TrendingUp className="w-8 h-8 text-orange-500" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Products Section */}
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Package className="w-6 h-6 text-gray-700" />
            <h2 className="text-2xl font-bold text-gray-900">My Products</h2>
            <span className="bg-blue-100 text-blue-800 text-sm font-medium px-2.5 py-0.5 rounded-full">
              {products.length} {products.length === 1 ? 'product' : 'products'}
            </span>
          </div>
          <Button
            onClick={handleAddProduct}
            className="flex items-center gap-2"
          >
            <Plus className="w-4 h-4" />
            Add New Product
          </Button>
        </div>

        {/* Products Grid */}
        {products.length === 0 ? (
          <Card className="text-center py-12">
            <CardContent>
              <Package className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No products yet</h3>
              <p className="text-gray-600 mb-6">Start building your storefront by adding your first product.</p>
              <Button onClick={handleAddProduct} className="flex items-center gap-2 mx-auto">
                <Plus className="w-4 h-4" />
                Add Your First Product
              </Button>
            </CardContent>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {products.map((product) => (
              <Card key={product.id} hover className="group">
                <CardContent className="p-0">
                  {/* Product Image */}
                  <div className="aspect-square bg-gray-100 rounded-t-lg overflow-hidden">
                    <img
                      src={getImageUrl(product.image_urls?.[0])}
                      alt={product.name}
                      className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                    />
                  </div>
                  
                  {/* Product Info */}
                  <div className="p-4">
                    <h3 className="font-semibold text-gray-900 mb-2 line-clamp-2">
                      {product.name}
                    </h3>
                    
                    <div className="flex items-center justify-between mb-3">
                      <span className="text-xl font-bold text-blue-600">
                        {formatPrice(product.price)}
                      </span>
                      <div className="flex items-center gap-1 text-sm text-gray-600">
                        <Eye className="w-4 h-4" />
                        <span>{product.click_count} clicks</span>
                      </div>
                    </div>
                    
                    {/* Interest Clicks Badge */}
                    <div className="mb-4">
                      <span className="inline-flex items-center gap-1 bg-green-100 text-green-800 text-xs font-medium px-2.5 py-1 rounded-full">
                        <Eye className="w-3 h-3" />
                        Interest Clicks: {product.click_count}
                      </span>
                    </div>
                    
                    {/* Action Buttons */}
                    <div className="flex gap-2">
                      <Button
                        variant="secondary"
                        onClick={() => handleEditProduct(product)}
                        className="flex-1 flex items-center justify-center gap-2"
                      >
                        <Edit3 className="w-4 h-4" />
                        Edit
                      </Button>
                      <Button
                        variant="secondary"
                        onClick={() => handleDeleteProduct(product.id)}
                        className="px-3 text-red-600 border-red-300 hover:bg-red-50 hover:border-red-400"
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>

      {/* Product Modal Placeholder */}
      {showProductModal && (
        <ProductModal
          isOpen={showProductModal}
          onClose={() => setShowProductModal(false)}
          product={editingProduct}
          onSave={refreshProducts}
        />
      )}
    </PageLayout>
  );
};