'use client';

import { useState, useCallback, useMemo, useEffect } from 'react';
import { Search, ChevronDown, RefreshCw, MoreHorizontal, Calendar, FileText, HardDrive, Check } from 'lucide-react';
import { 
  FolderIcon, 
  DocumentIcon, 
  CheckCircleIcon, 
  CircleStackIcon,
  Bars3Icon,
  FunnelIcon
} from '@heroicons/react/24/outline';
import { clsx } from 'clsx';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Skeleton } from '@/components/ui/skeleton';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from '@/components/ui/tooltip';
import { IntegrationIcon } from '@/components/ui/integration-icon';
import { useStackAI } from '@/contexts/stackai-context';
import { useFiles } from '@/hooks/useFiles';
import { useFileActions } from '@/hooks/useFileActions';
import { getFileName, filterFiles, sortFiles, type SortOption, type SortDirection } from '@/lib/utils';
import { FileItem } from './FileItem';
import { ResourceType, type FileResource } from '@/lib/api/stackai-client';
import type { Integration } from '@/types';
import { toast } from 'sonner';

interface IntegrationContentProps {
  integration: Integration;
  selectedItems: string[];
  onItemSelect: (id: string) => void;
  searchTerm: string;
  onSearchChange: (term: string) => void;
}

export function IntegrationContent({ 
  integration, 
  selectedItems, 
  onItemSelect, 
  searchTerm, 
  onSearchChange 
}: IntegrationContentProps) {
  const [showAddAccountDialog, setShowAddAccountDialog] = useState(false);
  
  // Render content based on integration type
  const renderContent = () => {
    switch (integration.id) {
      case 'googledrive':
        return <GoogleDriveContent 
          selectedItems={selectedItems}
          onItemSelect={onItemSelect}
          searchTerm={searchTerm}
          onSearchChange={onSearchChange}
        />;
      case 'files':
        return <FilesContent />;
      case 'websites':
        return <WebsitesContent />;
      case 'text':
        return <TextContent />;
      case 'confluence':
        return <ConfluenceContent />;
      case 'notion':
        return <NotionContent />;
      case 'onedrive':
        return <OneDriveContent />;
      case 'sharepoint':
        return <SharePointContent />;
      case 'slack':
        return <SlackContent />;
      default:
        return <DefaultContent integration={integration} />;
    }
  };

  return (
    <div className="h-full flex flex-col p-6">
      {/* Dynamic Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <IntegrationIcon icon={integration.icon} name={integration.name} withBackground={true} />
          <span className="font-semibold text-gray-900">{integration.name}</span>
          {integration.id === 'googledrive' && (
            <span className="text-xs text-gray-600 bg-gray-100 px-2 py-0.5 rounded">
              Beta
            </span>
          )}
        </div>
        <div className="flex items-center gap-2">
          {integration.id === 'googledrive' && (
            <Button 
              variant="secondary" 
              size="sm"
              onClick={() => setShowAddAccountDialog(true)}
            >
              + Add account
            </Button>
          )}
        </div>
      </div>
      
      {/* Separator */}
      <div className="border-b border-gray-200 mb-4"></div>

      {/* Dynamic Content */}
      {renderContent()}

      {/* Add Account Dialog */}
      {showAddAccountDialog && (
        <div 
          className="fixed inset-0 z-50 bg-black/50 flex items-center justify-center p-4"
          onClick={() => setShowAddAccountDialog(false)}
        >
          <div 
            className="bg-white rounded-lg shadow-xl p-6 max-w-md w-full mx-4"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="text-left">
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Feature Coming Soon
              </h3>
              <p className="text-gray-600 mb-6 text-sm leading-relaxed">
                Additional Google Drive accounts are not yet available. This feature is coming soon to help you manage multiple Google Drive connections.
              </p>
              <div className="flex gap-3 justify-end">
                <Button 
                  onClick={() => setShowAddAccountDialog(false)}
                  className="px-4 py-2 bg-gray-900 hover:bg-gray-800 text-white"
                >
                  Got it
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// Enhanced Google Drive content with real API integration
function GoogleDriveContent({ selectedItems, onItemSelect, searchTerm, onSearchChange }: {
  selectedItems: string[];
  onItemSelect: (id: string) => void;
  searchTerm: string;
  onSearchChange: (term: string) => void;
}) {
  // Authentication and API state
  const { isAuthenticated, isAuthenticating, error: authError, authenticate, userEmail } = useStackAI();
  const [currentResourceId, setCurrentResourceId] = useState<string | undefined>();
  const [currentPath, setCurrentPath] = useState<string[]>([]);
  const [sortBy, setSortBy] = useState<SortOption>('name');
  const [sortDirection, setSortDirection] = useState<SortDirection>('asc');
  const [isExpanded, setIsExpanded] = useState(true);

  // Data fetching
  const { files, isLoading, error, mutate } = useFiles(currentResourceId);
  const { indexFiles } = useFileActions();

  // Handle authentication errors with toasts
  useEffect(() => {
    if (authError) {
      toast.error(`Connection failed: ${authError}`, {
        action: {
          label: 'Retry',
          onClick: () => authenticate(),
        },
        duration: 10000,
      });
    }
  }, [authError, authenticate]);

  // Handle file loading errors with toasts
  useEffect(() => {
    if (error && !isLoading) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to load files';
      toast.error(`Error loading files: ${errorMessage}`, {
        action: {
          label: 'Try Again',
          onClick: () => mutate(),
        },
        duration: 8000,
      });
    }
  }, [error, isLoading, mutate]);

  // Handle folder navigation
  const handleFolderOpen = useCallback((file: FileResource) => {
    if (file.inode_type !== ResourceType.DIRECTORY) return;
    
    const folderName = getFileName(file.inode_path.path);
    setCurrentPath(prev => [...prev, folderName]);
    setCurrentResourceId(file.resource_id);
  }, []);

  // Handle breadcrumb navigation
  const handleBreadcrumbClick = useCallback((index: number) => {
    if (index === 0) {
      setCurrentPath([]);
      setCurrentResourceId(undefined);
    } else {
      setCurrentPath(prev => prev.slice(0, index));
      setCurrentResourceId(undefined); // For simplicity, go to root
    }
  }, []);

  // Handle select all
  const handleSelectAll = useCallback((checked: boolean) => {
    if (checked) {
      const allFileIds = files.map(f => f.resource_id);
      allFileIds.forEach(id => {
        if (!selectedItems.includes(id)) {
          onItemSelect(id);
        }
      });
    } else {
      selectedItems.forEach(id => onItemSelect(id));
    }
  }, [files, selectedItems, onItemSelect]);

  // Handle sort change
  const handleSortChange = useCallback((newSortBy: SortOption) => {
    if (newSortBy === sortBy) {
      setSortDirection(prev => prev === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(newSortBy);
      setSortDirection('asc');
    }
  }, [sortBy]);

  // Process files (filter and sort)
  const processedFiles = useMemo(() => {
    let result = files;
    
    // Apply search filter
    if (searchTerm.trim()) {
      result = filterFiles(result, searchTerm);
    }
    
    // Apply sorting
    result = sortFiles(result, sortBy, sortDirection);
    
    return result;
  }, [files, searchTerm, sortBy, sortDirection]);



  // Generate breadcrumbs
  const breadcrumbs = useMemo(() => {
    const crumbs = [{ name: 'Google Drive', index: 0 }];
    currentPath.forEach((segment, index) => {
      crumbs.push({ name: segment, index: index + 1 });
    });
    return crumbs;
  }, [currentPath]);

  // Show loading while authenticating
  if (isAuthenticating) {
    return (
      <div className="flex-1 flex flex-col space-y-6 p-6">
        {/* Header skeleton */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Skeleton className="h-4 w-4" />
            <Skeleton className="h-4 w-32" />
          </div>
          <Skeleton className="h-8 w-24" />
        </div>
        
        {/* Controls skeleton */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <Skeleton className="h-4 w-24" />
            <Skeleton className="h-8 w-32" />
          </div>
          <div className="flex items-center gap-4">
            <Skeleton className="h-8 w-16" />
            <Skeleton className="h-8 w-16" />
            <Skeleton className="h-10 flex-1" />
          </div>
        </div>
        
        {/* File list skeleton */}
        <div className="p-4">
          <FolderLoadingSkeleton />
        </div>
      </div>
    );
  }

  // Show connection prompt if not authenticated (and no active error)
  if (!isAuthenticated && !authError) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <div className="text-center space-y-4">
          <p className="text-gray-600">Not connected to Stack AI</p>
          <Button onClick={authenticate}>Connect to Stack AI</Button>
        </div>
      </div>
    );
  }

  // Show empty state if authentication failed (error handled via toast)
  if (authError) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <div className="text-center space-y-4">
          <div className="text-6xl mb-4">🔌</div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            Connection Required
          </h3>
          <p className="text-gray-600">
            Please check the error notification and try connecting again.
          </p>
          <Button onClick={authenticate} variant="outline">
            Retry Connection
          </Button>
        </div>
      </div>
    );
  }

  return (
    <>
      {/* Controls Section */}
      <div className="space-y-3 mb-2">
        {/* Top Row: Select all + count */}
        <div className="flex items-center justify-between">
          <button
            onClick={() => handleSelectAll(selectedItems.length !== processedFiles.length)}
            className="flex items-center gap-2 text-sm text-gray-600 hover:text-gray-900"
          >
            <input
              type="checkbox"
              checked={selectedItems.length > 0 && selectedItems.length === processedFiles.length}
              ref={(el) => {
                if (el) el.indeterminate = selectedItems.length > 0 && selectedItems.length < processedFiles.length;
              }}
              readOnly
              className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500 focus:ring-offset-0"
            />
            <span>Select all</span>
          </button>
          <span className="text-sm text-gray-500">
            {selectedItems.length > 0 ? `${selectedItems.length} selected` : `0 selected`}
          </span>
        </div>

        {/* Horizontal Separator */}
        <div className="border-t border-gray-200"></div>

        {/* Bottom Row: Sort/Filter on left, Index/Search on right */}
        <div className="flex items-center justify-between">
          {/* Left side: Sort + Filter */}
          <div className="flex items-center gap-2">
            {/* Sort Dropdown */}
            <DropdownMenu>
              <Tooltip>
                <TooltipTrigger asChild>
                  <DropdownMenuTrigger asChild>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="flex items-center gap-1.5 px-2 py-1 h-auto text-sm text-gray-500 hover:text-gray-700 hover:bg-gray-50"
                    >
                      <Bars3Icon className="h-4 w-4" />
                      <span>Sort</span>
                    </Button>
                  </DropdownMenuTrigger>
                </TooltipTrigger>
                <TooltipContent side="top">
                  <p>Sort files</p>
                </TooltipContent>
              </Tooltip>
              <DropdownMenuContent align="start" className="w-48">
                {(['name', 'date', 'size'] as SortOption[]).map((option) => {
                  const icons = {
                    name: <FileText className="h-4 w-4" />,
                    date: <Calendar className="h-4 w-4" />,
                    size: <HardDrive className="h-4 w-4" />
                  };
                  
                  return (
                    <DropdownMenuItem
                      key={option}
                      onClick={() => handleSortChange(option)}
                      className="flex items-center gap-3 cursor-pointer"
                    >
                      {icons[option]}
                      <span className="flex-1 capitalize">{option}</span>
                      {sortBy === option && (
                        <div className="flex items-center gap-1">
                          <Check className="h-3 w-3 text-blue-600" />
                          <span className="text-xs text-gray-500">
                            {sortDirection === 'asc' ? '↑' : '↓'}
                          </span>
                        </div>
                      )}
                    </DropdownMenuItem>
                  );
                })}
              </DropdownMenuContent>
            </DropdownMenu>

            {/* Filter Dropdown */}
            <DropdownMenu>
              <Tooltip>
                <TooltipTrigger asChild>
                  <DropdownMenuTrigger asChild>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="flex items-center gap-1.5 px-2 py-1 h-auto text-sm text-gray-500 hover:text-gray-700 hover:bg-gray-50"
                    >
                      <FunnelIcon className="h-4 w-4" />
                      <span>Filter</span>
                    </Button>
                  </DropdownMenuTrigger>
                </TooltipTrigger>
                <TooltipContent side="top">
                  <p>Filter files</p>
                </TooltipContent>
              </Tooltip>
              <DropdownMenuContent align="start" className="w-48">
                <DropdownMenuItem className="flex items-center gap-3 cursor-pointer">
                  <FolderIcon className="h-4 w-4 text-gray-500" />
                  <span>Folders only</span>
                </DropdownMenuItem>
                <DropdownMenuItem className="flex items-center gap-3 cursor-pointer">
                  <DocumentIcon className="h-4 w-4 text-gray-500" />
                  <span>Files only</span>
                </DropdownMenuItem>
                <DropdownMenuItem className="flex items-center gap-3 cursor-pointer">
                  <CheckCircleIcon className="h-4 w-4 text-green-500" />
                  <span>Indexed</span>
                </DropdownMenuItem>
                <DropdownMenuItem className="flex items-center gap-3 cursor-pointer">
                  <CircleStackIcon className="h-4 w-4 text-gray-400" />
                  <span>Not indexed</span>
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem className="text-gray-500 cursor-pointer">
                  Clear filters
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>

          {/* Right side: Index + Search */}
          <div className="flex items-center gap-2">
            {/* Index Selected Files Button */}
            {selectedItems.length > 0 && (
              <Button
                onClick={() => {
                  const selectedFiles = processedFiles.filter(f => selectedItems.includes(f.resource_id));
                  indexFiles(selectedItems, selectedFiles);
                }}
                size="sm"
                className="h-8 px-3 text-xs bg-blue-600 hover:bg-blue-700 text-white"
              >
                Index {selectedItems.length} file{selectedItems.length !== 1 ? 's' : ''}
              </Button>
            )}
            
            {/* Compact Search */}
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <Input
                type="text"
                placeholder="Search..."
                value={searchTerm}
                onChange={(e) => onSearchChange(e.target.value)}
                className="pl-10 w-48 h-8 text-sm bg-gray-50 border-0 rounded-md focus:bg-white focus:ring-0 focus:outline-none transition-colors"
              />
            </div>
          </div>
        </div>
      </div>

      {/* Breadcrumbs - After Controls */}
      {breadcrumbs.length > 1 && (
        <div className="mb-2">
          <nav className="flex items-center space-x-1 text-sm">
            {breadcrumbs.map((crumb, index) => (
              <div key={index} className="flex items-center">
                <button
                  onClick={() => handleBreadcrumbClick(index)}
                  className={`px-2 py-1 rounded ${
                    index === breadcrumbs.length - 1
                      ? 'text-gray-900 cursor-default'
                      : 'text-gray-600 hover:text-gray-800 hover:bg-gray-50'
                  }`}
                  disabled={index === breadcrumbs.length - 1}
                >
                  {crumb.name}
                </button>
                {index < breadcrumbs.length - 1 && (
                  <ChevronDown className="h-4 w-4 text-gray-400 mx-1 -rotate-90" />
                )}
              </div>
            ))}
          </nav>
        </div>
      )}

      {/* Hierarchical File Tree */}
      <div className="flex-1 flex flex-col min-h-0">
        {/* File loading error - show empty content, error is handled via toast */}
        {error && !isLoading ? (
          <div className="flex-1 flex items-center justify-center p-8">
            <div className="text-center space-y-4">
              <div className="text-6xl mb-4">⚠️</div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Unable to Load Files
              </h3>
              <p className="text-gray-600">
                Check the error notification for details.
              </p>
              <Button onClick={() => mutate()} variant="outline" className="flex items-center gap-2">
                <RefreshCw className="h-4 w-4" />
                Try Again
              </Button>
            </div>
          </div>
        ) : (
          /* Google Drive Node - Always show when authenticated and no error */
          <div className="flex flex-col flex-1 min-h-0">
            {/* Google Drive Parent Node - Fixed Header */}
            <div className="flex items-center gap-2 py-2 border-b border-gray-100 bg-gray-100 flex-shrink-0">
              {/* Expand/Collapse Arrow */}
              <button
                onClick={() => setIsExpanded(!isExpanded)}
                className="p-0.5 hover:bg-gray-100 rounded transition-colors ml-1"
              >
                <ChevronDown 
                  className={clsx(
                    "h-4 w-4 text-gray-400 transition-transform",
                    !isExpanded && "-rotate-90"
                  )} 
                />
              </button>
              
              {/* Select All Checkbox */}
              <input
                type="checkbox"
                checked={selectedItems.length > 0 && selectedItems.length === processedFiles.length}
                ref={(el) => {
                  if (el) el.indeterminate = selectedItems.length > 0 && selectedItems.length < processedFiles.length;
                }}
                onChange={(e) => handleSelectAll(e.target.checked)}
                className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500 focus:ring-offset-0"
              />
              
              <div className="flex items-center gap-2">
                <FolderIcon className="h-5 w-5 text-gray-600" />
                <div>
                  <span className="text-sm font-semibold text-gray-900">Google Drive</span>
                  <span className="ml-2 text-xs text-gray-500">{userEmail || 'Loading...'}</span>
                </div>
              </div>
              <div className="flex-1"></div>
              <span className="text-sm text-gray-500">{selectedItems.length}</span>
              <div className="flex items-center gap-1">
                <Button
                  variant="outline"
                  size="sm"
                  className="h-7 px-3 text-xs border-gray-200 hover:bg-gray-50 text-gray-700"
                >
                  Manage
                </Button>
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="h-7 w-7 p-0 hover:bg-gray-100 mr-1"
                    >
                      <MoreHorizontal className="h-4 w-4 text-gray-400" />
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end" className="w-48">
                    <DropdownMenuItem disabled className="text-gray-400 cursor-not-allowed">
                      Sync connection
                    </DropdownMenuItem>
                    <DropdownMenuItem disabled className="text-gray-400 cursor-not-allowed">
                      Disconnect
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              </div>
            </div>

            {/* Child Files - Scrollable Container */}
            {isExpanded && (
              <div className="flex-1 overflow-y-auto min-h-0">
                {/* Initial loading state - shown in scrollable area */}
                {isLoading && processedFiles.length === 0 && !currentResourceId ? (
                  <div className="p-4">
                    <FolderLoadingSkeleton />
                  </div>
                ) : 
                /* Empty state - only when not loading, no error, and no files */
                !isLoading && processedFiles.length === 0 && !currentResourceId ? (
                  <EmptyState />
                ) : 
                /* Folder navigation loading */
                isLoading && processedFiles.length === 0 ? (
                  <div className="p-4">
                    <FolderLoadingSkeleton />
                  </div>
                ) : (
                  /* File list */
                  processedFiles.map((file) => (
                    <FileItem
                      key={file.resource_id}
                      file={file}
                      isSelected={selectedItems.includes(file.resource_id)}
                      onSelect={onItemSelect}
                      onOpen={handleFolderOpen}
                      isChild={true}
                    />
                  ))
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </>
  );
}


// Folder navigation loading skeleton - more compact for the scrollable area
function FolderLoadingSkeleton() {
  return (
    <div className="space-y-1">
      {Array.from({ length: 4 }, (_, i) => (
        <div key={i} className="flex items-center gap-3 py-2 pl-12 pr-3">
          <Skeleton className="h-4 w-4" />
          <Skeleton className="h-5 w-5" />
          <div className="flex-1">
            <Skeleton className="h-4 w-2/3" />
          </div>
          <Skeleton className="h-4 w-8" />
          <Skeleton className="h-7 w-16" />
          <Skeleton className="h-7 w-7" />
        </div>
      ))}
    </div>
  );
}

// Empty state component
function EmptyState() {
  return (
    <div className="flex flex-col items-center justify-center p-8 text-center">
      <div className="text-6xl mb-4">📁</div>
      <h3 className="text-lg font-semibold text-gray-900 mb-2">
        No Files Found
      </h3>
      <p className="text-gray-600">
        This folder appears to be empty or no files match your search.
      </p>
    </div>
  );
}





// Coming Soon component for non-implemented integrations
function ComingSoonContent({ integration }: { integration: Integration }) {
  return (
    <div className="flex-1 flex items-center justify-center p-8">
      <div className="bg-gray-50 rounded-xl p-4 max-w-md">
        <div className="inline-flex items-center gap-2 text-sm text-gray-500 bg-gray-100 px-3 py-2 rounded-md mb-4">
          <div className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-pulse"></div>
          Coming Soon
        </div>
        <p className="text-gray-600 leading-relaxed text-sm">
          We&apos;re working on bringing {integration.name} integration to StackAI. 
          This feature will be available soon.
        </p>
      </div>
    </div>
  );
}

// Placeholder components for other integrations
function FilesContent() {
  return <ComingSoonContent integration={{ id: 'files', name: 'Files', icon: 'FileText' }} />;
}

function WebsitesContent() {
  return <ComingSoonContent integration={{ id: 'websites', name: 'Websites', icon: 'Globe' }} />;
}

function TextContent() {
  return <ComingSoonContent integration={{ id: 'text', name: 'Text', icon: 'Edit3' }} />;
}

function ConfluenceContent() {
  return <ComingSoonContent integration={{ id: 'confluence', name: 'Confluence', icon: '/confluence_icon.svg' }} />;
}

function NotionContent() {
  return <ComingSoonContent integration={{ id: 'notion', name: 'Notion', icon: '/notion_icon.svg' }} />;
}

function OneDriveContent() {
  return <ComingSoonContent integration={{ id: 'onedrive', name: 'OneDrive', icon: '/onedrive_icon.svg' }} />;
}

function SharePointContent() {
  return <ComingSoonContent integration={{ id: 'sharepoint', name: 'SharePoint', icon: '/sharepoint_icon.png' }} />;
}

function SlackContent() {
  return <ComingSoonContent integration={{ id: 'slack', name: 'Slack', icon: '/slack_icon.svg.png' }} />;
}

function DefaultContent({ integration }: { integration: Integration }) {
  return <ComingSoonContent integration={integration} />;
} 