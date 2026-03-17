// Mock API service for restaurant data
// In production, replace with actual API calls

const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));

export const restaurantAPI = {
  // Fetch restaurant information
  getRestaurantInfo: async () => {
    await delay(300);
    return {
      name: 'The Rustic Spoon',
      tagline: 'Award-Winning Farm to Table Dining',
      address: '123 Farm Road, Rural District',
      phone: '(555) 123-4567',
      email: 'info@rusticspooon.com',
      hours: {
        monday: '5PM - 11PM',
        tuesday: '5PM - 11PM',
        wednesday: '5PM - 11PM',
        thursday: '5PM - 11PM',
        friday: '5PM - 12AM',
        saturday: '5PM - 12AM',
        sunday: '5PM - 10PM',
      },
      rating: 4.8,
      reviews: 342,
    };
  },

  // Fetch menu
  getMenu: async () => {
    await delay(500);
    return {
      success: true,
      categories: 7,
      items: 56,
      lastUpdated: new Date(),
    };
  },

  // Submit order
  submitOrder: async (orderData) => {
    await delay(1000);
    return {
      success: true,
      orderId: `ORD-${Date.now()}`,
      estimatedTime: 45, // minutes
      message: 'Order received! You will receive a confirmation email shortly.',
    };
  },

  // Get promotions
  getPromotions: async () => {
    await delay(300);
    return [
      {
        id: 1,
        title: 'Happy Hour',
        description: 'Monday-Friday 5PM-7PM: 20% off appetizers',
        active: true,
      },
      {
        id: 2,
        title: 'Wine Wednesday',
        description: 'All wines 30% off on Wednesdays',
        active: true,
      },
      {
        id: 3,
        title: 'Birthday Special',
        description: 'Free dessert with birthday ID',
        active: true,
      },
    ];
  },

  // Make reservation
  makeReservation: async (reservationData) => {
    await delay(800);
    return {
      success: true,
      confirmationCode: `RES-${Date.now()}`,
      message: 'Your reservation has been confirmed!',
    };
  },

  // Get reviews
  getReviews: async () => {
    await delay(400);
    return [
      {
        id: 1,
        author: 'Michael S.',
        rating: 5,
        text: 'Absolutely amazing food and exceptional service. The salmon was perfectly cooked!',
        date: '2 weeks ago',
      },
      {
        id: 2,
        author: 'Sarah T.',
        rating: 5,
        text: 'Best restaurant in the area. Love the farm-to-table concept and fresh ingredients.',
        date: '1 month ago',
      },
      {
        id: 3,
        author: 'James D.',
        rating: 4,
        text: 'Great food, beautiful ambiance. Service was a bit slow on a busy night.',
        date: '1 month ago',
      },
    ];
  },
};

// Order service
export const orderService = {
  calculateTotal: (items, quantities) => {
    const subtotal = items.reduce((sum, item) => {
      const price = parseFloat(item.price.replace('$', ''));
      const qty = quantities[item.name] || 1;
      return sum + (price * qty);
    }, 0);
    const tax = subtotal * 0.12;
    return { subtotal, tax, total: subtotal + tax };
  },

  generateReceipt: (orderData) => {
    return {
      orderId: `ORD-${Date.now()}`,
      timestamp: new Date(),
      items: orderData.items,
      subtotal: orderData.subtotal,
      tax: orderData.tax,
      total: orderData.total,
      paymentMethod: orderData.paymentMethod,
    };
  },
};

// Analytics service
export const analyticsService = {
  trackMenuView: (category) => {
    console.log('Menu viewed:', category);
    // Send to analytics platform
  },

  trackItemClick: (itemName) => {
    console.log('Item clicked:', itemName);
    // Send to analytics platform
  },

  trackOrderSubmission: (total) => {
    console.log('Order submitted:', total);
    // Send to analytics platform
  },
};
