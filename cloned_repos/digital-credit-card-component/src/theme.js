/**
 * Theme configuration for the application
 */

export const theme = {
  colors: {
    primary: '#7c3aed', // purple-600
    secondary: '#4f46e5', // indigo-600
    success: '#10b981', // green-600
    warning: '#f59e0b', // amber-500
    danger: '#ef4444', // red-500
    info: '#3b82f6', // blue-500
    light: '#f3f4f6', // gray-100
    dark: '#1f2937', // gray-800
  },
  
  sizes: {
    cardWidth: 384, // w-96: 24rem
    cardHeight: 240, // h-60: 15rem
    borderRadius: '1rem', // rounded-2xl
  },
  
  animations: {
    duration: {
      fast: '200ms',
      normal: '300ms',
      slow: '500ms',
      slower: '700ms',
    },
  },
  
  shadows: {
    sm: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
    md: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
    lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
    xl: '0 20px 25px -5px rgba(0, 0, 0, 0.1)',
  },
};

export default theme;
