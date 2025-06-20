'use client';

import { useState } from 'react';
import { FileText } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { FilePickerDialog } from './dialog';

export function FilePickerButton() {
  const [isDialogOpen, setIsDialogOpen] = useState(false);

  return (
    <>
      <Button 
        onClick={() => setIsDialogOpen(true)}
        variant="outline" 
        className="gap-2 bg-white hover:bg-gray-50 border-gray-300 text-gray-700 hover:text-gray-900 px-6 py-3 text-base font-medium shadow-sm"
      >
        <FileText className="h-5 w-5" />
        Select Files
      </Button>
      
      <FilePickerDialog 
        isOpen={isDialogOpen} 
        onClose={() => setIsDialogOpen(false)} 
      />
    </>
  );
} 