import Image from 'next/image';
import { FileText, Globe, Edit3 } from 'lucide-react';

interface IntegrationIconProps {
  icon: string;
  name: string;
  withBackground?: boolean;
}

export function IntegrationIcon({ icon, name, withBackground = false }: IntegrationIconProps) {
  const iconElement = (() => {
    if (icon.startsWith('/')) {
      return (
        <Image
          src={icon}
          alt={`${name} icon`}
          width={16}
          height={16}
          className="w-4 h-4 object-contain"
        />
      );
    }
    
    // Fallback for lucide icons
    switch (icon) {
      case 'FileText':
        return <FileText className="w-4 h-4" />;
      case 'Globe':
        return <Globe className="w-4 h-4" />;
      case 'Edit3':
        return <Edit3 className="w-4 h-4" />;
      default:
        return <span className="text-sm">{icon}</span>;
    }
  })();

  if (withBackground) {
    return (
      <div className="w-6 h-6 flex items-center justify-center bg-white rounded shadow-sm">
        {iconElement}
      </div>
    );
  }

  return (
    <div className="w-5 h-5 flex items-center justify-center">
      {iconElement}
    </div>
  );
} 