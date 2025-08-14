/**
 * API utility functions for the proposal generator.
 */

const API_BASE_URL = 'http://localhost:8000/api/v1'

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

/**
 * Fetch available proposal templates.
 */
export async function fetchAvailableTemplates(): Promise<TemplateListItem[]> {
  const response = await fetch(`${API_BASE_URL}/templates/`)
  
  if (!response.ok) {
    throw new Error(`Failed to fetch templates: ${response.status}`)
  }
  
  return response.json()
}

/**
 * Fetch a specific proposal template.
 */
export async function fetchProposalTemplate(templateId: string): Promise<ProposalTemplate> {
  const response = await fetch(`${API_BASE_URL}/templates/${templateId}`)
  
  if (!response.ok) {
    throw new Error(`Failed to fetch template ${templateId}: ${response.status}`)
  }
  
  return response.json()
}

/**
 * Fetch available AI models for proposal generation.
 */
export async function fetchAvailableModels(): Promise<AvailableModelsResponse> {
  const response = await fetch(`${API_BASE_URL}/models`)
  
  if (!response.ok) {
    throw new Error(`Failed to fetch available models: ${response.status}`)
  }
  
  return response.json()
}

/**
 * Upload a PDF file and extract its content.
 */
export async function uploadFile(file: File): Promise<FileUploadResponse> {
  const formData = new FormData()
  formData.append('file', file)
  
  const response = await fetch(`${API_BASE_URL.replace('/v1', '')}/files/upload`, {
    method: 'POST',
    body: formData,
  })
  
  if (!response.ok) {
    throw new Error(`Failed to upload file: ${response.status}`)
  }
  
  return response.json()
}

/**
 * Extract content from a URL.
 */
export async function extractURLContent(url: string): Promise<URLContentResponse> {
  const response = await fetch(`${API_BASE_URL.replace('/v1', '')}/urls/extract`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ url: url }),
  })
  
  if (!response.ok) {
    throw new Error(`Failed to extract URL content: ${response.status}`)
  }
  
  return response.json()
}

/**
 * Delete an uploaded file.
 */
export async function deleteFile(fileId: string): Promise<void> {
  const response = await fetch(`${API_BASE_URL.replace('/v1', '')}/files/${fileId}`, {
    method: 'DELETE',
  })
  
  if (!response.ok) {
    throw new Error(`Failed to delete file: ${response.status}`)
  }
}
