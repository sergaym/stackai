import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"
import React from "react"
import {
  FolderIcon,
  DocumentIcon,
  DocumentTextIcon,
  ChartBarIcon,
  PhotoIcon,
  FilmIcon,
  MusicalNoteIcon,
  ArchiveBoxIcon,
} from '@heroicons/react/24/outline'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

/**
 * Debounce function to limit API calls
 */
export function debounce<T extends (...args: readonly unknown[]) => unknown>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout | null = null
  
  return (...args: Parameters<T>) => {
    if (timeout) clearTimeout(timeout)
    timeout = setTimeout(() => func(...args), wait)
  }
}

/**
 * Format file size in human readable format
 */
export function formatFileSize(bytes?: number): string {
  if (!bytes || bytes === 0) return '—'
  
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(1024))
  return `${(bytes / Math.pow(1024, i)).toFixed(1)} ${sizes[i]}`
}

/**
 * Format date to relative or absolute format
 */
export function formatDate(dateString: string): string {
  const date = new Date(dateString)
  const now = new Date()
  const diffInDays = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60 * 24))
  
  if (diffInDays === 0) {
    return 'Today'
  } else if (diffInDays === 1) {
    return 'Yesterday'
  } else if (diffInDays < 7) {
    return `${diffInDays} days ago`
  } else {
    return date.toLocaleDateString()
  }
}

/**
 * Get file extension from filename
 */
export function getFileExtension(filename: string): string {
  const lastDot = filename.lastIndexOf('.')
  return lastDot > 0 ? filename.substring(lastDot + 1).toLowerCase() : ''
}

/**
 * Get appropriate icon for file type
 */
export function getFileIcon(filename: string, isDirectory: boolean): React.ReactElement {
  const iconProps = { className: "h-5 w-5 text-gray-600" };
  
  if (isDirectory) {
    return React.createElement(FolderIcon, iconProps);
  }
  
  const ext = getFileExtension(filename)
  
  // Document types
  if (['pdf', 'doc', 'docx', 'txt', 'md'].includes(ext)) {
    return React.createElement(DocumentTextIcon, iconProps);
  }
  
  // Spreadsheet and presentation types
  if (['xls', 'xlsx', 'csv', 'ppt', 'pptx'].includes(ext)) {
    return React.createElement(ChartBarIcon, iconProps);
  }
  
  // Image types
  if (['jpg', 'jpeg', 'png', 'gif', 'svg', 'webp'].includes(ext)) {
    return React.createElement(PhotoIcon, iconProps);
  }
  
  // Video types
  if (['mp4', 'avi', 'mov', 'mkv', 'webm'].includes(ext)) {
    return React.createElement(FilmIcon, iconProps);
  }
  
  // Audio types
  if (['mp3', 'wav', 'flac', 'ogg'].includes(ext)) {
    return React.createElement(MusicalNoteIcon, iconProps);
  }
  
  // Archive types
  if (['zip', 'rar', 'tar', 'gz', '7z'].includes(ext)) {
    return React.createElement(ArchiveBoxIcon, iconProps);
  }
  
  // Default document icon
  return React.createElement(DocumentIcon, iconProps);
}

/**
 * Filter files by search query
 */
export function filterFiles<T extends { inode_path: { path: string } }>(
  files: T[],
  query: string
): T[] {
  if (!query.trim()) return files
  
  const lowercaseQuery = query.toLowerCase()
  return files.filter(file => 
    file.inode_path.path.toLowerCase().includes(lowercaseQuery)
  )
}

/**
 * Sort files by different criteria
 */
export type SortOption = 'name' | 'date' | 'size'
export type SortDirection = 'asc' | 'desc'

export function sortFiles<T extends { 
  inode_path: { path: string }
  inode_type: string
  modified_at?: string
  size?: number
}>(
  files: T[],
  sortBy: SortOption,
  direction: SortDirection = 'asc'
): T[] {
  const sortedFiles = [...files].sort((a, b) => {
    // Always put directories first
    if (a.inode_type === 'directory' && b.inode_type !== 'directory') return -1
    if (a.inode_type !== 'directory' && b.inode_type === 'directory') return 1
    
    let comparison = 0
    
    switch (sortBy) {
      case 'name':
        comparison = a.inode_path.path.localeCompare(b.inode_path.path)
        break
      case 'date':
        const dateA = new Date(a.modified_at || 0).getTime()
        const dateB = new Date(b.modified_at || 0).getTime()
        comparison = dateA - dateB
        break
      case 'size':
        comparison = (a.size || 0) - (b.size || 0)
        break
    }
    
    return direction === 'asc' ? comparison : -comparison
  })
  
  return sortedFiles
}

/**
 * Extract filename from full path
 */
export function getFileName(path: string): string {
  return path.split('/').pop() || path
}

/**
 * Generate breadcrumb path from folder path
 */
export function generateBreadcrumbs(path: string): Array<{ name: string; path: string }> {
  if (!path || path === '/') {
    return [{ name: 'Root', path: '/' }]
  }
  
  const parts = path.split('/').filter(Boolean)
  const breadcrumbs = [{ name: 'Root', path: '/' }]
  
  let currentPath = ''
  for (const part of parts) {
    currentPath += `/${part}`
    breadcrumbs.push({
      name: part,
      path: currentPath
    })
  }
  
  return breadcrumbs
}

/**
 * Truncate text with ellipsis
 */
export function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text
  return text.substring(0, maxLength - 3) + '...'
}
