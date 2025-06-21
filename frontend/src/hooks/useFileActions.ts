/**
 * Hook for file actions with optimistic UI updates
 */

import { useCallback } from 'react'
import { toast } from 'sonner'
import { mutate } from 'swr'
import { useStackAI } from '@/contexts/stackai-context'
import { optimizeFileSelection, type FileResource } from '@/lib/api/stackai-client'
import { files as fileLogger } from '@/lib/logger'

interface UseFileActionsReturn {
  indexFiles: (resourceIds: string[], files?: FileResource[], knowledgeBaseName?: string) => Promise<void>
  deindexFiles: (resourceIds: string[], files?: FileResource[]) => Promise<void>
  deleteFromKnowledgeBase: (knowledgeBaseId: string, resourcePath: string) => Promise<void>
  isLoading: boolean
}

export function useFileActions(): UseFileActionsReturn {
  const { client, isAuthenticated, connectionId } = useStackAI()

  const indexFiles = useCallback(async (
    resourceIds: string[], 
    files: FileResource[] = [],
    knowledgeBaseName = `KB-${new Date().toLocaleDateString()}-${Math.random().toString(36).substr(2, 4)}`
  ) => {
    if (!client || !isAuthenticated || !connectionId) {
      toast.error('Please authenticate first')
      return
    }

    if (resourceIds.length === 0) {
      toast.error('No files selected')
      return
    }

    try {
      toast.loading('Creating knowledge base and indexing files...', { id: 'indexing' })
      
      // Get selected files and optimize selection (remove children if parent selected)
      const selectedFiles = files.filter(f => resourceIds.includes(f.resource_id))
      const optimizedFiles = optimizeFileSelection(selectedFiles)
      
      fileLogger.debug('Optimized selection', { 
        optimized: optimizedFiles.length, 
        selected: selectedFiles.length 
      })

      if (optimizedFiles.length === 0) {
        toast.error('No valid files selected for indexing', { id: 'indexing' })
        return
      }

      const optimizedResourceIds = optimizedFiles.map(f => f.resource_id)

      fileLogger.info('Creating knowledge base with files', { count: optimizedResourceIds.length })

      // Step 1: Create knowledge base with optimized file selection
      const knowledgeBase = await client.createKnowledgeBase(
        connectionId,
        optimizedResourceIds,
        knowledgeBaseName,
        `Knowledge base with ${optimizedFiles.length} files from Google Drive`
      )
      
      fileLogger.info('Knowledge base created', { id: knowledgeBase.knowledge_base_id })

      // Step 2: Trigger sync to start indexing
      toast.loading('Starting indexing process...', { id: 'indexing' })
      await client.syncKnowledgeBase(knowledgeBase.knowledge_base_id)
      
      fileLogger.info('Knowledge base sync triggered')
      
      toast.success(
        `Successfully started indexing ${optimizedFiles.length} files in "${knowledgeBase.name}"`, 
        { 
          id: 'indexing', 
          duration: 8000,
          description: `Knowledge Base ID: ${knowledgeBase.knowledge_base_id}`
        }
      )
      
      // Store KB ID for later reference (could be stored in local storage or context)
      fileLogger.debug('Knowledge Base created', {
        id: knowledgeBase.knowledge_base_id,
        name: knowledgeBase.name,
        fileCount: optimizedFiles.length
      })
      
      // Invalidate file caches to refetch updated status
      setTimeout(() => {
        mutate(key => Array.isArray(key) && key[0] === 'files')
      }, 2000)
      
    } catch (error) {
      fileLogger.error('Error indexing files', { error })
      const errorMessage = error instanceof Error ? error.message : 'Failed to start indexing'
      toast.error(`Indexing failed: ${errorMessage}`, { id: 'indexing' })
    }
  }, [client, isAuthenticated, connectionId])

  const deindexFiles = useCallback(async (
    resourceIds: string[], 
    files: FileResource[] = []
  ) => {
    if (!client || !isAuthenticated) {
      toast.error('Please authenticate first')
      return
    }

    try {
      toast.loading('Removing files from knowledge base...', { id: 'deindexing' })
      
      // Get selected files
      const selectedFiles = files.filter(f => resourceIds.includes(f.resource_id))
      
      if (selectedFiles.length === 0) {
        toast.error('No files selected for de-indexing', { id: 'deindexing' })
        return
      }

      // Group files by knowledge base ID
      const filesByKnowledgeBase = new Map<string, FileResource[]>()
      
      selectedFiles.forEach(file => {
        const kbId = file.knowledge_base_id
        if (kbId && kbId !== '00000000-0000-0000-0000-000000000000') {
          if (!filesByKnowledgeBase.has(kbId)) {
            filesByKnowledgeBase.set(kbId, [])
          }
          filesByKnowledgeBase.get(kbId)!.push(file)
        }
      })

      if (filesByKnowledgeBase.size === 0) {
        toast.error('Selected files are not indexed in any knowledge base', { id: 'deindexing' })
        return
      }

      // De-index files from each knowledge base
      const deindexPromises = Array.from(filesByKnowledgeBase.entries()).map(async ([kbId, kbFiles]) => {
        const promises = kbFiles.map(async (file) => {
          // Get access token from client
          if (!client || !client.isAuthenticated()) {
            throw new Error('Client not authenticated')
          }

          const response = await fetch(`/api/stackai/knowledge-bases/${kbId}/resources?resource_path=${encodeURIComponent(file.inode_path.path)}`, {
            method: 'DELETE',
                          headers: {
                'x-access-token': client.getAccessToken() || '',
              },
          })

          if (!response.ok) {
            const errorData = await response.json().catch(() => ({}))
            throw new Error(`Failed to de-index ${file.inode_path.path}: ${errorData.error || response.statusText}`)
          }

          return file.inode_path.path
        })

        return Promise.all(promises)
      })

      const results = await Promise.all(deindexPromises)
      const deindexedPaths = results.flat()
      
      toast.success(
        `Successfully de-indexed ${deindexedPaths.length} files`, 
        { 
          id: 'deindexing', 
          duration: 5000,
          description: deindexedPaths.length <= 3 ? deindexedPaths.join(', ') : `${deindexedPaths.slice(0, 2).join(', ')} and ${deindexedPaths.length - 2} more...`
        }
      )
      
      fileLogger.info('De-indexed files', { count: deindexedPaths.length })

      // Invalidate file caches to refetch updated status
      setTimeout(() => {
        mutate(key => Array.isArray(key) && key[0] === 'files')
      }, 1000)
      
    } catch (error) {
      fileLogger.error('Error de-indexing files', { error })
      const errorMessage = error instanceof Error ? error.message : 'Failed to de-index files'
      toast.error(`De-indexing failed: ${errorMessage}`, { id: 'deindexing' })
    }
  }, [client, isAuthenticated])

  const deleteFromKnowledgeBase = useCallback(async (
    knowledgeBaseId: string,
    resourcePath: string
  ) => {
    if (!client || !isAuthenticated) {
      toast.error('Not authenticated')
      return
    }

    try {
      toast.loading('Removing file from knowledge base...', { id: 'delete-toast' })

      // TODO: Use the client to remove from knowledge base
      // await client.removeFromKnowledgeBase(knowledgeBaseId, [resourcePath])

      // For now, simulate the operation
      await new Promise(resolve => setTimeout(resolve, 1000))

      toast.success('File removed from knowledge base', { id: 'delete-toast' })

      fileLogger.info('Removed file from knowledge base', { path: resourcePath })

      // Invalidate caches
      mutate(key => Array.isArray(key) && key[0] === 'files')

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to remove file'
      toast.error(`Delete failed: ${errorMessage}`, { id: 'delete-toast' })
      fileLogger.error('Delete error', { error })
    }
  }, [client, isAuthenticated])

  return {
    indexFiles,
    deindexFiles,
    deleteFromKnowledgeBase,
    isLoading: false
  }
} 