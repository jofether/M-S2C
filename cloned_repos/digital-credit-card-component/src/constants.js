/**
 * Constants for the Digital Wallet Application
 */

// Card brands and their properties
export const CARD_BRANDS = {
  VISA: { name: 'Visa', regex: /^4/, color: 'from-blue-600 to-blue-900' },
  MASTERCARD: { name: 'Mastercard', regex: /^5[1-5]/, color: 'from-red-600 to-orange-900' },
  AMEX: { name: 'American Express', regex: /^3[47]/, color: 'from-green-600 to-teal-900' },
  DISCOVER: { name: 'Discover', regex: /^6(?:011|5)/, color: 'from-orange-600 to-yellow-900' },
  DEFAULT: { name: 'Card', regex: /./, color: 'from-purple-600 to-indigo-900' },
};

// Transaction categories
export const TRANSACTION_CATEGORIES = [
  'Shopping',
  'Food',
  'Transport',
  'Entertainment',
  'Utilities',
  'Health',
  'Education',
  'Travel',
  'Services',
];

// Security levels
export const SECURITY_LEVELS = {
  EXCELLENT: { label: 'Excellent', score: 90, color: 'text-green-600' },
  GOOD: { label: 'Good', score: 75, color: 'text-blue-600' },
  FAIR: { label: 'Fair', score: 60, color: 'text-yellow-600' },
  POOR: { label: 'Poor', score: 40, color: 'text-red-600' },
};

// Validation rules
export const VALIDATION_RULES = {
  CARD_NUMBER_LENGTH: 16,
  CVV_MIN_LENGTH: 3,
  CVV_MAX_LENGTH: 4,
  EXPIRY_FORMAT: /^(0[1-9]|1[0-2])\/\d{2}$/,
};

// Messages
export const MESSAGES = {
  CARD_ADDED: 'Card added successfully!',
  CARD_DELETED: 'Card deleted successfully!',
  CARD_LOCKED: 'Card has been locked',
  CARD_UNLOCKED: 'Card has been unlocked',
  ERROR_INVALID_CARD: 'Invalid card details provided',
  ERROR_NUMERIC_ONLY: 'Only numeric characters allowed',
  SUCCESS: 'Operation completed successfully',
  ERROR: 'An error occurred. Please try again.',
};
