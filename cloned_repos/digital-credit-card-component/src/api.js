/**
 * API service layer (mock)
 * In a real application, this would connect to a backend
 */

// Mock API delay
const delay = (ms = 500) => new Promise(resolve => setTimeout(resolve, ms));

/**
 * Card API calls
 */
export const cardAPI = {
  /**
   * Fetch all cards for user
   */
  getCards: async () => {
    await delay();
    return Promise.resolve([
      {
        id: 1,
        number: '4532 1098 7654 3210',
        holder: 'Jofether Mendoza',
        expiry: '12/28',
        cvv: '123',
        balance: 5250.00,
        creditLimit: 10000.00,
      },
    ]);
  },

  /**
   * Create new card
   */
  createCard: async (cardData) => {
    await delay();
    return Promise.resolve({
      id: Date.now(),
      ...cardData,
      balance: 0,
      creditLimit: 5000,
    });
  },

  /**
   * Delete card
   */
  deleteCard: async (cardId) => {
    await delay();
    return Promise.resolve({ success: true, cardId });
  },

  /**
   * Update card
   */
  updateCard: async (cardId, updates) => {
    await delay();
    return Promise.resolve({ id: cardId, ...updates });
  },

  /**
   * Lock card
   */
  lockCard: async (cardId) => {
    await delay();
    return Promise.resolve({ cardId, status: 'locked' });
  },

  /**
   * Unlock card
   */
  unlockCard: async (cardId) => {
    await delay();
    return Promise.resolve({ cardId, status: 'active' });
  },
};

/**
 * Transaction API calls
 */
export const transactionAPI = {
  /**
   * Get transactions for a card
   */
  getTransactions: async (cardId) => {
    await delay();
    return Promise.resolve([]);
  },

  /**
   * Get all user transactions
   */
  getAllTransactions: async () => {
    await delay();
    return Promise.resolve([]);
  },

  /**
   * Create transaction
   */
  createTransaction: async (transactionData) => {
    await delay();
    return Promise.resolve({
      id: Date.now(),
      ...transactionData,
    });
  },

  /**
   * Get spending statistics
   */
  getSpendingStats: async (period = 'month') => {
    await delay();
    return Promise.resolve({
      total: 0,
      byCategory: {},
      byMerchant: {},
    });
  },
};

/**
 * User API calls
 */
export const userAPI = {
  /**
   * Get user profile
   */
  getProfile: async () => {
    await delay();
    return Promise.resolve({
      id: 1,
      name: 'Jofether Mendoza',
      email: 'jofether@example.com',
    });
  },

  /**
   * Update profile
   */
  updateProfile: async (profileData) => {
    await delay();
    return Promise.resolve(profileData);
  },

  /**
   * Get security settings
   */
  getSecuritySettings: async () => {
    await delay();
    return Promise.resolve({
      twoFactorEnabled: true,
      fraudProtection: true,
      purchaseAlerts: true,
    });
  },

  /**
   * Update security settings
   */
  updateSecuritySettings: async (settings) => {
    await delay();
    return Promise.resolve(settings);
  },
};

export default {
  cardAPI,
  transactionAPI,
  userAPI,
};
