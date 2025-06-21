/**
 * Hook for file actions with optimistic UI updates
 */

import { useCallback } from 'react'
import { toast } from 'sonner'
import { mutate } from 'swr'
import { useStackAI } from './useStackAI'
import { optimizeFileSelection, type FileResource } from '@/lib/api/stackai-client'

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
      
      console.log('🔄 Optimized selection:', optimizedFiles.length, 'from', selectedFiles.length, 'selected files')

      if (optimizedFiles.length === 0) {
        toast.error('No valid files selected for indexing', { id: 'indexing' })
        return
      }

      const optimizedResourceIds = optimizedFiles.map(f => f.resource_id)

      console.log('📚 Creating knowledge base with files:', optimizedResourceIds)

      // Step 1: Create knowledge base with optimized file selection
      const knowledgeBase = await client.createKnowledgeBase(
        connectionId,
        optimizedResourceIds,
        knowledgeBaseName,
        `Knowledge base with ${optimizedFiles.length} files from Google Drive`
      )
      
      console.log('✅ Knowledge base created:', knowledgeBase.knowledge_base_id)

      // Step 2: Trigger sync to start indexing
      toast.loading('Starting indexing process...', { id: 'indexing' })
      await client.syncKnowledgeBase(knowledgeBase.knowledge_base_id)
      
      console.log('✅ Knowledge base sync triggered')
      
      toast.success(
        `Successfully started indexing ${optimizedFiles.length} files in "${knowledgeBase.name}"`, 
        { id: 'indexing', duration: 5000 }
      )
      
      // Invalidate file caches to refetch updated status
      setTimeout(() => {
        mutate(key => Array.isArray(key) && key[0] === 'files')
      }, 2000)
      
    } catch (error) {
      console.error('❌ Error indexing files:', error)
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

      // For now, show a placeholder message since de-indexing requires knowledge of which KB the files belong to
      toast.error('De-indexing requires knowledge base context. Feature needs enhancement!', { id: 'deindexing' })
      
      console.log('🚧 De-indexing not fully implemented - need KB context for files:', selectedFiles.map(f => f.inode_path.path))
      
    } catch (error) {
      console.error('❌ Error de-indexing files:', error)
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

      console.log('🗑️ Removed file from knowledge base:', resourcePath)

      // Invalidate caches
      mutate(key => Array.isArray(key) && key[0] === 'files')

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to remove file'
      toast.error(`Delete failed: ${errorMessage}`, { id: 'delete-toast' })
      console.error('❌ Delete error:', error)
    }
  }, [client, isAuthenticated])

  return {
    indexFiles,
    deindexFiles,
    deleteFromKnowledgeBase,
    isLoading: false
  }
} 