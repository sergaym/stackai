/**
 * Application types
 */

// Re-export API types for consistency
export type {
  FileResource,
  ResourceType,
  ResourceStatus,
  Connection,
  PaginatedResponse,
  KnowledgeBase
} from '@/lib/api/stackai-client'

// ==========================================
// INTEGRATIONS
// ==========================================

export interface Integration {
  id: string;
  name: string;
  icon: string;
  count?: number;
  isActive?: boolean;
  isBeta?: boolean;
}

// ==========================================
// COMPONENT PROPS
// ==========================================

export interface FilePickerDialogProps {
  isOpen: boolean;
  onClose: () => void;
}

// ==========================================
// UI STATE (simple)
// ==========================================

export interface FileSelectionState {
  selectedIds: string[];
  searchQuery: string;
  sortBy: 'name' | 'date' | 'size';
  sortDirection: 'asc' | 'desc';
}

// ==========================================
// API RESPONSES (basic)
// ==========================================

export interface ApiResponse<T> {
  data: T;
  success: boolean;
  message?: string;
}
