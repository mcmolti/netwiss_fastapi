/**
 * API utility functions for the proposal generator.
 * Includes CORS handling, retry logic, and environment-specific configuration.
 */

// Environment and configuration
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'
const API_TIMEOUT = parseInt(process.env.NEXT_PUBLIC_API_TIMEOUT || '30000')
const API_RETRY_ATTEMPTS = parseInt(process.env.NEXT_PUBLIC_API_RETRY_ATTEMPTS || '3')
const API_RETRY_DELAY = parseInt(process.env.NEXT_PUBLIC_API_RETRY_DELAY || '1000')
const ENABLE_CORS_LOGGING = process.env.NEXT_PUBLIC_ENABLE_CORS_LOGGING === 'true'
const ENABLE_REQUEST_LOGGING = process.env.NEXT_PUBLIC_ENABLE_REQUEST_LOGGING === 'true'

// Export for use in other files
export { API_BASE_URL }

/**
 * Enhanced fetch wrapper with CORS handling, timeout, and retry logic
 */
class APIClient {
  private static instance: APIClient
  
  private constructor() {}
  
  static getInstance(): APIClient {
    if (!APIClient.instance) {
      APIClient.instance = new APIClient()
    }
    return APIClient.instance
  }
  
  /**
   * Make an API request with enhanced error handling and CORS support
   */
  async request<T>(
    endpoint: string, 
    options: RequestInit = {},
    retryCount = 0
  ): Promise<T> {
    const url = `${API_BASE_URL}${endpoint.startsWith('/') ? '' : '/'}${endpoint}`
    
    // Default headers for CORS and content type
    const defaultHeaders: HeadersInit = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      // Add CORS headers if needed
      'Access-Control-Request-Method': options.method || 'GET',
      'Access-Control-Request-Headers': 'Content-Type, Accept, Authorization',
    }
    
    // Merge headers
    const headers = {
      ...defaultHeaders,
      ...options.headers,
    }
    
    // Enhanced fetch options
    const fetchOptions: RequestInit = {
      ...options,
      headers,
      // Ensure credentials are included for CORS
      credentials: 'include',
      // Add mode for CORS
      mode: 'cors',
      // Add cache control
      cache: 'no-cache',
    }
    
    if (ENABLE_REQUEST_LOGGING) {
      console.log(`API Request: ${options.method || 'GET'} ${url}`, fetchOptions)
    }
    
    try {
      // Create abort controller for timeout
      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), API_TIMEOUT)
      
      const response = await fetch(url, {
        ...fetchOptions,
        signal: controller.signal,
      })
      
      clearTimeout(timeoutId)
      
      if (ENABLE_REQUEST_LOGGING) {
        console.log(`API Response: ${response.status} ${response.statusText}`, response)
      }
      
      // Handle CORS errors
      if (response.type === 'opaque') {
        throw new Error('CORS error: Request blocked by browser')
      }
      
      if (!response.ok) {
        // Handle specific HTTP errors
        if (response.status === 0) {
          throw new Error('Network error: Unable to connect to server')
        }
        
        let errorMessage = `HTTP ${response.status}: ${response.statusText}`
        try {
          const errorData = await response.json()
          errorMessage = errorData.detail || errorData.message || errorMessage
        } catch {
          // Response is not JSON, use default message
        }
        
        throw new Error(errorMessage)
      }
      
      // Handle empty responses
      const contentType = response.headers.get('content-type')
      if (!contentType || !contentType.includes('application/json')) {
        const text = await response.text()
        if (!text) {
          throw new Error('Empty response from server')
        }
        // Try to parse as JSON anyway
        try {
          return JSON.parse(text)
        } catch {
          throw new Error('Invalid JSON response from server')
        }
      }
      
      return await response.json()
      
    } catch (error) {
      if (ENABLE_CORS_LOGGING || ENABLE_REQUEST_LOGGING) {
        console.error(`API Error: ${url}`, error)
      }
      
      // Handle specific error types
      if (error instanceof Error) {
        // Timeout error
        if (error.name === 'AbortError') {
          throw new Error(`Request timeout after ${API_TIMEOUT}ms`)
        }
        
        // CORS or network errors - retry if possible
        if (
          (error.message.includes('CORS') || 
           error.message.includes('Network') ||
           error.message.includes('fetch')) &&
          retryCount < API_RETRY_ATTEMPTS
        ) {
          if (ENABLE_CORS_LOGGING) {
            console.warn(`Retrying request (attempt ${retryCount + 1}/${API_RETRY_ATTEMPTS})`)
          }
          
          // Wait before retrying
          await new Promise(resolve => setTimeout(resolve, API_RETRY_DELAY * (retryCount + 1)))
          return this.request<T>(endpoint, options, retryCount + 1)
        }
      }
      
      throw error
    }
  }
  
  /**
   * GET request
   */
  async get<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: 'GET' })
  }
  
  /**
   * POST request
   */
  async post<T>(endpoint: string, data?: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    })
  }
  
  /**
   * PUT request
   */
  async put<T>(endpoint: string, data?: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined,
    })
  }
  
  /**
   * DELETE request
   */
  async delete<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: 'DELETE' })
  }
}

// Create singleton instance
const apiClient = APIClient.getInstance()

export interface TemplateListItem {
  id: string
  name: string
  description?: string
}

export interface ProposalTemplate {
  sections: Record<string, {
    title: string
    questions: string
    best_practice_beispiele: string[]
    user_input: string
    max_section_length: number
    attached_files?: string[]
    attached_urls?: string[]
    attachment_summaries?: string[]
  }>
}

export interface AIModel {
  id: string
  name: string
  provider: string
  description: string
}

export interface AvailableModelsResponse {
  models: AIModel[]
  default: string
}

export interface FileUploadResponse {
  file_id: string
  filename: string
  size: number
  content_type: string
  extracted_text?: string
}

export interface URLContentResponse {
  url: string
  title?: string
  content: string
  status: string
}

export interface GenerationPayload {
  model: string
  sections: Record<string, {
    title: string
    questions: string
    best_practice_beispiele: string[]
    user_input: string
    max_section_length: number
    attached_files?: string[]
    attached_urls?: string[]
    attachment_summaries?: string[]
  }>
}

export interface GenerationResponse {
  sections: Record<string, {
    title: string
    generated_content: string
    user_input: string
    status: string
  }>
  status: string
}

/**
 * Fetch available proposal templates.
 */
export async function fetchAvailableTemplates(): Promise<TemplateListItem[]> {
  return apiClient.get<TemplateListItem[]>('/templates/')
}

/**
 * Fetch a specific proposal template.
 */
export async function fetchProposalTemplate(templateId: string): Promise<ProposalTemplate> {
  return apiClient.get<ProposalTemplate>(`/templates/${templateId}`)
}

/**
 * Fetch available AI models for proposal generation.
 */
export async function fetchAvailableModels(): Promise<AvailableModelsResponse> {
  return apiClient.get<AvailableModelsResponse>('/models')
}

/**
 * Upload a PDF file and extract its content.
 */
export async function uploadFile(file: File): Promise<FileUploadResponse> {
  const formData = new FormData()
  formData.append('file', file)
  
  // Use fetch directly for file uploads since we need FormData
  const response = await fetch(`${API_BASE_URL.replace('/v1', '')}/files/upload`, {
    method: 'POST',
    body: formData,
    credentials: 'include',
    mode: 'cors',
  })
  
  if (!response.ok) {
    const errorText = await response.text()
    throw new Error(`Failed to upload file: ${response.status} - ${errorText}`)
  }
  
  return response.json()
}

/**
 * Extract content from a URL.
 */
export async function extractURLContent(url: string): Promise<URLContentResponse> {
  return apiClient.post<URLContentResponse>('/urls/extract', { url: url })
}

/**
 * Delete an uploaded file.
 */
export async function deleteFile(fileId: string): Promise<void> {
  return apiClient.delete<void>(`/files/${fileId}`)
}

/**
 * Generate proposal sections.
 */
export async function generateProposalSections(payload: GenerationPayload): Promise<GenerationResponse> {
  return apiClient.post<GenerationResponse>('/generate-sections', payload)
}
