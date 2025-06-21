'use client';

import React, { useCallback } from 'react';
import { clsx } from 'clsx';
import { Button } from '@/components/ui/button';
import { useFileActions } from '@/hooks/useFileActions';
import { getFileIcon, getFileName } from '@/lib/utils';
import { ResourceType, ResourceStatus, type FileResource } from '@/lib/api/stackai-client';
import { CheckCircle, Clock, XCircle } from 'lucide-react';

interface FileItemProps {
  file: FileResource;
  isSelected: boolean;
  onSelect: (id: string) => void;
  onOpen: (file: FileResource) => void;
  isChild?: boolean;
}

// Helper function to get indexing status display
function getIndexingStatus(status: ResourceStatus) {
  switch (status) {
    case ResourceStatus.INDEXED:
      return {
        icon: <CheckCircle className="h-4 w-4 text-green-500" />,
        label: 'Indexed',
        color: 'text-green-600',
        bgColor: 'bg-green-50'
      };
    case ResourceStatus.INDEXING:
    case ResourceStatus.PENDING:
      return {
        icon: <Clock className="h-4 w-4 text-yellow-500" />,
        label: 'Indexing...',
        color: 'text-yellow-600',
        bgColor: 'bg-yellow-50'
      };
    case ResourceStatus.ERROR:
      return {
        icon: <XCircle className="h-4 w-4 text-red-500" />,
        label: 'Error',
        color: 'text-red-600',
        bgColor: 'bg-red-50'
      };
    case ResourceStatus.RESOURCE:
    default:
      return {
        icon: <div className="h-4 w-4 rounded-full border-2 border-gray-300" />,
        label: 'Not indexed',
        color: 'text-gray-500',
        bgColor: 'bg-gray-50'
      };
  }
}

export const FileItem = React.memo<FileItemProps>(({ 
  file, 
  isSelected, 
  onSelect, 
  onOpen, 
  isChild = false 
}) => {
  const isDirectory = file.inode_type === ResourceType.DIRECTORY;
  const fileName = getFileName(file.inode_path.path);
  const fileIcon = getFileIcon(fileName, isDirectory);
  const { deindexFiles } = useFileActions();
  
  // Get indexing status for visual indicators
  const status = getIndexingStatus(file.status);
  const isIndexed = file.status === ResourceStatus.INDEXED;
  const isIndexing = file.status === ResourceStatus.INDEXING || file.status === ResourceStatus.PENDING;

  const handleClick = useCallback(() => {
    if (isDirectory) {
      onOpen(file);
    }
  }, [file, isDirectory, onOpen]);

  const handleSelectChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    e.stopPropagation();
    onSelect(file.resource_id);
  }, [file.resource_id, onSelect]);

  const handleDeindex = useCallback((e: React.MouseEvent) => {
    e.stopPropagation();
    deindexFiles([file.resource_id], [file]);
  }, [file, deindexFiles]);

  return (
    <div 
      className={clsx(
        'flex items-center gap-3 py-2 hover:bg-gray-50 cursor-pointer border-b border-gray-100 last:border-b-0',
        isChild ? 'pl-14 pr-3' : 'px-3',
        isSelected && 'bg-blue-50'
      )}
      onClick={handleClick}
    >
      {/* Selection checkbox */}
      <input
        type="checkbox"
        checked={isSelected}
        onChange={handleSelectChange}
        className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500 focus:ring-offset-0"
        onClick={(e) => e.stopPropagation()}
      />

      {/* File icon and name */}
      <div className="flex items-center gap-2 flex-1 min-w-0">
        <div className="flex-shrink-0">
          {fileIcon}
        </div>
        <span className={clsx(
          'text-sm text-gray-900 truncate',
          isDirectory && 'text-blue-700'
        )}>
          {fileName}
        </span>
        {file.dataloader_metadata?.last_modified_by && !isChild && (
          <span className="text-xs text-gray-500 ml-2 truncate">
            {file.dataloader_metadata.last_modified_by}
          </span>
        )}
      </div>

      {/* Status column - always present for consistent alignment */}
      <div className="flex items-center gap-1 min-w-[80px] justify-end mr-2">
        {!isDirectory && (
          <>
            {status.icon}
            <span className={clsx('text-xs', status.color)}>
              {status.label}
            </span>
          </>
        )}
      </div>

      {/* Action buttons column - always present for consistent alignment */}
      <div className="flex items-center gap-1 flex-shrink-0 min-w-[70px] justify-end mr-2.5">
        {isDirectory ? (
          <span className="text-sm text-gray-500">0</span>
        ) : (
          <>
            {isIndexed ? (
              <Button
                variant="outline"
                size="sm"
                onClick={handleDeindex}
                className="h-7 px-3 text-xs border-red-200 hover:bg-red-50 text-red-700"
              >
                De-index
              </Button>
            ) : isIndexing ? (
              <Button
                variant="outline"
                size="sm"
                disabled
                className="h-7 px-3 text-xs border-yellow-200 bg-yellow-50 text-yellow-700"
              >
                Indexing...
              </Button>
            ) : (
              <Button
                variant="outline"
                size="sm"
                onClick={(e) => {
                  e.stopPropagation();
                  onSelect(file.resource_id);
                }}
                className="h-7 px-3 text-xs border-gray-200 hover:bg-gray-50 text-gray-700"
              >
                Import
              </Button>
            )}
          </>
        )}
      </div>
    </div>
  );
});

FileItem.displayName = 'FileItem'; 