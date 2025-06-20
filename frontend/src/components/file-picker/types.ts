/**
 * File picker component-specific types
 * Component props only - domain types moved to @/types
 */

export interface FilePickerDialogProps {
  isOpen: boolean;
  onClose: () => void;
} 