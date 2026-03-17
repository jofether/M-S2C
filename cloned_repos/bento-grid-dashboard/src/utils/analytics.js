// Analytics utility functions

export const calculateMetrics = (data) => {
  if (!data || data.length === 0) return { avg: 0, max: 0, min: 0 };
  const avg = data.reduce((a, b) => a + b, 0) / data.length;
  const max = Math.max(...data);
  const min = Math.min(...data);
  return { avg: Math.round(avg), max, min };
};

export const generateChartData = (days = 10) => {
  return Array.from({ length: days }, () => Math.floor(Math.random() * 100));
};

export const formatCurrency = (value) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
  }).format(value);
};

export const getPercentageChange = (current, previous) => {
  if (previous === 0) return 0;
  return (((current - previous) / previous) * 100).toFixed(1);
};

export const formatTime = (date) => {
  return new Intl.DateTimeFormat('en-US', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  }).format(date);
};

export const groupByCategory = (items, categoryKey) => {
  return items.reduce((acc, item) => {
    const key = item[categoryKey];
    if (!acc[key]) acc[key] = [];
    acc[key].push(item);
    return acc;
  }, {});
};
