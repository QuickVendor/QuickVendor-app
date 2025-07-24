import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { PageLayout, Card, CardContent, Button } from './ui';
import { MessageCircle, Store, Package, ExternalLink, Loader2 } from 'lucide-react';

interface Product {
  id: string;
  name: string;
  price: number;
  image: string;
  description: string;
  inStock: boolean;
}

interface StorefrontData {
  vendorName: string;
  whatsappNumber: string;
  products: Product[];
}

export const StorefrontPage: React.FC = () => {
  const { username } = useParams<{ username: string }>();
  const [storefront, setStorefront] = useState<StorefrontData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [clickingProduct, setClickingProduct] = useState<string | null>(null);

  // Mock data for demo purposes
  const mockStorefrontData: StorefrontData = {
    vendorName: "Demo Vendor",
    whatsappNumber: "2348012345678",
    products: [
      {
        id: "1",
        name: "Premium Wireless Headphones",
        price: 45000,
        image: "https://images.pexels.com/photos/3394650/pexels-photo-3394650.jpeg?auto=compress&cs=tinysrgb&w=400",
        description: "High-quality wireless headphones with noise cancellation and premium sound quality.",
        inStock: true
      },
      {
        id: "2",
        name: "Smart Fitness Watch",
        price: 32000,
        image: "https://images.pexels.com/photos/437037/pexels-photo-437037.jpeg?auto=compress&cs=tinysrgb&w=400",
        description: "Track your fitness goals with this advanced smartwatch featuring heart rate monitoring.",
        inStock: true
      },
      {
        id: "3",
        name: "Portable Bluetooth Speaker",
        price: 18000,
        image: "https://images.pexels.com/photos/1649771/pexels-photo-1649771.jpeg?auto=compress&cs=tinysrgb&w=400",
        description: "Compact and powerful Bluetooth speaker with crystal clear sound and long battery life.",
        inStock: true
      },
      {
        id: "4",
        name: "Professional Camera Lens",
        price: 125000,
        image: "https://images.pexels.com/photos/90946/pexels-photo-90946.jpeg?auto=compress&cs=tinysrgb&w=400",
        description: "Professional grade camera lens perfect for portrait and landscape photography.",
        inStock: true
      },
      {
        id: "5",
        name: "Gaming Mechanical Keyboard",
        price: 28000,
        image: "https://images.pexels.com/photos/2115256/pexels-photo-2115256.jpeg?auto=compress&cs=tinysrgb&w=400",
        description: "RGB mechanical gaming keyboard with customizable keys and premium switches.",
        inStock: true
      },
      {
        id: "6",
        name: "Wireless Phone Charger",
        price: 8500,
        image: "https://images.pexels.com/photos/4526414/pexels-photo-4526414.jpeg?auto=compress&cs=tinysrgb&w=400",
        description: "Fast wireless charging pad compatible with all Qi-enabled devices.",
        inStock: true
      }
    ]
  };

  useEffect(() => {
    if (username) {
      fetchStorefrontData();
    }
  }, [username]);

  const fetchStorefrontData = async () => {
    try {
      // For demo purposes, use mock data if username is 'demo-vendor'
      if (username === 'demo-vendor') {
        setStorefront(mockStorefrontData);
        setLoading(false);
        return;
      }
      
      const response = await fetch(`/api/store/${username}`);
      
      if (response.ok) {
        const data = await response.json();
        setStorefront(data);
      } else if (response.status === 404) {
        setError('Store not found');
      } else {
        setError('Failed to load store');
      }
    } catch (error) {
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleWhatsAppClick = async (product: Product) => {
    setClickingProduct(product.id);
    
    try {
      // Track the click
      await fetch(`/api/products/${product.id}/track-click`, {
        method: 'POST',
      });
      
      // Construct WhatsApp message
      const message = encodeURIComponent(
        `Hi! I'm interested in "${product.name}" for ${formatPrice(product.price)}. Is it still available?`
      );
      
      // Open WhatsApp
      const whatsappUrl = `https://wa.me/${storefront?.whatsappNumber}?text=${message}`;
      window.open(whatsappUrl, '_blank');
      
    } catch (error) {
      console.error('Failed to track click:', error);
      // Still open WhatsApp even if tracking fails
      const message = encodeURIComponent(
        `Hi! I'm interested in "${product.name}" for ${formatPrice(product.price)}. Is it still available?`
      );
      const whatsappUrl = `https://wa.me/${storefront?.whatsappNumber}?text=${message}`;
      window.open(whatsappUrl, '_blank');
    } finally {
      setClickingProduct(null);
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
      <PageLayout className="bg-white">
        <div className="flex flex-col items-center justify-center min-h-96 text-center">
          <Loader2 className="w-12 h-12 text-blue-600 animate-spin mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Loading Store...</h2>
          <p className="text-gray-600">Please wait while we fetch the latest products</p>
        </div>
      </PageLayout>
    );
  }

  if (error) {
    return (
      <PageLayout className="bg-white">
        <div className="flex flex-col items-center justify-center min-h-96 text-center">
          <Store className="w-16 h-16 text-gray-300 mb-4" />
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Store Not Found</h2>
          <p className="text-gray-600 mb-6">
            {error === 'Store not found' 
              ? "The store you're looking for doesn't exist or may have been moved."
              : error
            }
          </p>
          <Button
            onClick={() => window.location.reload()}
            variant="secondary"
            className="flex items-center gap-2"
          >
            Try Again
          </Button>
        </div>
      </PageLayout>
    );
  }

  const inStockProducts = storefront?.products.filter(product => product.inStock) || [];

  return (
    <PageLayout className="bg-gray-50" maxWidth="xl">
      {/* Store Header */}
      <div className="text-center mb-8 bg-white rounded-xl shadow-sm p-8">
        <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-full mb-4">
          <Store className="w-8 h-8 text-white" />
        </div>
        <h1 className="text-3xl md:text-4xl font-bold text-gray-900 mb-2">
          {storefront?.vendorName}'s Store
        </h1>
        <p className="text-gray-600 text-lg">
          Browse our collection and chat with us on WhatsApp to place your order
        </p>
        <div className="flex items-center justify-center gap-2 mt-4 text-sm text-gray-500">
          <MessageCircle className="w-4 h-4" />
          <span>Quick ordering via WhatsApp</span>
        </div>
      </div>

      {/* Products Section */}
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Package className="w-6 h-6 text-gray-700" />
            <h2 className="text-2xl font-bold text-gray-900">Available Products</h2>
            <span className="bg-green-100 text-green-800 text-sm font-medium px-2.5 py-0.5 rounded-full">
              {inStockProducts.length} in stock
            </span>
          </div>
        </div>

        {/* Products Grid */}
        {inStockProducts.length === 0 ? (
          <Card className="text-center py-16">
            <CardContent>
              <Package className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <h3 className="text-xl font-medium text-gray-900 mb-2">No Products Available</h3>
              <p className="text-gray-600 mb-6">
                This store doesn't have any products in stock at the moment.
              </p>
              <p className="text-sm text-gray-500">
                Check back later or contact the vendor directly.
              </p>
            </CardContent>
          </Card>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {inStockProducts.map((product) => (
              <Card key={product.id} className="group hover:shadow-lg transition-all duration-300 bg-white">
                <CardContent className="p-0">
                  {/* Product Image */}
                  <div className="aspect-square bg-gray-100 rounded-t-lg overflow-hidden">
                    <img
                      src={product.image || 'https://images.pexels.com/photos/90946/pexels-photo-90946.jpeg?auto=compress&cs=tinysrgb&w=400'}
                      alt={product.name}
                      className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                      loading="lazy"
                    />
                  </div>
                  
                  {/* Product Details */}
                  <div className="p-4 space-y-3">
                    <div>
                      <h3 className="font-semibold text-gray-900 text-lg mb-1 line-clamp-2">
                        {product.name}
                      </h3>
                      <p className="text-gray-600 text-sm line-clamp-2">
                        {product.description}
                      </p>
                    </div>
                    
                    {/* Price */}
                    <div className="flex items-center justify-between">
                      <span className="text-2xl font-bold text-blue-600">
                        {formatPrice(product.price)}
                      </span>
                      <span className="inline-flex items-center gap-1 bg-green-100 text-green-800 text-xs font-medium px-2 py-1 rounded-full">
                        <div className="w-2 h-2 bg-green-500 rounded-full" />
                        In Stock
                      </span>
                    </div>
                    
                    {/* WhatsApp Button */}
                    <Button
                      onClick={() => handleWhatsAppClick(product)}
                      loading={clickingProduct === product.id}
                      disabled={clickingProduct === product.id}
                      className="w-full bg-green-600 hover:bg-green-700 focus:ring-green-500 flex items-center justify-center gap-2 py-3"
                    >
                      {clickingProduct === product.id ? (
                        'Opening WhatsApp...'
                      ) : (
                        <>
                          <MessageCircle className="w-4 h-4" />
                          Chat on WhatsApp to Buy
                        </>
                      )}
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="mt-16 text-center py-8 border-t border-gray-200">
        <p className="text-gray-500 text-sm">
          Powered by <span className="font-semibold text-gray-700">VendorApp</span>
        </p>
        <p className="text-gray-400 text-xs mt-1">
          Fast, secure, and easy online shopping
        </p>
      </div>
    </PageLayout>
  );
};