// Custom React hook for menu filtering and search
import { useState, useMemo } from 'react';

export const useMenuFilter = (menuCategories) => {
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [searchTerm, setSearchTerm] = useState('');

  const allItems = useMemo(() => {
    return menuCategories.flatMap(cat => 
      cat.items.map(item => ({ ...item, category: cat.title }))
    );
  }, [menuCategories]);

  const filteredItems = useMemo(() => {
    return allItems.filter(item => {
      const matchesCategory = selectedCategory === 'All' || item.category === selectedCategory;
      const matchesSearch = item.name.toLowerCase().includes(searchTerm.toLowerCase()) || 
                           item.desc.toLowerCase().includes(searchTerm.toLowerCase());
      return matchesCategory && matchesSearch;
    });
  }, [allItems, selectedCategory, searchTerm]);

  return {
    selectedCategory,
    setSelectedCategory,
    searchTerm,
    setSearchTerm,
    filteredItems,
    allItems,
  };
};

// Hook for managing order state
export const useOrder = () => {
  const [items, setItems] = useState([]);
  const [quantities, setQuantities] = useState({});

  const addItem = (item) => {
    if (!items.find(i => i.name === item.name)) {
      setItems([...items, item]);
      setQuantities({ ...quantities, [item.name]: 1 });
    }
  };

  const removeItem = (itemName) => {
    setItems(items.filter(i => i.name !== itemName));
    const newQuantities = { ...quantities };
    delete newQuantities[itemName];
    setQuantities(newQuantities);
  };

  const updateQuantity = (itemName, quantity) => {
    if (quantity <= 0) {
      removeItem(itemName);
    } else {
      setQuantities({ ...quantities, [itemName]: quantity });
    }
  };

  const getTotal = () => {
    return items.reduce((sum, item) => {
      const price = parseFloat(item.price.replace('$', ''));
      const qty = quantities[item.name] || 1;
      return sum + (price * qty);
    }, 0);
  };

  return {
    items,
    quantities,
    addItem,
    removeItem,
    updateQuantity,
    getTotal,
  };
};

// Hook for managing favorite items
export const useFavorites = () => {
  const [favorites, setFavorites] = useState([]);

  const toggleFavorite = (itemName) => {
    if (favorites.includes(itemName)) {
      setFavorites(favorites.filter(name => name !== itemName));
    } else {
      setFavorites([...favorites, itemName]);
    }
  };

  const isFavorite = (itemName) => {
    return favorites.includes(itemName);
  };

  return {
    favorites,
    toggleFavorite,
    isFavorite,
  };
};
