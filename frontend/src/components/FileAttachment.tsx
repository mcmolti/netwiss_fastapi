/**
 * File attachment component for proposal forms.
 * 
 * Provides functionality to upload PDF files and add URL links,
 * with preview of extracted content and management of attachments.
 */

'use client'

import React, { useState, useCallback } from 'react'
import { Button } from './ui/button'
import { Input } from './ui/input'
import { Card } from './ui/card'
import { uploadFile, extractURLContent, deleteFile, FileUploadResponse, URLContentResponse } from '../lib/api'

interface AttachmentData {
  id: string
  type: 'file' | 'url'
  name: string
  content?: string
  status: 'uploading' | 'processing' | 'ready' | 'error'
  error?: string
}

interface FileAttachmentProps {
  onAttachmentsChange: (attachments: AttachmentData[]) => void
  initialAttachments?: AttachmentData[]
  disabled?: boolean
}

export function FileAttachment({ onAttachmentsChange, initialAttachments = [], disabled = false }: FileAttachmentProps) {
  const [attachments, setAttachments] = useState<AttachmentData[]>(initialAttachments)
  const [urlInput, setUrlInput] = useState('')
  const [isProcessing, setIsProcessing] = useState(false)

  const updateAttachments = useCallback((newAttachments: AttachmentData[]) => {
    setAttachments(newAttachments)
    onAttachmentsChange(newAttachments)
  }, [onAttachmentsChange])

  const handleFileUpload = useCallback(async (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files
    if (!files || files.length === 0) return

    const file = files[0]
    
    // Validate file type
    if (!file.type.includes('pdf')) {
      alert('Nur PDF-Dateien sind erlaubt.')
      return
    }

    // Validate file size (10MB limit)
    if (file.size > 10 * 1024 * 1024) {
      alert('Datei ist zu groß. Maximum: 10MB')
      return
    }

    const tempId = `file_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    const newAttachment: AttachmentData = {
      id: tempId,
      type: 'file',
      name: file.name,
      status: 'uploading'
    }

    const updatedAttachments = [...attachments, newAttachment]
    updateAttachments(updatedAttachments)

    try {
      setIsProcessing(true)
      const response: FileUploadResponse = await uploadFile(file)
      
      const processedAttachment: AttachmentData = {
        id: response.file_id,
        type: 'file',
        name: response.filename,
        content: response.extracted_text,
        status: 'ready'
      }

      const finalAttachments = updatedAttachments.map(att => 
        att.id === tempId ? processedAttachment : att
      )
      updateAttachments(finalAttachments)

    } catch (error) {
      const errorAttachment: AttachmentData = {
        ...newAttachment,
        status: 'error',
        error: error instanceof Error ? error.message : 'Fehler beim Upload'
      }

      const finalAttachments = updatedAttachments.map(att => 
        att.id === tempId ? errorAttachment : att
      )
      updateAttachments(finalAttachments)
    } finally {
      setIsProcessing(false)
      // Reset file input
      event.target.value = ''
    }
  }, [attachments, updateAttachments])

  const handleUrlSubmit = useCallback(async () => {
    if (!urlInput.trim()) return

    // Basic URL validation
    try {
      new URL(urlInput)
    } catch {
      alert('Bitte geben Sie eine gültige URL ein.')
      return
    }

    const tempId = `url_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    const newAttachment: AttachmentData = {
      id: tempId,
      type: 'url',
      name: urlInput,
      status: 'processing'
    }

    const updatedAttachments = [...attachments, newAttachment]
    updateAttachments(updatedAttachments)

    try {
      setIsProcessing(true)
      const response: URLContentResponse = await extractURLContent(urlInput)
      
      const processedAttachment: AttachmentData = {
        id: `url_${Date.now()}`,
        type: 'url',
        name: response.title || urlInput,
        content: response.content,
        status: response.status === 'success' ? 'ready' : 'error',
        error: response.status !== 'success' ? 'Fehler beim Laden der URL' : undefined
      }

      const finalAttachments = updatedAttachments.map(att => 
        att.id === tempId ? processedAttachment : att
      )
      updateAttachments(finalAttachments)

    } catch (error) {
      const errorAttachment: AttachmentData = {
        ...newAttachment,
        status: 'error',
        error: error instanceof Error ? error.message : 'Fehler beim Laden der URL'
      }

      const finalAttachments = updatedAttachments.map(att => 
        att.id === tempId ? errorAttachment : att
      )
      updateAttachments(finalAttachments)
    } finally {
      setIsProcessing(false)
      setUrlInput('')
    }
  }, [urlInput, attachments, updateAttachments])

  const handleRemoveAttachment = useCallback(async (attachmentId: string) => {
    const attachment = attachments.find(att => att.id === attachmentId)
    
    // Delete file from server if it's a file attachment
    if (attachment?.type === 'file' && attachment.status === 'ready') {
      try {
        await deleteFile(attachmentId)
      } catch (error) {
        console.error('Error deleting file:', error)
        // Continue with removal from UI even if server deletion fails
      }
    }

    const updatedAttachments = attachments.filter(att => att.id !== attachmentId)
    updateAttachments(updatedAttachments)
  }, [attachments, updateAttachments])

  const getStatusText = (status: AttachmentData['status']) => {
    switch (status) {
      case 'uploading': return 'Wird hochgeladen...'
      case 'processing': return 'Wird verarbeitet...'
      case 'ready': return 'Bereit'
      case 'error': return 'Fehler'
      default: return ''
    }
  }

  const getStatusColor = (status: AttachmentData['status']) => {
    switch (status) {
      case 'uploading':
      case 'processing': return 'text-blue-600'
      case 'ready': return 'text-green-600'
      case 'error': return 'text-red-600'
      default: return 'text-gray-600'
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-col space-y-2">
        <label className="text-sm font-medium">Anhänge</label>
        <div className="flex flex-col space-y-2">
          {/* File Upload */}
          <div className="flex items-center space-x-2">
            <input
              type="file"
              accept=".pdf"
              onChange={handleFileUpload}
              disabled={disabled || isProcessing}
              className="flex-1 text-sm file:mr-2 file:py-1 file:px-2 file:rounded file:border-0 file:text-sm file:bg-gray-50 file:text-gray-700 hover:file:bg-gray-100"
            />
          </div>
          
          {/* URL Input */}
          <div className="flex items-center space-x-2">
            <Input
              type="url"
              placeholder="URL eingeben (z.B. https://example.com)"
              value={urlInput}
              onChange={(e) => setUrlInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleUrlSubmit()}
              disabled={disabled || isProcessing}
              className="flex-1"
            />
            <Button
              type="button"
              onClick={handleUrlSubmit}
              disabled={disabled || isProcessing || !urlInput.trim()}
              variant="outline"
              size="sm"
            >
              Hinzufügen
            </Button>
          </div>
        </div>
      </div>

      {/* Attachments List */}
      {attachments.length > 0 && (
        <div className="space-y-2">
          <label className="text-sm font-medium">Hinzugefügte Anhänge:</label>
          {attachments.map((attachment) => (
            <Card key={attachment.id} className="p-3">
              <div className="flex items-start justify-between">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center space-x-2">
                    <span className="text-sm font-medium truncate">
                      {attachment.type === 'file' ? '📄' : '🔗'} {attachment.name}
                    </span>
                    <span className={`text-xs ${getStatusColor(attachment.status)}`}>
                      {getStatusText(attachment.status)}
                    </span>
                  </div>
                  
                  {attachment.error && (
                    <p className="text-xs text-red-600 mt-1">{attachment.error}</p>
                  )}
                  
                  {attachment.content && attachment.status === 'ready' && (
                    <div className="mt-2">
                      <details className="text-xs">
                        <summary className="cursor-pointer text-gray-600 hover:text-gray-800">
                          Extrahierter Inhalt anzeigen
                        </summary>
                        <div className="mt-1 p-2 bg-gray-50 rounded max-h-32 overflow-y-auto">
                          {attachment.content.substring(0, 500)}
                          {attachment.content.length > 500 && '...'}
                        </div>
                      </details>
                    </div>
                  )}
                </div>
                
                <Button
                  type="button"
                  onClick={() => handleRemoveAttachment(attachment.id)}
                  disabled={disabled}
                  variant="ghost"
                  size="sm"
                  className="ml-2 text-red-600 hover:text-red-800"
                >
                  ✕
                </Button>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
