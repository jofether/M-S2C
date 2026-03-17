import { useState, useCallback } from 'react';

/**
 * Custom hook for managing toggle state
 * @param {boolean} initialState - Initial state value
 * @returns {Array} [value, toggle, setValue]
 */
export function useToggle(initialState = false) {
  const [value, setValue] = useState(initialState);

  const toggle = useCallback(() => {
    setValue(prev => !prev);
  }, []);

  return [value, toggle, setValue];
}

/**
 * Custom hook for managing local storage
 * @param {string} key - Storage key
 * @param {any} defaultValue - Default value
 * @returns {Array} [value, setValue]
 */
export function useLocalStorage(key, defaultValue) {
  const [storedValue, setStoredValue] = useState(() => {
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : defaultValue;
    } catch (error) {
      console.error('Error reading from localStorage:', error);
      return defaultValue;
    }
  });

  const setValue = useCallback((value) => {
    try {
      const valueToStore = value instanceof Function ? value(storedValue) : value;
      setStoredValue(valueToStore);
      window.localStorage.setItem(key, JSON.stringify(valueToStore));
    } catch (error) {
      console.error('Error writing to localStorage:', error);
    }
  }, [key, storedValue]);

  return [storedValue, setValue];
}

/**
 * Custom hook for filtering items
 * @param {Array} items - Items to filter
 * @param {string} searchTerm - Search term
 * @returns {Array} Filtered items
 */
export function useFilter(items, searchTerm) {
  return items.filter(item =>
    item.name.toLowerCase().includes(searchTerm.toLowerCase())
  );
}
