/**
 * Application types
 */

// ==========================================
// FILE MANAGEMENT
// ==========================================

export interface FileItem {
  id: string;
  name: string;
  type: 'file' | 'folder';
  size?: number;
  modifiedDate: string;
  status: 'resource' | 'pending' | 'indexing' | 'indexed' | 'error';
  isExpanded?: boolean;
  children?: FileItem[];
}

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

export interface PaginatedResponse<T> {
  data: T[];
  next_cursor?: string;
  has_more: boolean;
}
