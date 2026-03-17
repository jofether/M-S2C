/**
 * Card utility functions
 */

export const generateCardId = () => Date.now();

export const maskCardNumber = (number) => {
  const lastFour = number.slice(-4);
  const masked = number.slice(0, -4).replace(/\d/g, '•');
  return masked + lastFour;
};

export const detectCardBrand = (number) => {
  const num = number.replace(/\s/g, '');
  
  if (/^4/.test(num)) {
    return { name: 'Visa', color: 'from-blue-600 to-blue-900', icon: '💳' };
  }
  if (/^5[1-5]/.test(num)) {
    return { name: 'Mastercard', color: 'from-red-600 to-orange-900', icon: '💳' };
  }
  if (/^3[47]/.test(num)) {
    return { name: 'Amex', color: 'from-green-600 to-teal-900', icon: '💳' };
  }
  if (/^6(?:011|5)/.test(num)) {
    return { name: 'Discover', color: 'from-orange-600 to-yellow-900', icon: '💳' };
  }
  
  return { name: 'Card', color: 'from-purple-600 to-indigo-900', icon: '💳' };
};

export const validateCardNumber = (number) => {
  const cardNum = number.replace(/\s/g, '');
  return cardNum.length === 16 && /^\d+$/.test(cardNum);
};

export const validateExpiry = (expiry) => {
  const expiryRegex = /^(0[1-9]|1[0-2])\/\d{2}$/;
  return expiryRegex.test(expiry);
};

export const validateCVV = (cvv) => {
  return /^\d{3,4}$/.test(cvv);
};

export const validateCardForm = (formData) => {
  const errors = {};

  if (!validateCardNumber(formData.number)) {
    errors.number = 'Card number must be 16 digits';
  }

  if (!formData.holder.trim()) {
    errors.holder = 'Cardholder name is required';
  }

  if (!validateExpiry(formData.expiry)) {
    errors.expiry = 'Expiry must be in MM/YY format';
  }

  if (!validateCVV(formData.cvv)) {
    errors.cvv = 'CVV must be 3-4 digits';
  }

  return errors;
};

export const formatCardNumber = (value) => {
  const cardNum = value.replace(/\D/g, '').slice(0, 16);
  return cardNum.replace(/(\d{4})(?=\d)/g, '$1 ');
};

export const formatExpiry = (value) => {
  const formatted = value.replace(/\D/g, '').slice(0, 4);
  if (formatted.length >= 2) {
    return formatted.slice(0, 2) + '/' + formatted.slice(2);
  }
  return formatted;
};

export const formatCVV = (value) => {
  return value.replace(/\D/g, '').slice(0, 4);
};

/**
 * Transaction utilities
 */

export const generateSampleTransactions = () => [
  { id: 1, cardId: 1, merchant: 'Amazon', amount: 45.99, date: '2026-02-15', category: 'Shopping' },
  { id: 2, cardId: 1, merchant: 'Starbucks', amount: 6.50, date: '2026-02-14', category: 'Food' },
  { id: 3, cardId: 1, merchant: 'Uber Eats', amount: 28.45, date: '2026-02-13', category: 'Food' },
  { id: 4, cardId: 1, merchant: 'Netflix', amount: 15.99, date: '2026-02-10', category: 'Entertainment' },
  { id: 5, cardId: 1, merchant: 'Electric Company', amount: 125.00, date: '2026-02-05', category: 'Utilities' },
  { id: 6, cardId: 1, merchant: 'Best Buy', amount: 299.99, date: '2026-01-28', category: 'Shopping' },
  { id: 7, cardId: 1, merchant: 'Target', amount: 87.65, date: '2026-01-25', category: 'Shopping' },
  { id: 8, cardId: 1, merchant: 'Gym Membership', amount: 50.00, date: '2026-01-20', category: 'Health' },
];

/**
 * Date utilities
 */

export const formatDate = (date) => {
  return new Date(date).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
};

export const getCardExpiryMonths = () => {
  const months = [];
  for (let i = 1; i <= 12; i++) {
    months.push(String(i).padStart(2, '0'));
  }
  return months;
};

export const getCardExpiryYears = () => {
  const years = [];
  const currentYear = new Date().getFullYear();
  for (let i = currentYear; i < currentYear + 20; i++) {
    years.push(String(i).slice(-2));
  }
  return years;
};
