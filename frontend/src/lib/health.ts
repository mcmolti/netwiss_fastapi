/**
 * Health check and CORS testing utilities
 */

import { API_BASE_URL } from './api'

interface HealthCheckResponse {
  status: string
  openai_api_key_configured: boolean
  timestamp: string
  cors_enabled: boolean
}

/**
 * Check API health and CORS configuration
 */
export async function checkAPIHealth(): Promise<HealthCheckResponse> {
  try {
    const response = await fetch(`${API_BASE_URL.replace('/api/v1', '')}/health`, {
      method: 'GET',
      credentials: 'include',
      mode: 'cors',
    })
    
    if (!response.ok) {
      throw new Error(`Health check failed: ${response.status}`)
    }
    
    const data = await response.json()
    return {
      ...data,
      timestamp: new Date().toISOString(),
      cors_enabled: true,
    }
  } catch (error) {
    console.error('Health check failed:', error)
    throw error
  }
}

/**
 * Test CORS configuration with a simple request
 */
export async function testCORS(): Promise<boolean> {
  try {
    await checkAPIHealth()
    return true
  } catch (error) {
    console.error('CORS test failed:', error)
    return false
  }
}

/**
 * Get environment information for debugging
 */
export function getEnvironmentInfo() {
  return {
    apiUrl: process.env.NEXT_PUBLIC_API_URL,
    environment: process.env.NEXT_PUBLIC_ENVIRONMENT,
    corsLogging: process.env.NEXT_PUBLIC_ENABLE_CORS_LOGGING,
    debugMode: process.env.NEXT_PUBLIC_ENABLE_DEBUG_MODE,
    requestLogging: process.env.NEXT_PUBLIC_ENABLE_REQUEST_LOGGING,
  }
}
