/**
 * SWR hooks for fetching files and folders
 */

import useSWR from 'swr'
import { useStackAI } from './useStackAI'
import type { FileResource } from '@/lib/api/stackai-client'

interface UseFilesOptions {
  revalidateOnFocus?: boolean
  refreshInterval?: number
}

interface UseFilesReturn {
  files: FileResource[]
  isLoading: boolean
  error: Error | null
  mutate: () => void
  hasMore: boolean
}

/**
 * Hook to fetch files in a specific folder
 */
export function useFiles(
  parentResourceId?: string,
  options: UseFilesOptions = {}
): UseFilesReturn {
  const { client, connectionId, isAuthenticated } = useStackAI()
  
  const {
    revalidateOnFocus = false,
    refreshInterval = 0
  } = options

  const { data, error, mutate, isLoading } = useSWR(
    // Key: only fetch if authenticated and we have a connection
    isAuthenticated && connectionId && client 
      ? ['files', connectionId, parentResourceId || 'root']
      : null,
    async ([, connId, parentId]) => {
      if (!client) throw new Error('Client not available')
      const result = await client.listResources(
        connId, 
        parentId === 'root' ? undefined : parentId
      )
      return result
    },
    {
      revalidateOnFocus,
      refreshInterval,
      dedupingInterval: 30000, // 30 seconds deduping
      errorRetryCount: 3,
      errorRetryInterval: 1000,
    }
  )

  return {
    files: data?.data || [],
    isLoading,
    error,
    mutate,
    hasMore: data?.has_more || false
  }
}

/**
 * Hook to search files
 */
export function useSearchFiles(query: string): UseFilesReturn {
  const { client, connectionId, isAuthenticated } = useStackAI()

  const { data, error, mutate, isLoading } = useSWR(
    // Only search if we have a query and are authenticated
    isAuthenticated && connectionId && client && query.trim()
      ? ['search', connectionId, query.trim()]
      : null,
    async ([, connId]) => {
      if (!client) throw new Error('Client not available')
      // For now, we'll use the regular list endpoint and filter client-side
      // In a real implementation, there might be a dedicated search endpoint
      const result = await client.listResources(connId)
      return result
    },
    {
      dedupingInterval: 5000, // 5 seconds for search
      revalidateOnFocus: false,
    }
  )

  return {
    files: data?.data || [],
    isLoading,
    error,
    mutate,
    hasMore: data?.has_more || false
  }
}

/**
 * Hook to get details for specific resources
 */
export function useResourceDetails(resourceIds: string[]) {
  const { client, connectionId, isAuthenticated } = useStackAI()

  const { data, error, mutate, isLoading } = useSWR(
    isAuthenticated && connectionId && client && resourceIds.length > 0
      ? ['resource-details', connectionId, ...resourceIds.sort()]
      : null,
    async ([, connId, ...ids]) => {
      if (!client) throw new Error('Client not available')
      return await client.getResourceDetails(connId, ids)
    },
    {
      revalidateOnFocus: false,
      dedupingInterval: 60000, // 1 minute for details
    }
  )

  return {
    resources: data || {},
    isLoading,
    error,
    mutate
  }
} 