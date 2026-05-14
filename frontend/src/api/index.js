import axios from 'axios';

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: apiBaseUrl,
});

// Orders
export const fetchOrders = () => api.get('/orders');
export const fetchOrder = (id) => api.get(`/orders/${id}`);
export const fetchOrderPrediction = (id) => api.get(`/orders/${id}/prediction`);
export const updateOrderStatus = (id, status) => api.patch(`/orders/${id}/status`, { status });

// Suppliers
export const fetchSuppliers = () => api.get('/suppliers');
export const fetchSupplier = (id) => api.get(`/suppliers/${id}`);
export const fetchAlternateSuppliers = (itemId) => api.get(`/suppliers/alternates?item_id=${itemId}`);

// Inventory
export const fetchInventory = () => api.get('/inventory');
export const fetchItemStock = (id) => api.get(`/inventory/${id}`);

// Disaster
export const fetchDisasterEvents = () => api.get('/disaster/events');
export const fetchActiveDisaster = () => api.get('/disaster/active');
export const fetchDisasterContext = () => api.get('/disaster/context');
export const fetchAffectedRoutes = () => api.get('/disaster/routes');
export const triggerDisasterCheck = () => api.post('/disaster/trigger-check');
export const simulateDisaster = () => api.post('/disaster/simulate');

// Predictions
export const recheckPredictions = () => api.post('/predictions/recheck-all');
