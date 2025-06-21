'use client';

import { useState } from 'react';
import { X } from 'lucide-react';
import { clsx } from 'clsx';
import { Button } from '@/components/ui/button';
import { IntegrationIcon } from '@/components/ui/integration-icon';
import type { Integration } from '@/types';
import type { FilePickerDialogProps } from './types';
import { IntegrationContent } from './integration-content';

const integrations: Integration[] = [
  { id: 'files', name: 'Files', icon: 'FileText', count: 4 },
  { id: 'websites', name: 'Websites', icon: 'Globe' },
  { id: 'text', name: 'Text', icon: 'Edit3' },
  { id: 'confluence', name: 'Confluence', icon: '/confluence_icon.svg' },
  { id: 'notion', name: 'Notion', icon: '/notion_icon.svg' },
  { id: 'googledrive', name: 'Google Drive', icon: '/google_drive_icon.png', isActive: true },
  { id: 'onedrive', name: 'OneDrive', icon: '/onedrive_icon.svg' },
  { id: 'sharepoint', name: 'SharePoint', icon: '/sharepoint_icon.png' },
  { id: 'slack', name: 'Slack', icon: '/slack_icon.png' }
];

export function FilePickerDialog({ isOpen, onClose }: FilePickerDialogProps) {
  const [selectedItems, setSelectedItems] = useState<string[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [activeIntegration, setActiveIntegration] = useState('googledrive');

  const handleItemSelect = (id: string) => {
    setSelectedItems(prev => 
      prev.includes(id) 
        ? prev.filter(item => item !== id)
        : [...prev, id]
    );
  };

  const handleImport = () => {
    console.log('Importing selected files:', selectedItems);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 bg-black/50 flex items-center justify-center">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-5xl h-[80vh] flex overflow-hidden">
        {/* Sidebar - Fixed Width and Height */}
        <div className="w-56 bg-gray-50 border-r border-gray-200 flex flex-col flex-shrink-0">
          <div className="px-3 py-3 border-b border-gray-200 flex items-center gap-2">
            <Button 
              onClick={onClose}
              variant="ghost"
              size="icon"
              className="h-6 w-6 text-gray-400 hover:text-gray-600 hover:bg-gray-100 p-0"
            >
              <X className="h-4 w-4" />
            </Button>
            <h2 className="text-sm font-semibold text-gray-900">Integrations</h2>
          </div>

          {/* Integrations Label */}
          <div className="px-3 pt-4 pb-2">
            <div className="text-xs font-semibold text-gray-400 text-left">
              Integrations
            </div>
          </div>
          
          <div className="flex-1 overflow-y-auto px-2 space-y-0.5">
            {integrations.map((integration) => (
              <button
                key={integration.id}
                onClick={() => setActiveIntegration(integration.id)}
                className={clsx(
                  'w-full flex items-center gap-2.5 px-2 py-1.5 text-left rounded-sm transition-colors',
                  'hover:bg-gray-100 text-gray-700 text-sm',
                  activeIntegration === integration.id ? 'bg-gray-200 text-gray-900' : ''
                )}
              >
                <IntegrationIcon icon={integration.icon} name={integration.name} withBackground={true} />
                <span className="flex-1 font-normal">
                  {integration.name}
                </span>
                {integration.count && (
                  <span className="text-xs text-blue-600 font-medium">
                    {integration.count}
                  </span>
                )}
              </button>
            ))}
          </div>
        </div>

        {/* Right Side - Content + Footer */}
        <div className="flex-1 flex flex-col min-w-0">
          {/* Main Content */}
          <div className="flex-1 overflow-y-auto min-h-0">
            <IntegrationContent
              integration={integrations.find(i => i.id === activeIntegration) || integrations[0]}
              selectedItems={selectedItems}
              onItemSelect={handleItemSelect}
              searchTerm={searchTerm}
              onSearchChange={setSearchTerm}
            />
          </div>

          {/* Footer - Only spans right side */}
          <div className="px-6 py-4 border-t border-gray-200 flex items-center justify-end gap-4">
            <div className="flex items-center gap-2 text-sm text-gray-600 bg-gray-50 px-3 py-2 rounded-md">
              <span className="text-gray-500">ⓘ</span>
              <span>We recommend selecting as few items as needed.</span>
            </div>
            <div className="flex items-center gap-2">
              <Button variant="outline" onClick={onClose}>
                Cancel
              </Button>
              <Button 
                onClick={handleImport}
                disabled={selectedItems.length === 0}
                className="bg-blue-600 hover:bg-blue-700 text-white"
              >
                Select {selectedItems.length > 0 ? selectedItems.length : ''}
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
} 