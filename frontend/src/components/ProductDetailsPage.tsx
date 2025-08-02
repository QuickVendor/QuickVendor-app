import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { PageLayout, Button, Card, CardContent } from './ui';
import { ArrowLeft, MessageCircle, Eye, Store, Loader2, ChevronLeft, ChevronRight, Package } from 'lucide-react';
import { getStorefrontData, trackClick } from '../apiService';
import { API_BASE_URL } from '../config/api';

// Helper function to get full image URL
const getImageUrl = (imagePath: string | null | undefined): string => {
  if (!imagePath) {
    return 'https://images.pexels.com/photos/90946/pexels-photo-90946.jpeg?auto=compress&cs=tinysrgb&w=800';
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
  is_available: boolean;
}

interface StorefrontData {
  vendor_name: string;
  whatsapp_number: string;
  products: Product[];
}

export const ProductDetailsPage: React.FC = () => {
  const { username, productId } = useParams<{ username: string; productId: string }>();
  const navigate = useNavigate();
  const [product, setProduct] = useState<Product | null>(null);
  const [vendorData, setVendorData] = useState<{ vendor_name: string; whatsapp_number: string } | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [clickingProduct, setClickingProduct] = useState(false);
  const [currentImageIndex, setCurrentImageIndex] = useState(0);

  useEffect(() => {
    const fetchProductData = async () => {
      try {
        if (!username || !productId) {
          setError('Invalid product URL');
          setLoading(false);
          return;
        }

        const data: StorefrontData = await getStorefrontData(username);
        const foundProduct = data.products.find(p => p.id === productId);
        
        if (!foundProduct) {
          setError('Product not found');
          setLoading(false);
          return;
        }

        if (!foundProduct.is_available) {
          setError('This product is currently unavailable');
          setLoading(false);
          return;
        }

        setProduct(foundProduct);
        setVendorData({
          vendor_name: data.vendor_name,
          whatsapp_number: data.whatsapp_number
        });
      } catch (error) {
        console.error('Failed to fetch product data:', error);
        setError('Failed to load product details');
      } finally {
        setLoading(false);
      }
    };

    fetchProductData();
  }, [username, productId]);

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('en-NG', {
      style: 'currency',
      currency: 'NGN'
    }).format(price);
  };

  const handleWhatsAppClick = async () => {
    if (!product || !vendorData) return;
    
    setClickingProduct(true);
    
    try {
      // Track the click
      await trackClick(product.id);
      
      // Create WhatsApp message
      const message = `Hi! I'm interested in your product:\n\n*${product.name}*\n${formatPrice(product.price)}\n\nCould you please provide more details?`;
      const whatsappUrl = `https://wa.me/${vendorData.whatsapp_number}?text=${encodeURIComponent(message)}`;
      
      // Open WhatsApp
      window.open(whatsappUrl, '_blank');
    } catch (error) {
      console.error('Failed to track click:', error);
      // Still open WhatsApp even if tracking fails
      const message = `Hi! I'm interested in your product:\n\n*${product.name}*\n${formatPrice(product.price)}\n\nCould you please provide more details?`;
      const whatsappUrl = `https://wa.me/${vendorData.whatsapp_number}?text=${encodeURIComponent(message)}`;
      window.open(whatsappUrl, '_blank');
    } finally {
      setClickingProduct(false);
    }
  };

  const goToStore = () => {
    navigate(`/store/${username}`);
  };

  const nextImage = () => {
    if (product && product.image_urls.length > 1) {
      setCurrentImageIndex((prev) => 
        prev === product.image_urls.length - 1 ? 0 : prev + 1
      );
    }
  };

  const prevImage = () => {
    if (product && product.image_urls.length > 1) {
      setCurrentImageIndex((prev) => 
        prev === 0 ? product.image_urls.length - 1 : prev - 1
      );
    }
  };

  if (loading) {
    return (
      <PageLayout className="bg-gray-50 flex items-center justify-center min-h-screen">
        <div className="text-center">
          <Loader2 className="w-8 h-8 animate-spin text-blue-600 mx-auto mb-4" />
          <p className="text-gray-600">Loading product details...</p>
        </div>
      </PageLayout>
    );
  }

  if (error || !product || !vendorData) {
    return (
      <PageLayout className="bg-gray-50">
        <div className="max-w-2xl mx-auto pt-20 text-center">
          <div className="bg-white rounded-xl shadow-sm p-8">
            <div className="text-red-500 mb-4">
              <Package className="w-16 h-16 mx-auto" />
            </div>
            <h1 className="text-2xl font-bold text-gray-900 mb-2">
              {error || 'Product Not Found'}
            </h1>
            <p className="text-gray-600 mb-6">
              The product you're looking for might have been removed or is temporarily unavailable.
            </p>
            <Button onClick={goToStore} className="flex items-center gap-2 mx-auto">
              <ArrowLeft className="w-4 h-4" />
              Back to Store
            </Button>
          </div>
        </div>
      </PageLayout>
    );
  }

  const hasMultipleImages = product.image_urls && product.image_urls.length > 1;

  return (
    <PageLayout className="bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 mb-8">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <button
              onClick={goToStore}
              className="flex items-center gap-2 text-gray-600 hover:text-gray-900 transition-colors duration-200"
            >
              <ArrowLeft className="w-5 h-5" />
              <span className="font-medium">Back to {vendorData.vendor_name}'s Store</span>
            </button>
            <div className="flex items-center gap-2 text-gray-500">
              <Store className="w-4 h-4" />
              <span className="text-sm">{vendorData.vendor_name}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Product Details */}
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
          {/* Product Images */}
          <div className="space-y-4">
            {/* Main Image */}
            <div className="relative aspect-square bg-gray-100 rounded-xl overflow-hidden">
              <img
                src={getImageUrl(product.image_urls?.[currentImageIndex])}
                alt={product.name}
                className="w-full h-full object-cover"
              />
              
              {/* Image Navigation */}
              {hasMultipleImages && (
                <>
                  <button
                    onClick={prevImage}
                    aria-label="Previous image"
                    className="absolute left-4 top-1/2 -translate-y-1/2 bg-white/80 hover:bg-white rounded-full p-2 transition-colors duration-200"
                  >
                    <ChevronLeft className="w-5 h-5 text-gray-700" />
                  </button>
                  <button
                    onClick={nextImage}
                    aria-label="Next image"
                    className="absolute right-4 top-1/2 -translate-y-1/2 bg-white/80 hover:bg-white rounded-full p-2 transition-colors duration-200"
                  >
                    <ChevronRight className="w-5 h-5 text-gray-700" />
                  </button>
                  
                  {/* Image Indicators */}
                  <div className="absolute bottom-4 left-1/2 -translate-x-1/2 flex gap-2">
                    {product.image_urls.map((_, index) => (
                      <button
                        key={index}
                        onClick={() => setCurrentImageIndex(index)}
                        aria-label={`View image ${index + 1}`}
                        className={`w-2 h-2 rounded-full transition-colors duration-200 ${
                          index === currentImageIndex ? 'bg-white' : 'bg-white/50'
                        }`}
                      />
                    ))}
                  </div>
                </>
              )}
            </div>
            
            {/* Thumbnail Images */}
            {hasMultipleImages && (
              <div className="grid grid-cols-4 gap-2">
                {product.image_urls.map((imageUrl, index) => (
                  <button
                    key={index}
                    onClick={() => setCurrentImageIndex(index)}
                    className={`aspect-square bg-gray-100 rounded-lg overflow-hidden border-2 transition-colors duration-200 ${
                      index === currentImageIndex ? 'border-blue-500' : 'border-transparent hover:border-gray-300'
                    }`}
                  >
                    <img
                      src={getImageUrl(imageUrl)}
                      alt={`${product.name} ${index + 1}`}
                      className="w-full h-full object-cover"
                    />
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Product Information */}
          <div className="space-y-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-4">
                {product.name}
              </h1>
              <div className="flex items-center gap-4 mb-6">
                <span className="text-4xl font-bold text-blue-600">
                  {formatPrice(product.price)}
                </span>
                <span className="inline-flex items-center gap-2 bg-green-100 text-green-800 text-sm font-medium px-3 py-1 rounded-full">
                  <div className="w-2 h-2 bg-green-500 rounded-full" />
                  In Stock
                </span>
              </div>
            </div>

            {/* Description */}
            <Card>
              <CardContent className="p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-3">Description</h3>
                <p className="text-gray-700 leading-relaxed">
                  {product.description || 'No description available for this product.'}
                </p>
              </CardContent>
            </Card>

            {/* Purchase Section */}
            <Card>
              <CardContent className="p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Interested in this product?</h3>
                <p className="text-gray-600 mb-6">
                  Contact {vendorData.vendor_name} directly via WhatsApp to place your order or ask questions.
                </p>
                
                <Button
                  onClick={handleWhatsAppClick}
                  loading={clickingProduct}
                  disabled={clickingProduct}
                  className="w-full bg-green-600 hover:bg-green-700 focus:ring-green-500 flex items-center justify-center gap-3 py-4 text-lg"
                >
                  {clickingProduct ? (
                    'Opening WhatsApp...'
                  ) : (
                    <>
                      <MessageCircle className="w-5 h-5" />
                      Contact on WhatsApp
                    </>
                  )}
                </Button>
                
                <p className="text-xs text-gray-500 text-center mt-3">
                  You'll be redirected to WhatsApp with a pre-filled message about this product.
                </p>
              </CardContent>
            </Card>

            {/* Store Info */}
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center gap-3 mb-3">
                  <Store className="w-5 h-5 text-blue-600" />
                  <h3 className="text-lg font-semibold text-gray-900">{vendorData.vendor_name}</h3>
                </div>
                <p className="text-gray-600 mb-4">
                  Browse more products from this vendor or contact them directly.
                </p>
                <Button
                  variant="secondary"
                  onClick={goToStore}
                  className="w-full flex items-center justify-center gap-2"
                >
                  <Eye className="w-4 h-4" />
                  View All Products
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </PageLayout>
  );
};
