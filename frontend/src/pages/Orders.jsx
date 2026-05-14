import { useEffect, useState } from 'react';
import { fetchOrders } from '../api';
import { Link, useSearchParams } from 'react-router-dom';
import { format } from 'date-fns';

export default function Orders() {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchParams] = useSearchParams();
  const statusFilter = searchParams.get('status');

  useEffect(() => {
    const loadOrders = async () => {
      try {
        const res = await fetchOrders();
        let data = res.data;
        if (statusFilter) {
          data = data.filter(o => o.status === statusFilter);
        }
        setOrders(data);
      } catch (err) {
        console.error("Failed to load orders", err);
      } finally {
        setLoading(false);
      }
    };
    loadOrders();
  }, [statusFilter]);

  const getStatusColor = (status) => {
    switch (status) {
      case 'delivered': return 'bg-green-100 text-green-800';
      case 'delayed': return 'bg-red-100 text-red-800';
      case 'in_transit': return 'bg-yellow-100 text-yellow-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) return <div>Loading orders...</div>;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-800">Orders</h1>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-gray-50 text-gray-600 font-medium border-b border-gray-100">
              <tr>
                <th className="px-6 py-4">Order ID</th>
                <th className="px-6 py-4">Item ID</th>
                <th className="px-6 py-4">Supplier ID</th>
                <th className="px-6 py-4">Qty</th>
                <th className="px-6 py-4">Expected Date</th>
                <th className="px-6 py-4">Status</th>
                <th className="px-6 py-4">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {orders.slice(0, 100).map((order) => (
                <tr key={order.order_id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-6 py-4 text-gray-800 font-medium">{order.order_id.substring(0,8)}...</td>
                  <td className="px-6 py-4 text-gray-600">{order.item_id.substring(0,8)}...</td>
                  <td className="px-6 py-4 text-gray-600">{order.supplier_id.substring(0,8)}...</td>
                  <td className="px-6 py-4 font-medium">{order.quantity}</td>
                  <td className="px-6 py-4 text-gray-600">{format(new Date(order.expected_delivery_date), 'MMM dd, yyyy')}</td>
                  <td className="px-6 py-4">
                    <span className={`px-3 py-1 rounded-full text-xs font-semibold ${getStatusColor(order.status)} uppercase tracking-wider`}>
                      {order.status}
                    </span>
                    {order.is_emergency_order && (
                      <span className="ml-2 px-2 py-1 rounded-full bg-red-500 text-white text-xs font-bold uppercase">SOS</span>
                    )}
                  </td>
                  <td className="px-6 py-4">
                    <Link to={`/orders/${order.order_id}`} className="text-blue-600 hover:text-blue-800 font-medium">
                      View
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {orders.length > 100 && (
            <div className="p-4 text-center text-sm text-gray-500 bg-gray-50 border-t border-gray-100">
              Showing first 100 of {orders.length} orders.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
