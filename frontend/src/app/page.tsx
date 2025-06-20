'use client';

import { FilePickerButton } from '@/components/file-picker';

export default function Home() {
  return (
    <main className="min-h-screen bg-gray-100 flex flex-col items-center justify-center px-4">
      <FilePickerButton />
    </main>
  );
}
