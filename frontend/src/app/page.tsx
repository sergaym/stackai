'use client';

import Image from 'next/image'
import { FilePickerButton } from '@/components/file-picker'

export default function Home() {
  return (
    <main className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <div className="text-center space-y-2 max-w-sm">
        {/* Clean logo */}
        <div className="flex justify-center">
          <div className="p-2 rounded-xl">
            <Image src="/stackai_logo.svg" alt="Stack AI" width={48} height={48} className="h-14 w-14" />
          </div>
        </div>
        
        {/* Minimal heading */}
        <div className="space-y-2">
          <h1 className="text-2xl font-bold text-gray-900">Stack AI File Picker</h1>
          <p className="text-gray-600">
            Index your Google Drive files with AI.
          </p>
        </div>
        
        {/* Simple CTA */}
        <FilePickerButton />
      </div>
    </main>
  )
}
