/**
 * Stack AI API Client (TypeScript) - Proxied through Next.js API routes
 * =====================================================================
 * 
 * Frontend API client that calls our Next.js API routes which proxy
 * to the Stack AI API. This avoids CORS issues.
 */

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
    console.log('🔐 Client: Starting authentication via API route...')
    
    const requestBody: Record<string, string> = {}
    
    // Only include credentials if they were provided
    if (this.email && this.password) {
      requestBody.email = this.email
      requestBody.password = this.password
      console.log('🔑 Client: Using provided credentials for:', this.email)
    } else {
      console.log('🔑 Client: Using server default credentials from environment')
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
      console.error('❌ Client: Auth failed:', errorMessage)
      throw new Error(errorMessage)
    }

    const data = await response.json()
    
    this.accessToken = data.accessToken
    this.orgId = data.orgId
    this.userEmail = data.userEmail
    this.connections = data.connections || []
    this.authenticated = true

    console.log('✅ Client: Authentication successful!')

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

    console.log('📡 Client: Fetching files via API route...')

    const response = await fetch(`/api/stackai/files?${params}`, {
      headers: {
        'x-access-token': this.accessToken,
      },
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      const errorMessage = errorData.error || `Failed to fetch files: ${response.statusText}`
      console.error('❌ Client: Files fetch failed:', errorMessage)
      throw new Error(errorMessage)
    }

    const data = await response.json()
    console.log(`✅ Client: Fetched ${data.data?.length || 0} files`)
    
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
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    _connectionId: string,
    // eslint-disable-next-line @typescript-eslint/no-unused-vars  
    _resourceIds: string[]
  ): Promise<Record<string, FileResource>> {
    // For now, return empty object - we can implement this later if needed
    console.log('⚠️ getResourceDetails not implemented yet')
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
    // For demo purposes, return a mock knowledge base
    // In a real implementation, this would call another API route
    console.log('⚠️ createKnowledgeBase - using mock implementation for demo')
    
    const mockKb: KnowledgeBase = {
      knowledge_base_id: `kb_${Date.now()}`,
      name,
      description,
      connection_id: connectionId,
      connection_source_ids: connectionSourceIds,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      indexing_params: indexingParams || {}
    }

    return mockKb
  }

  /**
   * Trigger knowledge base synchronization
   */
  async syncKnowledgeBase(
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    _knowledgeBaseId: string
  ): Promise<boolean> {
    console.log('⚠️ syncKnowledgeBase - using mock implementation for demo')
    return true
  }

  /**
   * Wait for knowledge base indexing to complete
   */
  async waitForIndexing(
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    _knowledgeBaseId: string,
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    _timeout = 300000,
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    _checkInterval = 5000
  ): Promise<boolean> {
    console.log('⚠️ waitForIndexing - using mock implementation for demo')
    
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