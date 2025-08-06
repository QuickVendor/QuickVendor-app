import { Routes, Route, Navigate, Link } from 'react-router-dom';
import { Store, MessageCircle, Package, ExternalLink } from 'lucide-react';
import * as Sentry from '@sentry/react';
import { AuthPage } from './components/AuthPage';
import { VendorDashboard } from './components/VendorDashboard';
import { StorefrontPage } from './components/StorefrontPage';
import { ProductDetailsPage } from './components/ProductDetailsPage';
import { ProtectedRoute } from './components/ProtectedRoute';

// Create Sentry-enhanced React Router components
const SentryRoutes = Sentry.withSentryRouting(Routes);
const SentryRoute = Sentry.withSentryRouting(Route);

function App() {
  return (
    <SentryRoutes>
      {/* Product details route - must come before storefront route to avoid conflicts */}
      <SentryRoute path="/store/:username/product/:productId" element={<ProductDetailsPage />} />
      
      {/* Public storefront route */}
      <SentryRoute path="/store/:username" element={<StorefrontPage />} />
      
      {/* Auth route */}
      <SentryRoute path="/auth" element={<AuthPage />} />
      
      {/* Vendor dashboard route */}
      <SentryRoute 
        path="/dashboard" 
        element={
          <ProtectedRoute>
            <VendorDashboard />
          </ProtectedRoute>
        } 
      />
      
      {/* Default route */}
      <SentryRoute 
        path="/" 
        element={<HomePage />} 
      />
      
      {/* Catch all route - redirect to home */}
      <SentryRoute path="*" element={<Navigate to="/" replace />} />
    </SentryRoutes>
  );
}

// Simple home page to show available routes
const HomePage: React.FC = () => {
  return (
    <div className="min-h-screen bg-white">
      {/* Navigation */}
      <nav className="bg-white border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <div className="flex-shrink-0 flex items-center">
                <Store className="w-8 h-8 text-blue-600 mr-2" />
                <span className="text-xl font-bold text-gray-900">QuickVendor</span>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <Link 
                to="/auth" 
                className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors duration-200"
              >
                Get Started
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative bg-gradient-to-br from-blue-50 via-white to-indigo-50 py-20 lg:py-32">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h1 className="text-4xl md:text-6xl font-bold text-gray-900 mb-6">
              Launch Your
              <span className="text-blue-600 block">Micro-Storefront</span>
              in Minutes
            </h1>
            <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
              Create a beautiful online store, manage your products, and sell directly through WhatsApp. 
              No technical skills required.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link 
                to="/auth" 
                className="bg-blue-600 text-white px-8 py-4 rounded-lg text-lg font-semibold hover:bg-blue-700 transition-all duration-200 shadow-lg hover:shadow-xl"
              >
                Start Selling Now
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Everything You Need to Sell Online
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Built for Nigerian entrepreneurs who want to start selling online quickly and efficiently.
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {/* Feature 1 */}
            <div className="text-center p-6 rounded-xl bg-blue-50 hover:bg-blue-100 transition-colors duration-200">
              <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-600 rounded-full mb-4">
                <MessageCircle className="w-8 h-8 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">WhatsApp Integration</h3>
              <p className="text-gray-600">
                Customers can instantly chat with you on WhatsApp to place orders. No complex checkout process.
              </p>
            </div>

            {/* Feature 2 */}
            <div className="text-center p-6 rounded-xl bg-green-50 hover:bg-green-100 transition-colors duration-200">
              <div className="inline-flex items-center justify-center w-16 h-16 bg-green-600 rounded-full mb-4">
                <Package className="w-8 h-8 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Easy Product Management</h3>
              <p className="text-gray-600">
                Add products, upload images, set prices, and manage inventory with our simple dashboard.
              </p>
            </div>

            {/* Feature 3 */}
            <div className="text-center p-6 rounded-xl bg-purple-50 hover:bg-purple-100 transition-colors duration-200">
              <div className="inline-flex items-center justify-center w-16 h-16 bg-purple-600 rounded-full mb-4">
                <ExternalLink className="w-8 h-8 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Shareable Storefront</h3>
              <p className="text-gray-600">
                Get a beautiful, mobile-optimized storefront that you can share anywhere on social media.
              </p>
            </div>
          </div>
        </div>
      </section>
      {/* How It Works Section */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              How It Works
            </h2>
            <p className="text-xl text-gray-600">
              Get your online store up and running in just 3 simple steps
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {/* Step 1 */}
            <div className="text-center">
              <div className="inline-flex items-center justify-center w-12 h-12 bg-blue-600 text-white rounded-full text-xl font-bold mb-4">
                1
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Sign Up & Setup</h3>
              <p className="text-gray-600">
                Create your account with just your email and WhatsApp number. No credit card required.
              </p>
            </div>

            {/* Step 2 */}
            <div className="text-center">
              <div className="inline-flex items-center justify-center w-12 h-12 bg-blue-600 text-white rounded-full text-xl font-bold mb-4">
                2
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Add Your Products</h3>
              <p className="text-gray-600">
                Upload product photos, add descriptions, and set your prices. Make your store look professional.
              </p>
            </div>

            {/* Step 3 */}
            <div className="text-center">
              <div className="inline-flex items-center justify-center w-12 h-12 bg-blue-600 text-white rounded-full text-xl font-bold mb-4">
                3
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Share & Sell</h3>
              <p className="text-gray-600">
                Share your storefront link on social media and start receiving orders through WhatsApp.
              </p>
            </div>
          </div>
        </div>
      </section>
      {/* CTA Section */}
      <section className="py-20 bg-blue-600">
        <div className="max-w-4xl mx-auto text-center px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
            Ready to Start Your Online Business?
          </h2>
          <p className="text-xl text-blue-100 mb-8">
            Join thousands of Nigerian entrepreneurs who are already selling online with QuickVendor.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link 
              to="/auth" 
              className="bg-white text-blue-600 px-8 py-4 rounded-lg text-lg font-semibold hover:bg-gray-100 transition-all duration-200 shadow-lg hover:shadow-xl"
            >
              Create Your Store Now
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            {/* Brand */}
            <div className="col-span-1 md:col-span-2">
              <div className="flex items-center mb-4">
                <Store className="w-8 h-8 text-blue-400 mr-2" />
                <span className="text-xl font-bold">QuickVendor</span>
              </div>
              <p className="text-gray-400 mb-4">
                Empowering Nigerian entrepreneurs to build successful online businesses through 
                simple, effective micro-storefronts.
              </p>
            </div>

            {/* Quick Links */}
            <div>
              <h3 className="text-lg font-semibold mb-4">Quick Links</h3>
              <ul className="space-y-2">
                <li><Link to="/auth" className="text-gray-400 hover:text-white transition-colors duration-200">Get Started</Link></li>
              </ul>
            </div>

            {/* Support */}
            <div>
              <h3 className="text-lg font-semibold mb-4">Support</h3>
              <ul className="space-y-2">
                <li><span className="text-gray-400">Help Center</span></li>
                <li><span className="text-gray-400">Contact Us</span></li>
                <li><span className="text-gray-400">WhatsApp Support</span></li>
              </ul>
            </div>
          </div>
          
          <div className="border-t border-gray-800 mt-8 pt-8 text-center">
            <p className="text-gray-400">
              © 2025 QuickVendor. Built for Nigerian entrepreneurs.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
};
export default App;