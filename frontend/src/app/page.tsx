'use client'

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { 
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { Textarea } from '@/components/ui/textarea'
import { FileAttachment } from '@/components/FileAttachment'
import { fetchAvailableTemplates, fetchProposalTemplate, fetchAvailableModels, type TemplateListItem, type ProposalTemplate, type AIModel } from '@/lib/api'

interface AttachmentData {
  id: string
  type: 'file' | 'url'
  name: string
  content?: string
  status: 'uploading' | 'processing' | 'ready' | 'error'
  error?: string
}

interface Section {
  title: string
  questions: string
  best_practice_beispiele: string[]
  user_input: string
  max_section_length: number
  attached_files?: string[]
  attached_urls?: string[]
  attachment_summaries?: string[]
}

interface ProposalData {
  sections: Record<string, Section>
}

interface SectionResponse {
  title: string
  generated_content: string
  user_input: string
  status: string
}

interface GenerationResponse {
  sections: Record<string, SectionResponse>
  status: string
}

export default function ProposalGenerator() {
  const [proposalData, setProposalData] = useState<ProposalData | null>(null)
  const [userInputs, setUserInputs] = useState<Record<string, string>>({})
  const [attachments, setAttachments] = useState<Record<string, AttachmentData[]>>({})
  const [generatedContent, setGeneratedContent] = useState<Record<string, string>>({})
  const [selectedProposal, setSelectedProposal] = useState<string>('')
  const [availableProposals, setAvailableProposals] = useState<TemplateListItem[]>([])
  const [availableModels, setAvailableModels] = useState<AIModel[]>([])
  const [selectedModel, setSelectedModel] = useState<string>('gpt-4o-mini')
  const [isLoading, setIsLoading] = useState(false)
  const [isGenerating, setIsGenerating] = useState(false)

  // Load available templates and models on component mount
  useEffect(() => {
    loadAvailableTemplates()
    loadAvailableModels()
  }, [])

  // Load proposal data when a template is selected
  useEffect(() => {
    if (selectedProposal) {
      loadProposalData(selectedProposal)
    }
  }, [selectedProposal])

  const loadAvailableTemplates = async () => {
    try {
      const templates = await fetchAvailableTemplates()
      setAvailableProposals(templates)
    } catch (error) {
      console.error('Fehler beim Laden der verfügbaren Templates:', error)
    }
  }

  const loadAvailableModels = async () => {
    try {
      const response = await fetchAvailableModels()
      setAvailableModels(response.models)
      setSelectedModel(response.default)
    } catch (error) {
      console.error('Fehler beim Laden der verfügbaren Modelle:', error)
    }
  }

  const loadProposalData = async (templateId: string) => {
    setIsLoading(true)
    try {
      const template = await fetchProposalTemplate(templateId)
      setProposalData(template)
      
      // Initialize user inputs and attachments
      const initialInputs: Record<string, string> = {}
      const initialAttachments: Record<string, AttachmentData[]> = {}
      Object.keys(template.sections).forEach(key => {
        initialInputs[key] = ''
        initialAttachments[key] = []
      })
      setUserInputs(initialInputs)
      setAttachments(initialAttachments)
    } catch (error) {
      console.error('Fehler beim Laden der Antragsdaten:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleInputChange = (sectionKey: string, value: string) => {
    setUserInputs(prev => ({
      ...prev,
      [sectionKey]: value
    }))
  }

  const handleAttachmentsChange = (sectionKey: string, sectionAttachments: AttachmentData[]) => {
    setAttachments(prev => ({
      ...prev,
      [sectionKey]: sectionAttachments
    }))
  }

  const generateProposal = async () => {
    if (!proposalData) return

    setIsGenerating(true)
    try {
      // Prepare the payload for the FastAPI backend
      const payload = {
        model: selectedModel,
        sections: Object.entries(proposalData.sections).reduce((acc, [key, section]) => {
          const sectionAttachments = attachments[key] || []
          acc[key] = {
            ...section,
            user_input: userInputs[key] || '',
            attached_files: sectionAttachments
              .filter(att => att.type === 'file' && att.status === 'ready')
              .map(att => att.id),
            attached_urls: sectionAttachments
              .filter(att => att.type === 'url' && att.status === 'ready')
              .map(att => att.name) // Use the original URL as the value
          }
          return acc
        }, {} as Record<string, Section>)
      }

      const response = await fetch('http://localhost:8000/api/v1/generate-sections', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload)
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const result: GenerationResponse = await response.json()
      
      // Extract generated content
      const generated: Record<string, string> = {}
      Object.entries(result.sections).forEach(([key, section]) => {
        generated[key] = section.generated_content
      })
      
      setGeneratedContent(generated)
    } catch (error) {
      console.error('Fehler beim Generieren des Antrags:', error)
      alert('Fehler beim Generieren des Antrags. Bitte stellen Sie sicher, dass das Backend erreichbar ist.')
    } finally {
      setIsGenerating(false)
    }
  }

  const downloadResults = () => {
    if (!proposalData || Object.keys(generatedContent).length === 0) {
      alert('Es gibt keine generierten Inhalte zum Herunterladen.')
      return
    }

    // Create the text content
    let textContent = `Generierte Antragsinhalte\n`
    textContent += `=================================\n\n`
    textContent += `Erstellt am: ${new Date().toLocaleDateString('de-DE')}\n`
    textContent += `KI-Modell: ${availableModels.find(model => model.id === selectedModel)?.name || selectedModel}\n\n`

    Object.entries(proposalData.sections).forEach(([sectionKey, section]) => {
      if (generatedContent[sectionKey]) {
        textContent += `${section.title}\n`
        textContent += `${'-'.repeat(section.title.length)}\n\n`
        textContent += `${generatedContent[sectionKey]}\n\n\n`
      }
    })

    // Create and download the file
    const blob = new Blob([textContent], { type: 'text/plain;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `antrag-${selectedProposal}-${new Date().toISOString().split('T')[0]}.txt`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
  }

  return (
    <div className="container mx-auto p-6 max-w-4xl">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-4">KI-Antragsgenerator</h1>
        <p className="text-gray-600 mb-6">
          Wählen Sie eine Antragsvorlage und geben Sie Ihre Informationen ein, um professionelle Inhalte mit KI zu generieren.
        </p>

        <Card className="mb-6">
          <CardHeader>
            <CardTitle>Antragsvorlage auswählen</CardTitle>
            <CardDescription>Wählen Sie, welche Art von Antrag Sie generieren möchten</CardDescription>
          </CardHeader>
          <CardContent>
            <Select value={selectedProposal} onValueChange={setSelectedProposal}>
              <SelectTrigger className="w-full">
                <SelectValue placeholder="Wählen Sie eine Antragsvorlage..." />
              </SelectTrigger>
              <SelectContent>
                {availableProposals.map((proposal) => (
                  <SelectItem key={proposal.id} value={proposal.id}>
                    {proposal.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </CardContent>
        </Card>
      </div>

      {isLoading && (
        <div className="text-center py-8">
          <p>Antragsvorlage wird geladen...</p>
        </div>
      )}

      {proposalData && (
        <div className="space-y-6">
          {Object.entries(proposalData.sections).map(([sectionKey, section]) => (
            <Card key={sectionKey}>
              <CardHeader>
                <CardTitle>{section.title}</CardTitle>
                <CardDescription className="whitespace-pre-wrap">
                  {section.questions}
                </CardDescription>
                {section.max_section_length > 0 && (
                  <div className="text-sm text-muted-foreground mt-2">
                    Maximale Zeichenlänge: {section.max_section_length.toLocaleString()} Zeichen
                  </div>
                )}
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <label htmlFor={`input-${sectionKey}`} className="block text-sm font-medium mb-2">
                    Ihre Eingabe:
                  </label>
                  <Textarea
                    id={`input-${sectionKey}`}
                    placeholder="Geben Sie hier Ihre Antworten ein..."
                    value={userInputs[sectionKey] || ''}
                    onChange={(e) => handleInputChange(sectionKey, e.target.value)}
                    className="min-h-[100px]"
                  />
                </div>

                {/* File Attachment Component */}
                <FileAttachment
                  onAttachmentsChange={(sectionAttachments) => handleAttachmentsChange(sectionKey, sectionAttachments)}
                  initialAttachments={attachments[sectionKey] || []}
                  disabled={isGenerating}
                />
                
                {generatedContent[sectionKey] && (
                  <div>
                    <label className="block text-sm font-medium mb-2 text-green-700">
                      Generierter Abschnitt:
                    </label>
                    <div className="p-4 bg-green-50 border border-green-200 rounded-md">
                      <p className="whitespace-pre-wrap">{generatedContent[sectionKey]}</p>
                    </div>
                    <div className="mt-2 text-sm text-muted-foreground">
                      <span className="font-medium">Zeichenanzahl:</span> {generatedContent[sectionKey].length.toLocaleString()}
                      {section.max_section_length > 0 && (
                        <span className={`ml-2 ${generatedContent[sectionKey].length > section.max_section_length ? 'text-red-600' : 'text-green-600'}`}>
                          / {section.max_section_length.toLocaleString()} max
                          {generatedContent[sectionKey].length > section.max_section_length && 
                            ` (${(generatedContent[sectionKey].length - section.max_section_length).toLocaleString()} Zeichen über dem Limit)`
                          }
                        </span>
                      )}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          ))}

          <div className="flex items-center justify-center gap-6 pt-6">
            
            {/* Action Buttons */}
            <div className="flex flex-col gap-2">
              <div className="flex gap-3">
                <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="outline" className="w-64 justify-between">
                    {availableModels.find(model => model.id === selectedModel)?.name || 'Modell auswählen'}
                    <svg
                      className="h-4 w-4 opacity-50"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                      xmlns="http://www.w3.org/2000/svg"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M19 9l-7 7-7-7"
                      />
                    </svg>
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent className="w-64">
                  {availableModels.map((model) => (
                    <DropdownMenuItem
                      key={model.id}
                      onClick={() => setSelectedModel(model.id)}
                      className="cursor-pointer"
                    >
                      <div className="flex flex-col items-center text-center w-full">
                        <span className="font-medium">{model.name}</span>
                        <span className="text-xs text-gray-500">{model.provider}</span>
                      </div>
                    </DropdownMenuItem>
                  ))}
                </DropdownMenuContent>
              </DropdownMenu>
                <Button 
                  onClick={generateProposal} 
                  disabled={isGenerating || (
                    Object.values(userInputs).every(input => !input.trim()) && 
                    Object.values(attachments).every(sectionAttachments => 
                      sectionAttachments.filter(att => att.status === 'ready').length === 0
                    )
                  )}
                  className="px-8 py-2"
                >
                  {isGenerating ? 'Generiere...' : 'Antragsinhalte generieren'}
                </Button>
                <Button
                  onClick={downloadResults}
                  disabled={Object.keys(generatedContent).length === 0}
                  variant="outline"
                  className="px-6 py-2"
                >
                  <svg
                    className="h-4 w-4 mr-2"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                    xmlns="http://www.w3.org/2000/svg"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                    />
                  </svg>
                  Download
                </Button>
              </div>
            </div>
          </div>

          {isGenerating && (
            <div className="text-center py-4">
              <p className="text-gray-600">Inhalte werden mit KI generiert... Dies kann einen Moment dauern.</p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
