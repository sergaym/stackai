'use client';

import { useState } from 'react';
import { Search, ChevronDown, Folder, File } from 'lucide-react';
import { clsx } from 'clsx';
import { Button } from '@/components/ui/button';
import { IntegrationIcon } from '@/components/ui/integration-icon';
import type { FileItem, Integration } from '@/types';

// Mock data - in real app this would come from API
const mockGoogleDriveFiles: FileItem[] = [
  {
    id: 'root',
    name: 'Google Drive',
    type: 'folder',
    modifiedDate: '2024-01-15',
    status: 'resource',
    isExpanded: true,
    children: [
      {
        id: '1',
        name: 'test',
        type: 'folder',
        modifiedDate: '2024-01-15',
        status: 'resource'
      },
      {
        id: '2',
        name: 'Rutadelaseadamenu_MARZO_2023.pdf',
        type: 'file',
        size: 2048,
        modifiedDate: '2024-01-14',
        status: 'indexed'
      }
    ]
  }
];

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
    <div className="flex-1 flex flex-col p-6">
      {/* Dynamic Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <IntegrationIcon icon={integration.icon} name={integration.name} withBackground={true} />
          <span className="font-medium text-gray-900">{integration.name}</span>
          {integration.id === 'googledrive' && (
            <span className="text-xs text-gray-600 bg-gray-100 px-2 py-0.5 rounded">
              Beta
            </span>
          )}
        </div>
        <div className="flex items-center gap-2">
          {integration.id === 'googledrive' && (
            <Button variant="secondary" size="sm">
              + Add account
            </Button>
          )}
        </div>
      </div>
      
      {/* Separator */}
      <div className="border-b border-gray-200 mb-4"></div>

      {/* Dynamic Content */}
      {renderContent()}
    </div>
  );
}

// Google Drive specific content
function GoogleDriveContent({ selectedItems, onItemSelect, searchTerm, onSearchChange }: {
  selectedItems: string[];
  onItemSelect: (id: string) => void;
  searchTerm: string;
  onSearchChange: (term: string) => void;
}) {
  const handleSelectAll = () => {
    // Implementation for select all
  };

  return (
    <>
      {/* Controls */}
      <div className="space-y-4 mb-6">
        <div className="flex items-center justify-between">
          <label className="flex items-center gap-2">
            <input
              type="checkbox"
              onChange={handleSelectAll}
              className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <span className="text-sm text-gray-700">Select all</span>
          </label>
          <span className="text-sm text-gray-500">{selectedItems.length}</span>
        </div>

        <div className="flex items-center gap-4">
          <button className="flex items-center gap-1 text-sm text-gray-600 hover:text-gray-900">
            <span>Sort</span>
            <ChevronDown className="h-4 w-4" />
          </button>
          <button className="flex items-center gap-1 text-sm text-gray-600 hover:text-gray-900">
            <span>Filter</span>
            <ChevronDown className="h-4 w-4" />
          </button>
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search..."
              value={searchTerm}
              onChange={(e) => onSearchChange(e.target.value)}
              className="w-full pl-10 pr-4 py-2.5 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-gray-50"
            />
          </div>
        </div>
      </div>

      {/* File List */}
      <div className="flex-1 overflow-y-auto">
        <div className="space-y-0">
          {mockGoogleDriveFiles.map((item) => (
            <FileTreeItem
              key={item.id}
              item={item}
              level={0}
              selectedItems={selectedItems}
              onSelect={onItemSelect}
            />
          ))}
        </div>
      </div>
    </>
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

// Specific placeholder content for different integration types
function FilesContent() {
  return (
    <ComingSoonContent integration={{ id: 'files', name: 'Files', icon: 'FileText' }} />
  );
}

function WebsitesContent() {
  return (
    <ComingSoonContent integration={{ id: 'websites', name: 'Websites', icon: 'Globe' }} />
  );
}

function TextContent() {
  return (
    <ComingSoonContent integration={{ id: 'text', name: 'Text', icon: 'Edit3' }} />
  );
}

function ConfluenceContent() {
  return (
    <ComingSoonContent integration={{ id: 'confluence', name: 'Confluence', icon: '/confluence_icon.svg' }} />
  );
}

function NotionContent() {
  return (
    <ComingSoonContent integration={{ id: 'notion', name: 'Notion', icon: '/notion_icon.svg' }} />
  );
}

function OneDriveContent() {
  return (
    <ComingSoonContent integration={{ id: 'onedrive', name: 'OneDrive', icon: '/onedrive_icon.svg' }} />
  );
}

function SharePointContent() {
  return (
    <ComingSoonContent integration={{ id: 'sharepoint', name: 'SharePoint', icon: '/sharepoint_icon.png' }} />
  );
}

function SlackContent() {
  return (
    <ComingSoonContent integration={{ id: 'slack', name: 'Slack', icon: '/slack_icon.svg.png' }} />
  );
}

function DefaultContent({ integration }: { integration: Integration }) {
  return (
    <ComingSoonContent integration={integration} />
  );
}

// File tree item component (moved from main dialog)
interface FileTreeItemProps {
  item: FileItem;
  level: number;
  selectedItems: string[];
  onSelect: (id: string) => void;
}

function FileTreeItem({ item, level, selectedItems, onSelect }: FileTreeItemProps) {
  const [isExpanded, setIsExpanded] = useState(item.isExpanded || false);
  
  return (
    <div>
      <div 
        className={clsx(
          'flex items-center gap-3 px-0 py-3 hover:bg-gray-50 cursor-pointer border-b border-gray-100 group',
          selectedItems.includes(item.id) && 'bg-gray-100'
        )}
        style={{ paddingLeft: `${level * 24}px` }}
        onClick={() => onSelect(item.id)}
      >
        {item.type === 'folder' && item.children ? (
          <button 
            onClick={(e) => {
              e.stopPropagation();
              setIsExpanded(!isExpanded);
            }}
            className="h-5 w-5 flex items-center justify-center text-gray-400 hover:text-gray-600"
          >
            <ChevronDown 
              className={clsx(
                'h-4 w-4 transition-transform',
                !isExpanded && '-rotate-90'
              )}
            />
          </button>
        ) : (
          <div className="w-5" />
        )}
        
        <input
          type="checkbox"
          checked={selectedItems.includes(item.id)}
          onChange={() => onSelect(item.id)}
          className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
          onClick={(e) => e.stopPropagation()}
        />
        
        <div className="flex items-center gap-3 flex-1 min-w-0">
          {item.type === 'folder' ? (
            <Folder className="h-5 w-5 text-gray-500 flex-shrink-0" />
          ) : (
            <File className="h-5 w-5 text-red-500 flex-shrink-0" />
          )}
          <span className="text-sm text-gray-900 truncate">{item.name}</span>
        </div>

        <div className="flex items-center gap-6 ml-auto">
          <span className="text-sm text-gray-500 min-w-[20px] text-center">0</span>
          <Button 
            variant="ghost" 
            size="sm" 
            className="text-gray-600 hover:text-gray-900 h-auto px-2 py-1"
            onClick={(e) => e.stopPropagation()}
          >
            {item.type === 'file' ? 'Import' : 'Manage'}
          </Button>
          <button className="h-6 w-6 flex items-center justify-center text-gray-400 hover:text-gray-600 opacity-0 group-hover:opacity-100 transition-opacity">
            <span className="text-lg leading-none">⋯</span>
          </button>
        </div>
      </div>

      {item.children && isExpanded && (
        <div>
          {item.children.map((child) => (
            <FileTreeItem
              key={child.id}
              item={child}
              level={level + 1}
              selectedItems={selectedItems}
              onSelect={onSelect}
            />
          ))}
        </div>
      )}
    </div>
  );
} 