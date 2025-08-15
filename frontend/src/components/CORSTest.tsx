'use client'

import { useState, useEffect } from 'react'
import { checkAPIHealth, testCORS, getEnvironmentInfo } from '@/lib/health'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

interface CORSTestProps {
  showDetails?: boolean
}

export function CORSTest({ showDetails = false }: CORSTestProps) {
  const [healthStatus, setHealthStatus] = useState<any>(null)
  const [corsStatus, setCorsStatus] = useState<boolean | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const runTests = async () => {
    setIsLoading(true)
    setError(null)
    
    try {
      // Test CORS
      const corsResult = await testCORS()
      setCorsStatus(corsResult)
      
      // Get health status
      if (corsResult) {
        const health = await checkAPIHealth()
        setHealthStatus(health)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
      setCorsStatus(false)
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    if (showDetails) {
      runTests()
    }
  }, [showDetails])

  if (!showDetails) {
    return (
      <Button 
        onClick={runTests} 
        disabled={isLoading}
        variant="outline"
        size="sm"
      >
        {isLoading ? 'Testing...' : 'Test CORS'}
      </Button>
    )
  }

  const envInfo = getEnvironmentInfo()

  return (
    <Card className="w-full max-w-2xl">
      <CardHeader>
        <CardTitle>CORS & API Configuration</CardTitle>
        <CardDescription>
          Test CORS configuration and API connectivity
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <Button 
          onClick={runTests} 
          disabled={isLoading}
          className="w-full"
        >
          {isLoading ? 'Testing...' : 'Run Tests'}
        </Button>

        {error && (
          <div className="p-3 bg-red-50 border border-red-200 rounded-md">
            <p className="text-red-700 text-sm">{error}</p>
          </div>
        )}

        {corsStatus !== null && (
          <div className={`p-3 border rounded-md ${
            corsStatus 
              ? 'bg-green-50 border-green-200' 
              : 'bg-red-50 border-red-200'
          }`}>
            <p className={`text-sm font-medium ${
              corsStatus ? 'text-green-700' : 'text-red-700'
            }`}>
              CORS Status: {corsStatus ? 'Working' : 'Failed'}
            </p>
          </div>
        )}

        {healthStatus && (
          <div className="p-3 bg-blue-50 border border-blue-200 rounded-md">
            <h4 className="text-sm font-medium text-blue-700 mb-2">API Health</h4>
            <div className="text-xs text-blue-600 space-y-1">
              <p>Status: {healthStatus.status}</p>
              <p>OpenAI Configured: {healthStatus.openai_api_key_configured ? 'Yes' : 'No'}</p>
              <p>Timestamp: {healthStatus.timestamp}</p>
            </div>
          </div>
        )}

        <div className="p-3 bg-gray-50 border border-gray-200 rounded-md">
          <h4 className="text-sm font-medium text-gray-700 mb-2">Environment</h4>
          <div className="text-xs text-gray-600 space-y-1">
            <p>API URL: {envInfo.apiUrl}</p>
            <p>Environment: {envInfo.environment}</p>
            <p>CORS Logging: {envInfo.corsLogging}</p>
            <p>Debug Mode: {envInfo.debugMode}</p>
            <p>Request Logging: {envInfo.requestLogging}</p>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

export default CORSTest
