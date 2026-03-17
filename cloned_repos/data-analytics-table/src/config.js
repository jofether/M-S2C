// Application constants and configuration

export const APP_TITLE = 'Data Analytics Dashboard';
export const APP_VERSION = '1.0.0';
export const APP_AUTHOR = 'Your Organization';

// API Configuration
export const API_BASE_URL = process.env.REACT_APP_API_URL || 'https://api.example.com';
export const API_TIMEOUT = 30000; // 30 seconds

// User Roles
export const USER_ROLES = {
  ADMIN: 'Admin',
  EDITOR: 'Editor',
  VIEWER: 'Viewer',
  GUEST: 'Guest',
};

// User Status
export const USER_STATUS = {
  ACTIVE: 'Active',
  INACTIVE: 'Inactive',
  PENDING: 'Pending',
  SUSPENDED: 'Suspended',
};

// Report Status
export const REPORT_STATUS = {
  DRAFT: 'Draft',
  IN_PROGRESS: 'In Progress',
  COMPLETED: 'Completed',
  ARCHIVED: 'Archived',
};

// Color Palette
export const COLORS = {
  primary: '#4f46e5', // Indigo
  secondary: '#6b7280', // Gray
  success: '#10b981', // Green
  warning: '#f59e0b', // Amber
  danger: '#ef4444', // Red
  info: '#0ea5e9', // Sky
};

// Notification Types
export const NOTIFICATION_TYPES = {
  SUCCESS: 'success',
  ERROR: 'error',
  WARNING: 'warning',
  INFO: 'info',
};

// Date Format Options
export const DATE_FORMATS = {
  FULL: 'MMMM d, yyyy h:mm a',
  DATE: 'MMMM d, yyyy',
  SHORT: 'MMM d',
  TIME: 'h:mm a',
};

// Pagination
export const PAGINATION = {
  DEFAULT_PAGE: 1,
  DEFAULT_PAGE_SIZE: 10,
  PAGE_SIZE_OPTIONS: [10, 25, 50, 100],
};

// Local Storage Keys
export const STORAGE_KEYS = {
  USER_PREFERENCES: 'user_preferences',
  THEME: 'theme',
  SIDEBAR_OPEN: 'sidebar_open',
  RECENT_SEARCHES: 'recent_searches',
};

// Feature Flags
export const FEATURES = {
  ADVANCED_ANALYTICS: true,
  USER_MANAGEMENT: true,
  REPORT_GENERATION: true,
  DATA_EXPORT: true,
  CUSTOM_DASHBOARDS: false,
  API_ACCESS: true,
};

// Error Messages
export const ERROR_MESSAGES = {
  NETWORK_ERROR: 'Network error. Please check your connection.',
  UNAUTHORIZED: 'You do not have permission to access this resource.',
  NOT_FOUND: 'The requested resource was not found.',
  SERVER_ERROR: 'Server error. Please try again later.',
  VALIDATION_ERROR: 'Please check your input and try again.',
};

// Success Messages
export const SUCCESS_MESSAGES = {
  CREATED: 'Successfully created.',
  UPDATED: 'Successfully updated.',
  DELETED: 'Successfully deleted.',
  SAVED: 'Changes saved successfully.',
  EXPORTED: 'Data exported successfully.',
};

// Menu Items
export const MENU_ITEMS = [
  { id: 'dashboard', label: 'Dashboard', icon: '📊', path: '/' },
  { id: 'users', label: 'Users', icon: '👥', path: '/users' },
  { id: 'analytics', label: 'Analytics', icon: '📈', path: '/analytics' },
  { id: 'reports', label: 'Reports', icon: '📝', path: '/reports' },
  { id: 'settings', label: 'Settings', icon: '⚙️', path: '/settings' },
  { id: 'help', label: 'Help & Support', icon: '❓', path: '/help' },
];

// Sidebar Menu Items
export const SIDEBAR_ITEMS = MENU_ITEMS;
