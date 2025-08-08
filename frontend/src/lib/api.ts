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
