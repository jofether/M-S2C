// Mock data for the application
export const mockUsers = [
  { id: 1, name: 'Edrian Hernandez', email: 'edrian@university.edu', role: 'Admin', status: 'Active', avatar: null, joinDate: '2023-01-15' },
  { id: 2, name: 'Jett Mark Manalo', email: 'jett.mark@university.edu', role: 'Editor', status: 'Active', avatar: null, joinDate: '2023-03-22' },
  { id: 3, name: 'Jofether Mendoza', email: 'jofether@university.edu', role: 'Viewer', status: 'Inactive', avatar: null, joinDate: '2023-02-10' },
  { id: 4, name: 'Maurice Dela Cruz', email: 'maurice@university.edu', role: 'Admin', status: 'Active', avatar: null, joinDate: '2023-05-08' },
  { id: 5, name: 'Guest User', email: 'guest.123456789@temp-mail.com', role: 'Viewer', status: 'Pending', avatar: null, joinDate: '2024-01-20' },
  { id: 6, name: 'Alice Johnson', email: 'alice.johnson@university.edu', role: 'Editor', status: 'Active', avatar: null, joinDate: '2023-06-14' },
  { id: 7, name: 'Bob Smith', email: 'bob.smith@university.edu', role: 'Viewer', status: 'Active', avatar: null, joinDate: '2023-07-11' },
];

export const mockReports = [
  { id: 1, title: 'Q1 Revenue Analysis', author: 'Edrian Hernandez', date: '2024-01-20', status: 'Completed', views: 234 },
  { id: 2, title: 'User Engagement Metrics', author: 'Jett Mark Manalo', date: '2024-01-18', status: 'In Progress', views: 128 },
  { id: 3, title: 'Market Trends Report', author: 'Maurice Dela Cruz', date: '2024-01-15', status: 'Completed', views: 456 },
  { id: 4, title: 'Customer Satisfaction Survey', author: 'Alice Johnson', date: '2024-01-10', status: 'Completed', views: 312 },
];

export const mockAnalytics = [
  { month: 'Jan', revenue: 12400, users: 1200, sessions: 2890 },
  { month: 'Feb', revenue: 18600, users: 1500, sessions: 3210 },
  { month: 'Mar', revenue: 21200, users: 1800, sessions: 3890 },
  { month: 'Apr', revenue: 19400, users: 1650, sessions: 3456 },
  { month: 'May', revenue: 23800, users: 2000, sessions: 4120 },
  { month: 'Jun', revenue: 28600, users: 2300, sessions: 4890 },
];

export const mockNotifications = [
  { id: 1, type: 'success', message: 'Report generated successfully', timestamp: new Date(Date.now() - 5 * 60000) },
  { id: 2, type: 'warning', message: 'High CPU usage detected', timestamp: new Date(Date.now() - 15 * 60000) },
  { id: 3, type: 'info', message: 'New update available', timestamp: new Date(Date.now() - 2 * 3600000) },
  { id: 4, type: 'error', message: 'Failed to sync data', timestamp: new Date(Date.now() - 24 * 3600000) },
];
