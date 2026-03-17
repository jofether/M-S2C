// Application constants and configuration

export const AIRLINES = [
  { id: 1, name: 'Asian Airlines', logo: '✈️' },
  { id: 2, name: 'Pacific Airways', logo: '✈️' },
  { id: 3, name: 'Sky Express', logo: '✈️' },
  { id: 4, name: 'Travel Direct', logo: '✈️' },
  { id: 5, name: 'Global Airlines', logo: '✈️' },
];

export const AIRPORTS = {
  MNL: 'Ninoy Aquino International',
  NRT: 'Narita International',
  NYC: 'John F. Kennedy',
  LAX: 'Los Angeles International',
  LHR: 'London Heathrow',
  CDG: 'Paris Charles de Gaulle',
  SYD: 'Sydney Kingsford Smith',
  MEL: 'Melbourne Airport',
};

export const POPULAR_ROUTES = [
  { from: 'MNL', to: 'NRT', price: '$189' },
  { from: 'NYC', to: 'LAX', price: '$149' },
  { from: 'LHR', to: 'CDG', price: '$89' },
  { from: 'SYD', to: 'MEL', price: '$79' },
];

export const PROMO_OFFERS = [
  {
    icon: '🎉',
    title: 'Summer Flash Sale',
    description: 'Get up to 50% off on selected flights',
    discount: 'Save Now',
  },
  {
    icon: '🎁',
    title: 'Loyalty Rewards',
    description: 'Earn points on every booking',
    discount: 'Join Free',
  },
  {
    icon: '✈️',
    title: 'Weekend Getaways',
    description: 'Last-minute deals on weekend trips',
    discount: 'Book Today',
  },
];

export const STATS = [
  { icon: '✈️', number: '50K+', label: 'Flights Daily' },
  { icon: '🌍', number: '195+', label: 'Countries' },
  { icon: '💰', number: '$2B+', label: 'Saved Annually' },
  { icon: '😊', number: '4.8★', label: 'Customer Rating' },
];

export const TESTIMONIALS = [
  {
    name: 'Sarah Johnson',
    rating: 5,
    comment: 'Amazing experience! Found the perfect flight at an unbeatable price. Will definitely book again with TravelGo.',
    date: '2 weeks ago',
    image: '👩',
  },
  {
    name: 'Michael Chen',
    rating: 5,
    comment: 'Super easy to use website and great customer service. They helped me change my flight without any issues.',
    date: '1 month ago',
    image: '👨',
  },
  {
    name: 'Emma Davis',
    rating: 4,
    comment: 'Good prices and smooth booking process. Only wish there were more flight options for my specific route.',
    date: '3 weeks ago',
    image: '👩',
  },
];

export const FAQ_ITEMS = [
  {
    question: 'How far in advance should I book a flight?',
    answer: 'Typically, booking 1-2 months in advance offers the best prices. For domestic flights, 3-4 weeks is usually sufficient. However, prices can vary significantly based on travel season and destination, so using our price comparison tool is recommended.',
  },
  {
    question: 'Can I change or cancel my flight?',
    answer: 'Most tickets allow cancellations or changes, though fees may apply depending on the airline and ticket type. We recommend checking the specific terms when booking. Travel insurance can provide additional coverage for unforeseen circumstances.',
  },
  {
    question: 'What are your baggage policies?',
    answer: 'Baggage allowances vary by airline and ticket class. Most economy flights include one checked bag and a carry-on, while premium classes offer more baggage. You can view specific policies for each flight during the booking process.',
  },
  {
    question: 'Is my payment information secure?',
    answer: 'Yes, we use industry-leading encryption and security protocols. All payments are processed through secure payment gateways with SSL certificates to protect your personal and financial information.',
  },
  {
    question: 'Do you offer group discounts?',
    answer: 'We offer special rates for group bookings of 10 or more passengers. Please contact our customer support team for custom quotes and booking arrangements.',
  },
  {
    question: 'Can I get a refund?',
    answer: 'Refund eligibility depends on your ticket type and the airline\'s policy. Non-refundable tickets cannot be refunded but can usually be converted to travel credits. Flexible tickets can be refunded directly to your original payment method.',
  },
];

export const COLORS = {
  primary: '#2563eb',
  secondary: '#1d4ed8',
  success: '#10b981',
  warning: '#f59e0b',
  danger: '#ef4444',
  light: '#f9fafb',
  dark: '#111827',
};

export const BREAKPOINTS = {
  mobile: '640px',
  tablet: '768px',
  desktop: '1024px',
  wide: '1280px',
};

export const ANIMATION_DURATION = {
  fast: '150ms',
  normal: '300ms',
  slow: '500ms',
};
