'use client';

import { createContext, useContext, useCallback, useEffect, useState, ReactNode } from 'react'
import { StackAIClient, getDefaultClient } from '@/lib/api/stackai-client'
import { toast } from 'sonner'
import { auth } from '@/lib/logger'

interface StackAIContextValue {
  client: StackAIClient | null
  isAuthenticated: boolean
  isAuthenticating: boolean
  connectionId: string | null
  userEmail: string | null
  authenticate: () => Promise<void>
  error: string | null
}

const StackAIContext = createContext<StackAIContextValue | null>(null)

// Prevent multiple concurrent authentications
let authPromise: Promise<void> | null = null

export function StackAIProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState({
    client: getDefaultClient(),
    isAuthenticated: false,
    isAuthenticating: false,
    connectionId: null as string | null,
    userEmail: null as string | null,
    error: null as string | null
  })

  const authenticate = useCallback(async () => {
    if (!state.client || state.isAuthenticating) return

    if (state.isAuthenticated) {
      auth.debug('Already authenticated, skipping...')
      return
    }

    if (authPromise) {
      auth.debug('Authentication already in progress, waiting...')
      return authPromise
    }

    auth.info('Starting Stack AI authentication...')
    
    setState(prev => ({ ...prev, isAuthenticating: true, error: null }))

    authPromise = (async () => {
      try {
        await state.client!.authenticate()
        const connections = await state.client!.listConnections('gdrive', 1)
        
        if (connections.length === 0) {
          throw new Error('No Google Drive connection found. Please set up a connection first.')
        }

        const firstConnection = connections[0]
        
        setState(prev => ({
          ...prev,
          connectionId: firstConnection.connection_id,
          userEmail: state.client!.getUserEmail() || null,
          isAuthenticated: true,
          isAuthenticating: false,
          error: null
        }))
        
        toast.success('Successfully connected to Stack AI')
        
      } catch (err) {
        auth.error('Authentication error', { error: err })
        
        let errorMessage = 'Authentication failed'
        if (err instanceof Error) {
          errorMessage = err.message
        }
        
        setState(prev => ({
          ...prev,
          error: errorMessage,
          isAuthenticated: false,
          isAuthenticating: false
        }))
        
        toast.error(`Authentication failed: ${errorMessage}`)
      } finally {
        authPromise = null
      }
    })()

    return authPromise
  }, [state.client, state.isAuthenticated, state.isAuthenticating])

  // Auto-authenticate on mount
  useEffect(() => {
    if (!state.isAuthenticated && !state.isAuthenticating && !state.error) {
      authenticate()
    }
  }, [authenticate, state.isAuthenticated, state.isAuthenticating, state.error])

  return (
    <StackAIContext.Provider value={{ ...state, authenticate }}>
      {children}
    </StackAIContext.Provider>
  )
}

export function useStackAI() {
  const context = useContext(StackAIContext)
  if (!context) {
    throw new Error('useStackAI must be used within a StackAIProvider')
  }
  return context
} 