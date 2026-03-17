/**
 * Global application constants
 */

// App Info
export const APP_NAME = 'File Tree Explorer';
export const APP_VERSION = '1.0.0';
export const APP_DESCRIPTION = 'Interactive hierarchical file structure viewer';

// Paths
export const BASE_URL = import.meta.env.BASE_URL || '/';
export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:3000';

// Feature Flags
export const FEATURES = {
  SEARCH_ENABLED: true,
  CONTEXT_MENU_ENABLED: true,
  DARK_MODE_ENABLED: false,
  FILE_PREVIEW_ENABLED: false,
};

// Pagination
export const ITEMS_PER_PAGE = 50;

// Timeouts
export const DEBOUNCE_DELAY = 300;
export const ANIMATION_DURATION = 200;

// Storage Keys
export const STORAGE_KEYS = {
  EXPAND_STATE: 'tree_expand_state',
  SEARCH_HISTORY: 'search_history',
  THEME: 'app_theme',
  USER_PREFERENCES: 'user_preferences',
};

// Error Messages
export const ERROR_MESSAGES = {
  CLIPBOARD_COPY_FAILED: 'Failed to copy to clipboard',
  FETCH_FAILED: 'Failed to fetch data',
  INVALID_INPUT: 'Invalid input provided',
};

// Success Messages
export const SUCCESS_MESSAGES = {
  COPIED: 'Copied to clipboard!',
  SAVED: 'Changes saved successfully',
  DELETED: 'Item deleted successfully',
};
