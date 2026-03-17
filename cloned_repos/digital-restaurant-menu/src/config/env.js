// Environment configuration
// Switch between development and production settings

const isDevelopment = process.env.NODE_ENV === 'development';

export const config = {
  // API Configuration
  api: {
    baseURL: isDevelopment 
      ? 'http://localhost:5173/api' 
      : 'https://api.rusticspooon.com',
    timeout: 30000,
    retries: 3,
  },

  // Feature Flags
  features: {
    enableSearch: true,
    enableFilters: true,
    enableOrdering: true,
    enableReservations: true,
    enableReviews: true,
    enableAnalytics: !isDevelopment,
  },

  // Menu Configuration
  menu: {
    itemsPerPage: 20,
    enablePagination: false,
    defaultCategory: 'All',
    searchDebounceMs: 300,
  },

  // Pricing
  pricing: {
    taxRate: 0.12, // 12% VAT
    currency: 'USD',
    currencySymbol: '$',
    acceptedPayments: ['credit-card', 'debit-card', 'digital-wallet'],
  },

  // Theme
  theme: {
    mode: 'dark', // 'light' or 'dark'
    primaryColor: 'amber',
    accentColor: 'stone',
  },

  // Performance
  performance: {
    lazyLoadImages: true,
    enableCache: !isDevelopment,
    cacheDuration: 3600000, // 1 hour
  },

  // Logging
  logging: {
    enableConsoleLogging: isDevelopment,
    enableErrorReporting: !isDevelopment,
    logLevel: isDevelopment ? 'debug' : 'error',
  },
};

// Environment variables
export const env = {
  isDevelopment,
  isProduction: !isDevelopment,
  apiKey: process.env.REACT_APP_API_KEY,
  analyticsId: process.env.REACT_APP_ANALYTICS_ID,
};
