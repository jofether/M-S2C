export const PRODUCTS = [
  {
    id: '1',
    name: 'Premium Wireless Headphones',
    category: 'Electronics',
    price: 149.99,
    originalPrice: 199.99,
    rating: 4.8,
    badge: '-25%',
    description: 'High-quality sound with noise cancellation'
  },
  {
    id: '2',
    name: 'Classic Running Shoes',
    category: 'Footwear',
    price: 89.99,
    originalPrice: null,
    rating: 4.6,
    badge: null,
    description: 'Lightweight and comfortable for daily running'
  },
  {
    id: '3',
    name: 'Designer Watch',
    category: 'Accessories',
    price: 299.99,
    originalPrice: 399.99,
    rating: 4.9,
    badge: '-25%',
    description: 'Elegant timepiece with Swiss movement'
  },
  {
    id: '4',
    name: 'Organic Cotton T-Shirt',
    category: 'Clothing',
    price: 34.99,
    originalPrice: null,
    rating: 4.4,
    badge: null,
    description: 'Sustainable and comfortable everyday wear'
  },
  {
    id: '5',
    name: 'Smart Phone Case',
    category: 'Phone Accessories',
    price: 24.99,
    originalPrice: 34.99,
    rating: 4.7,
    badge: 'NEW',
    description: 'Durable protection with premium materials'
  },
  {
    id: '6',
    name: 'Portable Charger',
    category: 'Electronics',
    price: 59.99,
    originalPrice: null,
    rating: 4.5,
    badge: null,
    description: '20000mAh capacity with fast charging'
  }
];

export const SHIPPING_OPTIONS = [
  { id: 'standard', name: 'Standard Shipping (5-7 days)', price: 15.00 },
  { id: 'express', name: 'Express Shipping (2-3 days)', price: 29.99 },
  { id: 'overnight', name: 'Overnight Shipping', price: 59.99 },
  { id: 'pickup', name: 'In-Store Pickup', price: 0 }
];

export const TAX_RATE = 0.09; // 9% tax
