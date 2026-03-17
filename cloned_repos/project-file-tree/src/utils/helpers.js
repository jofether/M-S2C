/**
 * File icon mapping based on extensions
 */
export const FILE_ICONS = {
  jsx: '⚛️', 
  js: '🔶', 
  ts: '🔷', 
  tsx: '⚛️',
  css: '🎨', 
  scss: '🎨', 
  html: '🌐', 
  json: '📋',
  md: '📝', 
  png: '🖼️', 
  jpg: '🖼️', 
  svg: '🎭',
  ico: '🔗', 
  txt: '📄', 
  java: '☕', 
  py: '🐍', 
  rb: '💎', 
  php: '🐘',
  config: '⚙️', 
  lock: '🔒', 
  env: '🔑',
  yarn: '🧶',
  npm: '📦'
};

/**
 * Default file icon for unknown types
 */
export const DEFAULT_FILE_ICON = '📄';

/**
 * Color palette
 */
export const COLORS = {
  primary: 'from-blue-500 to-purple-600',
  success: 'from-green-400 to-green-600',
  warning: 'from-yellow-400 to-yellow-600',
  danger: 'from-red-400 to-red-600',
};

/**
 * Common file stats
 */
export const DEFAULT_STATS = {
  totalFiles: 24,
  totalFolders: 8,
  projectSize: '2.4 MB'
};

/**
 * Feature list
 */
export const FEATURES = [
  {
    icon: '🔍',
    title: 'Smart Search',
    description: 'Instantly filter through hundreds of files with powerful search capabilities'
  },
  {
    icon: '🎯',
    title: 'Quick Navigation',
    description: 'Organize your project structure with intuitive folder hierarchy visualization'
  },
  {
    icon: '📋',
    title: 'Copy & Paste',
    description: 'Right-click any file to copy its path directly to your clipboard'
  },
  {
    icon: '🎨',
    title: 'Beautiful Design',
    description: 'Modern UI with smooth animations and gradient backgrounds'
  }
];

/**
 * Get icon for file based on extension
 * @param {string} filename - File name
 * @returns {string} Icon emoji
 */
export function getFileIcon(filename) {
  const ext = filename.split('.').pop().toLowerCase();
  return FILE_ICONS[ext] || DEFAULT_FILE_ICON;
}

/**
 * Format file size
 * @param {number} bytes - File size in bytes
 * @returns {string} Formatted file size
 */
export function formatFileSize(bytes) {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

/**
 * Copy text to clipboard
 * @param {string} text - Text to copy
 * @returns {Promise<boolean>} Success status
 */
export async function copyToClipboard(text) {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch (err) {
    console.error('Failed to copy:', err);
    return false;
  }
}
