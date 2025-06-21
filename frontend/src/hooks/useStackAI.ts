/**
 * Hook for managing StackAI client instance and authentication
 */

import { useState, useEffect, useCallback } from 'react'
import { StackAIClient, getDefaultClient } from '@/lib/api/stackai-client'
import { toast } from 'sonner'

interface UseStackAIReturn {
  client: StackAIClient | null
  isAuthenticated: boolean
  isAuthenticating: boolean
  connectionId: string | null
  userEmail: string | null
  authenticate: () => Promise<void>
  error: string | null
}

interface GlobalState {
  isAuthenticated: boolean
  isAuthenticating: boolean
  connectionId: string | null
  userEmail: string | null
  error: string | null
  listeners: Set<(state: GlobalState) => void>
}

let globalClient: StackAIClient | null = null
let globalState: GlobalState = {
  isAuthenticated: false,
  isAuthenticating: false,
  connectionId: null,
  userEmail: null,
  error: null,
  listeners: new Set<(state: GlobalState) => void>()
}

// Prevent multiple concurrent authentications
let authPromise: Promise<void> | null = null

export function useStackAI(): UseStackAIReturn {
  const [state, setState] = useState({
    isAuthenticated: globalState.isAuthenticated,
    isAuthenticating: globalState.isAuthenticating,
    connectionId: globalState.connectionId,
    userEmail: globalState.userEmail,
    error: globalState.error
  })

  // Initialize client if not already done
  if (!globalClient) {
    globalClient = getDefaultClient()
  }

  // Subscribe to global state changes
  useEffect(() => {
    const listener = (newState: GlobalState) => {
      setState({
        isAuthenticated: newState.isAuthenticated,
        isAuthenticating: newState.isAuthenticating,
        connectionId: newState.connectionId,
        userEmail: newState.userEmail,
        error: newState.error
      })
    }
    
    globalState.listeners.add(listener)
    return () => {
      globalState.listeners.delete(listener)
    }
  }, [])

  // Helper to update global state
  const updateGlobalState = useCallback((updates: Partial<GlobalState>) => {
    Object.assign(globalState, updates)
    globalState.listeners.forEach(listener => listener(globalState))
  }, [])

  const authenticate = useCallback(async () => {
    if (!globalClient || globalState.isAuthenticating) return

    // If already authenticated, return early
    if (globalState.isAuthenticated) {
      console.log('✅ Already authenticated, skipping...')
      return
    }

    // If authentication is already in progress, wait for it
    if (authPromise) {
      console.log('⏳ Authentication already in progress, waiting...')
      return authPromise
    }

    console.log('🔐 Starting Stack AI authentication...')
    
    updateGlobalState({ 
      isAuthenticating: true, 
      error: null 
    })

    authPromise = (async () => {
      try {
        // Authenticate with Stack AI
        console.log('📡 Calling authenticate...')
        await globalClient!.authenticate()
        console.log('✅ Authentication successful!')
        
        // Get the first Google Drive connection
        console.log('🔍 Fetching connections...')
        const connections = await globalClient!.listConnections('gdrive', 1)
        console.log('📋 Connections received:', connections)
        
        if (connections.length === 0) {
          throw new Error('No Google Drive connection found. Please set up a connection first.')
        }

        const firstConnection = connections[0]
        console.log('🔗 Using connection:', firstConnection.name, firstConnection.connection_id)
        
        updateGlobalState({
          connectionId: firstConnection.connection_id,
          userEmail: globalClient!.getUserEmail(),
          isAuthenticated: true,
          isAuthenticating: false,
          error: null
        })
        
        toast.success('Successfully connected to Stack AI')
        console.log('🎉 Authentication flow completed successfully!')
        
      } catch (err) {
        console.error('❌ Authentication error details:', err)
        
        let errorMessage = 'Authentication failed'
        
        if (err instanceof Error) {
          errorMessage = err.message
          
          // Add more specific error handling
          if (err.message.includes('CORS')) {
            errorMessage = 'CORS error: Unable to connect to Stack AI API from browser'
          } else if (err.message.includes('Failed to fetch')) {
            errorMessage = 'Network error: Unable to reach Stack AI API'
          } else if (err.message.includes('401') || err.message.includes('403')) {
            errorMessage = 'Authentication failed: Invalid credentials'
          } else if (err.message.includes('Server configuration error')) {
            errorMessage = 'Server configuration error: Check environment variables'
          }
        }
        
        console.error('🚨 Final error message:', errorMessage)
        updateGlobalState({
          error: errorMessage,
          isAuthenticated: false,
          isAuthenticating: false
        })
        toast.error(`Authentication failed: ${errorMessage}`)
      } finally {
        authPromise = null
      }
    })()

    return authPromise
  }, [updateGlobalState])

  // Auto-authenticate on mount (only once globally)
  useEffect(() => {
    if (!globalState.isAuthenticated && !globalState.isAuthenticating && !globalState.error) {
      console.log('🚀 Auto-authenticating on mount...')
      authenticate()
    }
  }, [authenticate])

  return {
    client: globalClient,
    isAuthenticated: state.isAuthenticated,
    isAuthenticating: state.isAuthenticating,
    connectionId: state.connectionId,
    userEmail: state.userEmail,
    authenticate,
    error: state.error
  }
} 