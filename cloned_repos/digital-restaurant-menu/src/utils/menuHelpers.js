// Utility functions for menu operations
export const filterMenuItems = (items, searchTerm) => {
  if (!searchTerm.trim()) return items;
  
  const term = searchTerm.toLowerCase();
  return items.filter(item => 
    item.name.toLowerCase().includes(term) ||
    item.desc.toLowerCase().includes(term) ||
    (item.tags && item.tags.some(tag => tag.toLowerCase().includes(term)))
  );
};

export const formatPrice = (price) => {
  // Removes $ and returns numeric value
  return parseFloat(price.replace('$', ''));
};

export const priceRange = (items) => {
  const prices = items.map(item => formatPrice(item.price));
  return {
    min: Math.min(...prices),
    max: Math.max(...prices),
  };
};

export const getItemsByTag = (items, tag) => {
  return items.filter(item => item.tags && item.tags.includes(tag));
};

export const getSignatureDishes = (items) => {
  return getItemsByTag(items, 'signature');
};

export const getVegetarianItems = (items) => {
  return items.filter(item => item.tags && item.tags.includes('vegetarian'));
};

export const getVeganItems = (items) => {
  return items.filter(item => item.tags && item.tags.includes('vegan'));
};

export const getSeafoodItems = (items) => {
  return items.filter(item => item.tags && item.tags.includes('seafood'));
};

export const getPremiumItems = (items) => {
  return getItemsByTag(items, 'premium');
};

export const sortByPrice = (items, ascending = true) => {
  return [...items].sort((a, b) => {
    const priceA = formatPrice(a.price);
    const priceB = formatPrice(b.price);
    return ascending ? priceA - priceB : priceB - priceA;
  });
};

export const sortByName = (items, ascending = true) => {
  return [...items].sort((a, b) => {
    const comparison = a.name.localeCompare(b.name);
    return ascending ? comparison : -comparison;
  });
};

export const getItemStats = (items) => {
  const allItems = items.flatMap(cat => cat.items);
  const prices = allItems.map(item => formatPrice(item.price));
  
  return {
    totalItems: allItems.length,
    averagePrice: (prices.reduce((a, b) => a + b, 0) / prices.length).toFixed(2),
    minPrice: '$' + Math.min(...prices).toFixed(2),
    maxPrice: '$' + Math.max(...prices).toFixed(2),
    vegetarianCount: getVegetarianItems(allItems).length,
    seafoodCount: getSeafoodItems(allItems).length,
  };
};
