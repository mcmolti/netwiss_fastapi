#!/usr/bin/env node

/**
 * CORS Configuration Test Script
 * Run this script to test CORS configuration between frontend and backend
 */

const https = require('https');
const http = require('http');

// Configuration
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const FRONTEND_URL = process.env.FRONTEND_URL || 'http://localhost:3000';

console.log('🔧 CORS Configuration Test');
console.log('==========================');
console.log(`Frontend URL: ${FRONTEND_URL}`);
console.log(`Backend URL: ${API_BASE_URL}`);
console.log('');

async function makeRequest(url, options = {}) {
  return new Promise((resolve, reject) => {
    const client = url.startsWith('https:') ? https : http;
    
    const req = client.request(url, {
      method: 'GET',
      headers: {
        'Origin': FRONTEND_URL,
        'Access-Control-Request-Method': 'GET',
        'Access-Control-Request-Headers': 'Content-Type, Accept',
        ...options.headers
      },
      ...options
    }, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        resolve({
          status: res.statusCode,
          headers: res.headers,
          data: data
        });
      });
    });
    
    req.on('error', reject);
    req.end();
  });
}

async function testEndpoint(endpoint, description) {
  console.log(`📡 Testing ${description}...`);
  
  try {
    const response = await makeRequest(`${API_BASE_URL}${endpoint}`);
    
    console.log(`   Status: ${response.status}`);
    console.log(`   CORS Headers:`);
    console.log(`     Access-Control-Allow-Origin: ${response.headers['access-control-allow-origin'] || 'Not set'}`);
    console.log(`     Access-Control-Allow-Methods: ${response.headers['access-control-allow-methods'] || 'Not set'}`);
    console.log(`     Access-Control-Allow-Headers: ${response.headers['access-control-allow-headers'] || 'Not set'}`);
    console.log(`     Access-Control-Allow-Credentials: ${response.headers['access-control-allow-credentials'] || 'Not set'}`);
    
    if (response.status === 200) {
      console.log('   ✅ Success');
    } else {
      console.log(`   ❌ Failed with status ${response.status}`);
    }
  } catch (error) {
    console.log(`   ❌ Error: ${error.message}`);
  }
  
  console.log('');
}

async function testPreflight(endpoint, description) {
  console.log(`🚀 Testing preflight for ${description}...`);
  
  try {
    const response = await makeRequest(`${API_BASE_URL}${endpoint}`, {
      method: 'OPTIONS'
    });
    
    console.log(`   Status: ${response.status}`);
    console.log(`   CORS Headers:`);
    console.log(`     Access-Control-Allow-Origin: ${response.headers['access-control-allow-origin'] || 'Not set'}`);
    console.log(`     Access-Control-Allow-Methods: ${response.headers['access-control-allow-methods'] || 'Not set'}`);
    console.log(`     Access-Control-Allow-Headers: ${response.headers['access-control-allow-headers'] || 'Not set'}`);
    console.log(`     Access-Control-Max-Age: ${response.headers['access-control-max-age'] || 'Not set'}`);
    
    if (response.status === 200 || response.status === 204) {
      console.log('   ✅ Preflight successful');
    } else {
      console.log(`   ❌ Preflight failed with status ${response.status}`);
    }
  } catch (error) {
    console.log(`   ❌ Preflight error: ${error.message}`);
  }
  
  console.log('');
}

async function runTests() {
  console.log('Starting CORS tests...\n');
  
  // Test basic endpoints
  await testEndpoint('/', 'Root endpoint');
  await testEndpoint('/health', 'Health check');
  await testEndpoint('/api/v1/templates/', 'Templates API');
  await testEndpoint('/api/v1/models', 'Models API');
  
  // Test preflight requests
  await testPreflight('/api/v1/templates/', 'Templates API');
  await testPreflight('/api/v1/generate-sections', 'Generate sections API');
  
  console.log('✨ CORS tests completed!');
  console.log('');
  console.log('💡 Tips:');
  console.log('   - If CORS headers are missing, check backend CORS configuration');
  console.log('   - If preflight fails, ensure OPTIONS method is allowed');
  console.log('   - For production, verify origins are properly configured');
}

// Run tests
runTests().catch(console.error);
