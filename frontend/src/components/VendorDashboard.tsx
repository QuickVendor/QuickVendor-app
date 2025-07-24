import React, { useState, useEffect } from 'react';
import { ProductModal } from './ProductModal';
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
  CheckCircle
} from 'lucide-react';

interface Product {
  id: string;
  name: string;
  price: number;
  image: string;
  clickCount: number;
  description?: string;
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
  const [editingProduct, setEditingProduct] = useState<Product | null>(null);

  useEffect(() => {
    fetchVendorData();
    fetchProducts();
  }, []);

  const fetchVendorData = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/vendor/profile', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      
      if (response.ok) {
        const data = await response.json();
        setVendor(data);
      }
    } catch (error) {
      console.error('Failed to fetch vendor data:', error);
    }
  };

  const fetchProducts = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/products', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      
      if (response.ok) {
        const data = await response.json();
        setProducts(data);
      }
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
    setEditingProduct(product);
    setShowProductModal(true);
  };

  const handleDeleteProduct = async (productId: string) => {
    if (!confirm('Are you sure you want to delete this product?')) return;
    
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`/api/products/${productId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      
      if (response.ok) {
        setProducts(products.filter(p => p.id !== productId));
      }
    } catch (error) {
      console.error('Failed to delete product:', error);
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
        </CardContent>
      </Card>

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
                      src={product.image || 'https://images.pexels.com/photos/90946/pexels-photo-90946.jpeg?auto=compress&cs=tinysrgb&w=400'}
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
                        <span>{product.clickCount} clicks</span>
                      </div>
                    </div>
                    
                    {/* Interest Clicks Badge */}
                    <div className="mb-4">
                      <span className="inline-flex items-center gap-1 bg-green-100 text-green-800 text-xs font-medium px-2.5 py-1 rounded-full">
                        <Eye className="w-3 h-3" />
                        Interest Clicks: {product.clickCount}
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