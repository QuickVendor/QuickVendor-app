import { useState } from 'react';
import { Button, Input, Card, CardHeader, CardTitle, CardContent } from './ui';
import { User, ArrowRight, Eye, EyeOff, ArrowLeft } from 'lucide-react';
import { apiCall } from '../config/api';

interface LoginData {
  email: string;
  password: string;
}

interface SignupData {
  email: string;
  password: string;
  whatsappNumber: string;
}

export const AuthPage: React.FC = () => {
  const [isLogin, setIsLogin] = useState(true);
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [showLoginPassword, setShowLoginPassword] = useState(false);
  const [showSignupPassword, setShowSignupPassword] = useState(false);
  
  const [loginData, setLoginData] = useState<LoginData>({
    email: '',
    password: ''
  });
  
  const [signupData, setSignupData] = useState<SignupData>({
    email: '',
    password: '',
    whatsappNumber: ''
  });

  const validateWhatsApp = (number: string): boolean => {
    return number.startsWith('234') && number.length >= 13;
  };

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};
    
    if (isLogin) {
      if (!loginData.email) newErrors.email = 'Email is required';
      if (!loginData.password) newErrors.password = 'Password is required';
    } else {
      if (!signupData.email) newErrors.email = 'Email is required';
      if (!signupData.password) newErrors.password = 'Password is required';
      if (!signupData.whatsappNumber) {
        newErrors.whatsappNumber = 'WhatsApp number is required';
      } else if (!validateWhatsApp(signupData.whatsappNumber)) {
        newErrors.whatsappNumber = 'WhatsApp number must start with 234 and be at least 13 digits';
      }
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validateForm()) return;
    
    setLoading(true);
    setErrors({});
    
    try {
      const response = await apiCall('/api/auth/login', {
        method: 'POST',
        body: JSON.stringify({
          email: loginData.email,
          password: loginData.password
        }),
      });
      
      if (response.ok) {
        const data = await response.json();
        localStorage.setItem('token', data.access_token);
        window.location.href = '/dashboard';
      } else {
        const errorData = await response.json();
        setErrors({ general: errorData.detail || 'Login failed' });
      }
    } catch (error) {
      console.error('Login error:', error);
      if (error instanceof TypeError && error.message.includes('fetch')) {
        setErrors({ general: 'Unable to connect to server. Please check your internet connection and try again.' });
      } else {
        setErrors({ general: 'Network error. Please try again.' });
      }
    } finally {
      setLoading(false);
    }
  };

  const handleSignup = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validateForm()) return;
    
    setLoading(true);
    setErrors({});
    
    try {
      // Register user
      const registerResponse = await apiCall('/api/users/register', {
        method: 'POST',
        body: JSON.stringify({
          email: signupData.email,
          password: signupData.password,
          whatsapp_number: signupData.whatsappNumber
        }),
      });
      
      if (!registerResponse.ok) {
        const errorData = await registerResponse.json();
        if (registerResponse.status === 409) {
          setErrors({ general: 'Email already exists.' });
        } else {
          setErrors({ general: errorData.detail || 'Registration failed' });
        }
        return;
      }
      
      // Auto-login after successful registration
      const loginResponse = await apiCall('/api/auth/login', {
        method: 'POST',
        body: JSON.stringify({
          email: signupData.email,
          password: signupData.password
        }),
      });
      
      if (loginResponse.ok) {
        const loginData = await loginResponse.json();
        localStorage.setItem('token', loginData.access_token);
        window.location.href = '/dashboard';
      } else {
        setErrors({ general: 'Registration successful, but login failed. Please try logging in.' });
      }
    } catch (error) {
      console.error('Signup error:', error);
      if (error instanceof TypeError && error.message.includes('fetch')) {
        setErrors({ general: 'Unable to connect to server. Please check your internet connection and try again.' });
      } else {
        setErrors({ general: 'Network error. Please try again.' });
      }
    } finally {
      setLoading(false);
    }
  };

  const toggleMode = () => {
    setIsLogin(!isLogin);
    setErrors({});
    setLoginData({ email: '', password: '' });
    setSignupData({ email: '', password: '', whatsappNumber: '' });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50 flex items-center justify-center p-4">
      <div className="w-full max-w-md relative">
        {/* Back Button */}
        <button
          onClick={() => window.location.href = '/'}
          className="absolute -top-12 left-0 flex items-center gap-2 text-gray-600 hover:text-gray-900 transition-colors duration-200 group"
        >
          <ArrowLeft className="w-5 h-5 group-hover:-translate-x-1 transition-transform duration-200" />
          <span className="text-sm font-medium">Back to Home</span>
        </button>

        {/* Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-600 rounded-full mb-4">
            <User className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Vendor Login</h1>
          <p className="text-gray-600">
            {isLogin ? 'Welcome back! Please sign in to your account.' : 'Create your vendor account to get started.'}
          </p>
        </div>

        {/* Auth Card */}
        <Card className="shadow-xl border-0">
          <CardHeader>
            <CardTitle className="text-center">
              {isLogin ? 'Sign In' : 'Create Account'}
            </CardTitle>
          </CardHeader>
          <CardContent>
            {/* Toggle Buttons */}
            <div className="flex bg-gray-100 rounded-lg p-1 mb-6">
              <button
                type="button"
                onClick={() => !isLogin && toggleMode()}
                className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-all duration-200 ${
                  isLogin
                    ? 'bg-white text-blue-600 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                Login
              </button>
              <button
                type="button"
                onClick={() => isLogin && toggleMode()}
                className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-all duration-200 ${
                  !isLogin
                    ? 'bg-white text-blue-600 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                Sign Up
              </button>
            </div>

            {/* Error Message */}
            {errors.general && (
              <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
                <p className="text-sm text-red-600">{errors.general}</p>
              </div>
            )}

            {/* Login Form */}
            {isLogin ? (
              <form onSubmit={handleLogin} className="space-y-4">
                <Input
                  label="Email Address"
                  type="email"
                  placeholder="Enter your email"
                  value={loginData.email}
                  onChange={(e) => setLoginData({ ...loginData, email: e.target.value })}
                  error={errors.email}
                />
                
                <div className="relative">
                  <Input
                    label="Password"
                    type={showLoginPassword ? "text" : "password"}
                    placeholder="Enter your password"
                    value={loginData.password}
                    onChange={(e) => setLoginData({ ...loginData, password: e.target.value })}
                    error={errors.password}
                    className="pr-10"
                  />
                  <button
                    type="button"
                    className="absolute right-3 top-9 text-gray-400 hover:text-gray-600 transition-colors focus:outline-none"
                    onClick={() => setShowLoginPassword(!showLoginPassword)}
                  >
                    {showLoginPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                  </button>
                </div>
                
                <Button
                  type="submit"
                  loading={loading}
                  disabled={!loginData.email || !loginData.password}
                  className="w-full"
                >
                  {loading ? 'Signing In...' : 'Sign In'}
                  {!loading && <ArrowRight className="w-4 h-4 ml-2" />}
                </Button>
              </form>
            ) : (
              /* Signup Form */
              <form onSubmit={handleSignup} className="space-y-4">
                <Input
                  label="Email Address"
                  type="email"
                  placeholder="Enter your email"
                  value={signupData.email}
                  onChange={(e) => setSignupData({ ...signupData, email: e.target.value })}
                  error={errors.email}
                />
                
                <div className="relative">
                  <Input
                    label="Password"
                    type={showSignupPassword ? "text" : "password"}
                    placeholder="Create a password"
                    value={signupData.password}
                    onChange={(e) => setSignupData({ ...signupData, password: e.target.value })}
                    error={errors.password}
                    helperText="Must be at least 8 characters"
                    className="pr-10"
                  />
                  <button
                    type="button"
                    className="absolute right-3 top-9 text-gray-400 hover:text-gray-600 transition-colors focus:outline-none"
                    onClick={() => setShowSignupPassword(!showSignupPassword)}
                  >
                    {showSignupPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                  </button>
                </div>
                
                <Input
                  label="WhatsApp Number"
                  type="tel"
                  placeholder="234XXXXXXXXX"
                  value={signupData.whatsappNumber}
                  onChange={(e) => setSignupData({ ...signupData, whatsappNumber: e.target.value })}
                  error={errors.whatsappNumber}
                  helperText="Must start with 234 (e.g., 2348012345678)"
                />
                
                <Button
                  type="submit"
                  loading={loading}
                  disabled={!signupData.email || !signupData.password || !signupData.whatsappNumber}
                  className="w-full"
                >
                  {loading ? 'Creating Account...' : 'Create Account'}
                  {!loading && <ArrowRight className="w-4 h-4 ml-2" />}
                </Button>
              </form>
            )}

            {/* Footer Links */}
            <div className="mt-6 text-center">
              <p className="text-sm text-gray-600">
                {isLogin ? "Don't have an account? " : "Already have an account? "}
                <button
                  type="button"
                  onClick={toggleMode}
                  className="text-blue-600 hover:text-blue-700 font-medium transition-colors duration-200"
                >
                  {isLogin ? 'Sign up here' : 'Sign in here'}
                </button>
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Additional Info */}
        <div className="mt-6 text-center">
          <p className="text-xs text-gray-500">
            By continuing, you agree to our Terms of Service and Privacy Policy
          </p>
        </div>
      </div>
    </div>
  );
};