// Testing utilities and mock data generators

export const generateMockMenuItem = (overrides = {}) => {
  return {
    name: 'Sample Dish',
    price: '$15.00',
    desc: 'A delicious sample dish',
    tags: ['signature'],
    ...overrides,
  };
};

export const generateMockOrder = () => {
  return {
    id: `ORD-${Date.now()}`,
    items: [
      generateMockMenuItem({ name: 'Item 1' }),
      generateMockMenuItem({ name: 'Item 2' }),
    ],
    quantities: { 'Item 1': 1, 'Item 2': 2 },
    createdAt: new Date(),
  };
};

export const mockMenuCategories = [
  {
    title: 'Test Appetizers',
    items: [
      generateMockMenuItem({ name: 'Test Appetizer 1' }),
      generateMockMenuItem({ name: 'Test Appetizer 2' }),
    ],
  },
  {
    title: 'Test Main Courses',
    items: [
      generateMockMenuItem({ name: 'Test Main 1' }),
      generateMockMenuItem({ name: 'Test Main 2' }),
    ],
  },
];

// Test data validation
export const validateMenuItem = (item) => {
  const errors = [];
  
  if (!item.name || typeof item.name !== 'string') {
    errors.push('Item must have a valid name');
  }
  
  if (!item.price || !item.price.match(/^\$\d+\.\d{2}$/)) {
    errors.push('Item must have a valid price in format $X.XX');
  }
  
  if (!item.desc || typeof item.desc !== 'string') {
    errors.push('Item must have a description');
  }
  
  if (item.tags && !Array.isArray(item.tags)) {
    errors.push('Tags must be an array');
  }
  
  return {
    valid: errors.length === 0,
    errors,
  };
};

export const validateMenuCategory = (category) => {
  const errors = [];
  
  if (!category.title || typeof category.title !== 'string') {
    errors.push('Category must have a valid title');
  }
  
  if (!Array.isArray(category.items) || category.items.length === 0) {
    errors.push('Category must have at least one item');
  }
  
  category.items?.forEach((item, index) => {
    const validation = validateMenuItem(item);
    if (!validation.valid) {
      errors.push(`Item ${index}: ${validation.errors.join(', ')}`);
    }
  });
  
  return {
    valid: errors.length === 0,
    errors,
  };
};
