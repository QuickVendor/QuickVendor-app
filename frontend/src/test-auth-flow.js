// Test file to verify authentication flow
// This will test the apiService functions directly

import { login, register } from './apiService.js';

async function testAuthenticationFlow() {
  console.log('🔄 Starting Authentication Flow Test...');
  
  try {
    // Test 1: Registration
    console.log('\n1. Testing Registration...');
    const testEmail = `test-${Date.now()}@example.com`;
    const testPassword = 'testpass123';
    const testWhatsApp = '2348012345678';
    
    const registerResult = await register(testEmail, testPassword, testWhatsApp);
    console.log('✅ Registration successful:', registerResult);
    
    // Test 2: Login
    console.log('\n2. Testing Login...');
    const loginResult = await login(testEmail, testPassword);
    console.log('✅ Login successful:', loginResult);
    console.log('🔐 Access token received:', loginResult.access_token ? 'Yes' : 'No');
    
    // Test 3: Invalid Login
    console.log('\n3. Testing Invalid Login...');
    try {
      await login(testEmail, 'wrongpassword');
      console.log('❌ Invalid login should have failed');
    } catch (error) {
      console.log('✅ Invalid login properly rejected:', error.message);
    }
    
    // Test 4: Duplicate Registration
    console.log('\n4. Testing Duplicate Registration...');
    try {
      await register(testEmail, testPassword, testWhatsApp);
      console.log('❌ Duplicate registration should have failed');
    } catch (error) {
      console.log('✅ Duplicate registration properly rejected:', error.message);
    }
    
    console.log('\n🎉 All authentication tests completed successfully!');
    
  } catch (error) {
    console.error('❌ Authentication test failed:', error.message);
  }
}

// Export for manual testing
window.testAuth = testAuthenticationFlow;
