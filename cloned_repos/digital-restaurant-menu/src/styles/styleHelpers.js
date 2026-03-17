// Tailwind CSS styling utilities and theme helpers

export const buttonStyles = {
  primary: 'bg-amber-600 hover:bg-amber-700 text-white font-semibold py-2 px-4 rounded-lg transition-colors',
  secondary: 'bg-stone-700 hover:bg-stone-600 text-amber-100 font-semibold py-2 px-4 rounded-lg border border-amber-600 border-opacity-30 transition-colors',
  danger: 'bg-red-600 hover:bg-red-700 text-white font-semibold py-2 px-4 rounded-lg transition-colors',
  text: 'text-amber-600 hover:text-amber-700 font-semibold cursor-pointer transition-colors',
};

export const cardStyles = {
  default: 'bg-stone-800 rounded-lg p-6 border border-amber-600 border-opacity-20 hover:border-opacity-40 transition-all',
  highlighted: 'bg-gradient-to-r from-amber-900 to-amber-800 rounded-lg p-6 border-2 border-amber-600',
  minimal: 'bg-stone-700 bg-opacity-50 rounded-lg p-4',
};

export const textStyles = {
  heading1: 'text-6xl font-bold text-amber-50 tracking-tight drop-shadow-lg',
  heading2: 'text-3xl font-bold text-amber-400 uppercase tracking-wider',
  heading3: 'text-xl font-semibold text-amber-100',
  body: 'text-stone-300 text-sm',
  caption: 'text-stone-400 text-xs',
  label: 'text-amber-200 font-medium text-sm',
};

export const containerStyles = {
  page: 'min-h-screen bg-gradient-to-br from-stone-900 via-stone-800 to-stone-900 py-12 px-4',
  maxWidth: 'max-w-5xl mx-auto',
  section: 'space-y-12',
};

export const tagColor = (tag) => {
  const colors = {
    signature: 'bg-amber-700 text-amber-100',
    premium: 'bg-red-700 text-red-100',
    seasonal: 'bg-green-700 text-green-100',
    vegetarian: 'bg-green-600 text-green-100',
    vegan: 'bg-green-700 text-green-100',
    seafood: 'bg-blue-700 text-blue-100',
    healthy: 'bg-teal-700 text-teal-100',
  };
  return colors[tag] || 'bg-amber-900 bg-opacity-50 text-amber-200';
};

export const getResponsiveClasses = (mobile, tablet, desktop) => {
  return `${mobile} md:${tablet} lg:${desktop}`;
};

// Theme configuration
export const theme = {
  colors: {
    primary: '#B45309', // amber-600
    secondary: '#78350f', // amber-900
    accent: '#FCD34D', // amber-300
    background: '#1C1917', // stone-900
    surface: '#292524', // stone-800
    text: '#FEF3C7', // amber-50
    disabled: '#78716C', // stone-600
  },
  spacing: {
    xs: '0.25rem',
    sm: '0.5rem',
    md: '1rem',
    lg: '1.5rem',
    xl: '2rem',
  },
  borderRadius: {
    sm: '0.375rem',
    md: '0.5rem',
    lg: '0.75rem',
    full: '9999px',
  },
  transitions: {
    fast: '150ms ease-in-out',
    normal: '300ms ease-in-out',
    slow: '500ms ease-in-out',
  },
};
