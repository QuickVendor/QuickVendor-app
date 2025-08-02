import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { PageLayout, Card, CardContent, Button } from './ui';
import { MessageCircle, Store, Package, Loader2, Eye } from 'lucide-react';
import { getStorefrontData, trackClick } from '../apiService';
import { API_BASE_URL } from '../config/api';

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

  useEffect(() => {
    const fetchStorefrontData = async () => {
      try {
        if (!username) {
          setError('Invalid store URL');
          setLoading(false);
          return;
        }

        const data = await getStorefrontData(username);
        
        // Transform API response to match frontend interface
        const transformedData: StorefrontData = {
          vendorName: data.vendor_name,
          whatsappNumber: data.whatsapp_number,
          products: data.products.map((product: {
            id: string;
            name: string;
            price: number;
            image_urls: string[];
            description: string;
            is_available: boolean;
          }) => ({
            id: product.id,
            name: product.name,
            price: product.price,
            image_urls: product.image_urls,
            description: product.description,
            inStock: product.is_available
          }))
        };
        
        setStorefront(transformedData);
      } catch (error: unknown) {
        const errorMessage = error instanceof Error ? error.message : 'Failed to load store';
        
        // Show appropriate error
        if (errorMessage.includes('404') || errorMessage.includes('not found')) {
          setError('Store not found');
        } else {
          setError('Failed to load store');
        }
      } finally {
        setLoading(false);
      }
    };

    if (username) {
      fetchStorefrontData();
    }
  }, [username]);

  const handleWhatsAppClick = async (product: Product) => {
    setClickingProduct(product.id);
    
    try {
      // First: Track the click without waiting for response (non-blocking)
      trackClick(product.id);
      
      // Second: Immediately construct WhatsApp link and open it
      const message = encodeURIComponent(
        `Hi! I'm interested in "${product.name}" for ${formatPrice(product.price)}. Is it still available?`
      );
      
      // Open WhatsApp using vendor's whatsapp_number from API response
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
                  {/* Product Image - Clickable */}
                  <Link to={`/store/${username}/product/${product.id}`} className="block">
                    <div className="aspect-square bg-gray-100 rounded-t-lg overflow-hidden">
                      <img
                        src={getImageUrl(product.image_urls?.[0])}
                        alt={product.name}
                        className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                        loading="lazy"
                      />
                    </div>
                  </Link>
                  
                  {/* Product Details */}
                  <div className="p-4 space-y-3">
                    <div>
                      <Link to={`/store/${username}/product/${product.id}`} className="block hover:text-blue-600 transition-colors duration-200">
                        <h3 className="font-semibold text-gray-900 text-lg mb-1 line-clamp-2">
                          {product.name}
                        </h3>
                      </Link>
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
                    
                    {/* Action Buttons */}
                    <div className="grid grid-cols-2 gap-2">
                      <Link to={`/store/${username}/product/${product.id}`}>
                        <Button
                          variant="secondary"
                          className="w-full flex items-center justify-center gap-2 py-2 text-sm"
                        >
                          <Eye className="w-4 h-4" />
                          View Details
                        </Button>
                      </Link>
                      <Button
                        onClick={() => handleWhatsAppClick(product)}
                        loading={clickingProduct === product.id}
                        disabled={clickingProduct === product.id}
                        className="w-full bg-green-600 hover:bg-green-700 focus:ring-green-500 flex items-center justify-center gap-2 py-2 text-sm"
                      >
                        {clickingProduct === product.id ? (
                          'Opening...'
                        ) : (
                          <>
                            <MessageCircle className="w-4 h-4" />
                            Buy Now
                          </>
                        )}
                      </Button>
                    </div>
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
          Powered by <span className="font-semibold text-gray-700">QuickVendor</span>
        </p>
        <p className="text-gray-400 text-xs mt-1">
          Fast, secure, and easy online shopping
        </p>
      </div>
    </PageLayout>
  );
};