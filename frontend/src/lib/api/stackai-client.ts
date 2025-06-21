/**
 * Stack AI API Client (TypeScript) - Proxied through Next.js API routes
 * =====================================================================
 * 
 * Frontend API client that calls our Next.js API routes which proxy
 * to the Stack AI API. This avoids CORS issues.
 */

import { api, warn } from '@/lib/logger'

// ==========================================
// TYPES & INTERFACES
// ==========================================

export enum ResourceType {
  FILE = 'file',
  DIRECTORY = 'directory'
}

export enum ResourceStatus {
  RESOURCE = 'resource',
  PENDING = 'pending', 
  INDEXING = 'indexing',
  INDEXED = 'indexed',
  ERROR = 'error'
}

export interface AuthHeaders {
  [key: string]: string
  Authorization: string
}

export interface Connection {
  connection_id: string
  name: string
  connection_provider: string
  created_at: string
  updated_at: string
  connection_provider_data?: Record<string, unknown>
}

export interface ResourceMetadata {
  last_modified_at: string
  last_modified_by: string
  created_at: string
  created_by: string
  web_url: string
  path: string
}

export interface FileResource {
  resource_id: string
  inode_type: ResourceType
  inode_path: { path: string }
  status: ResourceStatus
  knowledge_base_id: string
  created_at: string
  modified_at: string
  indexed_at?: string
  dataloader_metadata: ResourceMetadata
  content_mime?: string
  size?: number
  content_hash?: string
  user_metadata?: Record<string, unknown>
  inode_id?: string
}

export interface PaginatedResponse<T = unknown> {
  data: T[]
  next_cursor?: string
  current_cursor?: string
  has_more: boolean
}

export interface KnowledgeBase {
  knowledge_base_id: string
  name: string
  description: string
  connection_id: string
  connection_source_ids: string[]
  created_at: string
  updated_at: string
  indexing_params: Record<string, unknown>
}

export interface IndexingParams {
  ocr: boolean
  unstructured: boolean
  embedding_params: {
    embedding_model: string
    api_key: string | null
  }
  chunker_params: {
    chunk_size: number
    chunk_overlap: number
    chunker: string
  }
}

// Knowledge Base Management
export interface CreateKnowledgeBaseRequest {
  connection_id: string;
  connection_source_ids: string[];
  name: string;
  description?: string;
  indexing_params: {
    ocr: boolean;
    unstructured: boolean;
    embedding_params: {
      embedding_model: string;
      api_key: string | null;
    };
    chunker_params: {
      chunk_size: number;
      chunk_overlap: number;
      chunker: string;
    };
  };
  org_level_role: string | null;
  cron_job_id: string | null;
}

export interface KnowledgeBaseResponse {
  knowledge_base_id: string;
  name: string;
  description?: string;
  created_at: string;
  updated_at: string;
  status: string;
}

export interface IndexingProgress {
  total_files: number;
  processed_files: number;
  failed_files: number;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress_percentage: number;
}

// ==========================================
// API CLIENT
// ==========================================

export class StackAIClient {
  private email?: string
  private password?: string
  private accessToken?: string
  private orgId?: string
  private userEmail?: string
  private connections: Connection[] = []
  private authenticated = false

  constructor(
    email?: string,
    password?: string
  ) {
    this.email = email
    this.password = password
  }

  /**
   * Authenticate with Stack AI through our API route
   */
  async authenticate(): Promise<AuthHeaders> {
    api.debug('Starting authentication via API route...')
    
    const requestBody: Record<string, string> = {}
    
    // Only include credentials if they were provided
    if (this.email && this.password) {
      requestBody.email = this.email
      requestBody.password = this.password
      api.debug('Using provided credentials', { email: this.email })
    } else {
      api.debug('Using server default credentials from environment')
    }
    
    const response = await fetch('/api/stackai/auth', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestBody),
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      const errorMessage = errorData.error || `Authentication failed: ${response.statusText}`
      api.error('Auth failed', { message: errorMessage, status: response.status })
      throw new Error(errorMessage)
    }

    const data = await response.json()
    
    this.accessToken = data.accessToken
    this.orgId = data.orgId
    this.userEmail = data.userEmail
    this.connections = data.connections || []
    this.authenticated = true

    api.info('Authentication successful!')

    return {
      Authorization: `Bearer ${this.accessToken}`
    }
  }

  /**
   * List available connections (from cached data)
   */
  async listConnections(
    connectionProvider = 'gdrive',
    limit = 10
  ): Promise<Connection[]> {
    if (!this.authenticated) {
      throw new Error('Client not authenticated. Call authenticate() first.')
    }

    // Filter connections by provider if needed
    const filteredConnections = this.connections.filter(
      conn => conn.connection_provider === connectionProvider
    ).slice(0, limit)

    return filteredConnections
  }

  /**
   * List resources (files/folders) in a connection
   */
  async listResources(
    connectionId: string,
    parentResourceId?: string
  ): Promise<PaginatedResponse<FileResource>> {
    if (!this.authenticated || !this.accessToken) {
      throw new Error('Client not authenticated. Call authenticate() first.')
    }

    const params = new URLSearchParams({
      connectionId
    })
    
    if (parentResourceId) {
      params.set('parentResourceId', parentResourceId)
    }

    api.debug('Fetching files via API route...', { connectionId, parentResourceId })

    const response = await fetch(`/api/stackai/files?${params}`, {
      headers: {
        'x-access-token': this.accessToken,
      },
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      const errorMessage = errorData.error || `Failed to fetch files: ${response.statusText}`
      api.error('Files fetch failed', { message: errorMessage, status: response.status })
      throw new Error(errorMessage)
    }

    const data = await response.json()
    api.info('Fetched files', { count: data.data?.length || 0 })
    
    return {
      data: data.data || [],
      next_cursor: data.next_cursor,
      current_cursor: data.current_cursor,
      has_more: Boolean(data.next_cursor),
    }
  }

  /**
   * Get detailed information about specific resources
   */
  async getResourceDetails(
    connectionId: string,
    resourceIds: string[]
  ): Promise<Record<string, FileResource>> {
    // Suppress unused parameter warnings for future implementation
    void connectionId;
    void resourceIds;
    // For now, return empty object - we can implement this later if needed
    warn('getResourceDetails not implemented yet')
    return {}
  }

  /**
   * Create a new knowledge base
   */
  async createKnowledgeBase(
    connectionId: string,
    connectionSourceIds: string[],
    name: string,
    description: string,
    indexingParams?: Partial<IndexingParams>
  ): Promise<KnowledgeBase> {
    if (!this.authenticated || !this.accessToken) {
      throw new Error('Client not authenticated. Call authenticate() first.')
    }

    const requestData = {
      connection_id: connectionId,
      connection_source_ids: connectionSourceIds,
      name,
      description,
      indexing_params: {
        ocr: false,
        unstructured: true,
        embedding_params: { embedding_model: "text-embedding-ada-002", api_key: null },
        chunker_params: { chunk_size: 1500, chunk_overlap: 500, chunker: "sentence" },
        ...indexingParams
      },
      org_level_role: null,
      cron_job_id: null,
    }

    api.debug('Creating knowledge base via API route...', { name, connectionId })

    const response = await fetch('/api/stackai/knowledge-bases', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-access-token': this.accessToken,
      },
      body: JSON.stringify(requestData),
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      const errorMessage = errorData.error || `Failed to create knowledge base: ${response.statusText}`
      api.error('Knowledge base creation failed', { message: errorMessage, status: response.status })
      throw new Error(errorMessage)
    }

    const data = await response.json()
    api.info('Knowledge base created', { id: data.knowledge_base_id })

    return {
      knowledge_base_id: data.knowledge_base_id,
      name: data.name,
      description: data.description || '',
      connection_id: connectionId,
      connection_source_ids: connectionSourceIds,
      created_at: data.created_at,
      updated_at: data.updated_at,
      indexing_params: requestData.indexing_params
    }
  }

  /**
   * Trigger knowledge base synchronization
   */
  async syncKnowledgeBase(knowledgeBaseId: string): Promise<boolean> {
    if (!this.authenticated || !this.accessToken || !this.orgId) {
      throw new Error('Client not authenticated. Call authenticate() first.')
    }

    api.debug('Triggering knowledge base sync via API route...', { knowledgeBaseId })

    const response = await fetch(`/api/stackai/knowledge-bases/${knowledgeBaseId}/sync/${this.orgId}`, {
      method: 'POST',
      headers: {
        'x-access-token': this.accessToken,
      },
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      const errorMessage = errorData.error || `Failed to sync knowledge base: ${response.statusText}`
      api.error('Knowledge base sync failed', { message: errorMessage, status: response.status })
      throw new Error(errorMessage)
    }

    const data = await response.json()
    api.info('Knowledge base sync triggered', { message: data.message })

    return true
  }

  /**
   * Wait for knowledge base indexing to complete
   */
  async waitForIndexing(
    knowledgeBaseId: string,
    timeout = 300000,
    checkInterval = 5000
  ): Promise<boolean> {
    // Suppress unused parameter warnings for future implementation
    void knowledgeBaseId;
    void timeout;
    void checkInterval;
    warn('waitForIndexing - using mock implementation for demo')
    
    // Simulate indexing delay
    await new Promise(resolve => setTimeout(resolve, 2000))
    return true
  }

  /**
   * Get current organization ID
   */
  getOrgId(): string | undefined {
    return this.orgId
  }

  /**
   * Check if client is authenticated
   */
  isAuthenticated(): boolean {
    return this.authenticated
  }

  /**
   * Get authenticated user's email
   */
  getUserEmail(): string | undefined {
    return this.userEmail
  }

  /**
   * Get access token for API calls
   */
  getAccessToken(): string | undefined {
    return this.accessToken
  }
}

// ==========================================
// UTILITY FUNCTIONS
// ==========================================

/**
 * Helper to extract file name from resource path
 */
export function getResourceName(resource: FileResource): string {
  return resource.inode_path.path.split('/').pop() || resource.inode_path.path
}

/**
 * Helper to check if resource is a directory
 */
export function isDirectory(resource: FileResource): boolean {
  return resource.inode_type === ResourceType.DIRECTORY
}

/**
 * Helper to check if resource is indexed
 */
export function isIndexed(resource: FileResource): boolean {
  return resource.status === ResourceStatus.INDEXED
}

/**
 * Helper to check if resource is being indexed
 */
export function isIndexing(resource: FileResource): boolean {
  return resource.status === ResourceStatus.INDEXING
}

/**
 * Helper to format file size
 */
export function formatFileSize(bytes?: number): string {
  if (!bytes) return '—'
  
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(1024))
  return `${(bytes / Math.pow(1024, i)).toFixed(1)} ${sizes[i]}`
}

/**
 * Helper to format date
 */
export function formatDate(dateString: string): string {
  return new Date(dateString).toLocaleDateString()
}

// ==========================================
// FACTORY FUNCTIONS
// ==========================================

/**
 * Create a client with default credentials from environment (server-side)
 */
export function createDefaultClient(): StackAIClient {
  return new StackAIClient()
}

/**
 * Create a client with custom credentials
 */
export function createClientWithCredentials(email: string, password: string): StackAIClient {
  return new StackAIClient(email, password)
}

// Default client instance for convenience
let defaultClient: StackAIClient | null = null

export function getDefaultClient(): StackAIClient {
  if (!defaultClient) {
    defaultClient = createDefaultClient()
  }
  return defaultClient
}

/**
 * Create a new knowledge base with selected files
 */
// Note: This function is superseded by the StackAIClient.createKnowledgeBase method
// Keeping for backwards compatibility but not actively used
export const createKnowledgeBase = async (
  accessToken: string,
  request: CreateKnowledgeBaseRequest
): Promise<KnowledgeBaseResponse> => {
  const response = await fetch('/api/stackai/knowledge-bases', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${accessToken}`,
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ message: 'Failed to create knowledge base' }));
    throw new Error(error.message || 'Failed to create knowledge base');
  }

  return response.json();
};

/**
 * Sync knowledge base to trigger indexing
 */
export const syncKnowledgeBase = async (
  accessToken: string,
  knowledgeBaseId: string,
  orgId: string
): Promise<void> => {
  const response = await fetch(`/api/stackai/knowledge-bases/${knowledgeBaseId}/sync/${orgId}`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${accessToken}`,
    },
  });

  if (!response.ok) {
    throw new Error('Failed to sync knowledge base');
  }
};

/**
 * Get indexing progress for a knowledge base
 */
export const getIndexingProgress = async (
  accessToken: string,
  knowledgeBaseId: string
): Promise<IndexingProgress> => {
  const response = await fetch(`/api/stackai/knowledge-bases/${knowledgeBaseId}/progress`, {
    headers: {
      'Authorization': `Bearer ${accessToken}`,
    },
  });

  if (!response.ok) {
    throw new Error('Failed to get indexing progress');
  }

  return response.json();
};

/**
 * Remove files from knowledge base (de-index)
 */
export const removeFromKnowledgeBase = async (
  accessToken: string,
  knowledgeBaseId: string,
  resourcePaths: string[]
): Promise<void> => {
  const promises = resourcePaths.map(async (resourcePath) => {
    const response = await fetch(`/api/stackai/knowledge-bases/${knowledgeBaseId}/resources`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${accessToken}`,
      },
      body: JSON.stringify({ resource_path: resourcePath }),
    });

    if (!response.ok) {
      throw new Error(`Failed to remove ${resourcePath} from knowledge base`);
    }
  });

  await Promise.all(promises);
};

/**
 * Smart file selection - removes children if parent is selected
 */
export const optimizeFileSelection = (
  selectedFiles: FileResource[]
): FileResource[] => {
  const selectedPaths = new Set(selectedFiles.map(f => f.inode_path.path));
  
  return selectedFiles.filter(file => {
    // Check if any parent directory is already selected
    const pathParts = file.inode_path.path.split('/');
    
    for (let i = 1; i < pathParts.length; i++) {
      const parentPath = pathParts.slice(0, i).join('/');
      if (selectedPaths.has(parentPath)) {
        // Parent is selected, so we can exclude this file
        return false;
      }
    }
    
    return true;
  });
}; 