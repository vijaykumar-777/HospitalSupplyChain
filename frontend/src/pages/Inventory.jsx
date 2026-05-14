import { useEffect, useState } from 'react';
import { fetchInventory } from '../api';
import { AlertCircle, CheckCircle } from 'lucide-react';

export default function Inventory() {
  const [inventory, setInventory] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadData = async () => {
      try {
        const res = await fetchInventory();
        setInventory(res.data);
      } catch (err) {
        console.error("Failed to load inventory", err);
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, []);

  if (loading) return <div>Loading inventory...</div>;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-800">Inventory Status</h1>

      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-gray-50 text-gray-600 font-medium border-b border-gray-100">
              <tr>
                <th className="px-6 py-4">Item ID</th>
                <th className="px-6 py-4">Stock Level</th>
                <th className="px-6 py-4">Reorder Level</th>
                <th className="px-6 py-4">Days Remaining</th>
                <th className="px-6 py-4">Status</th>
                <th className="px-6 py-4">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {inventory.slice(0, 100).map((inv) => {
                const isCritical = inv.current_stock <= inv.reorder_level;
                const daysRemaining = Math.round(inv.current_stock / inv.daily_consumption_rate);
                
                return (
                  <tr key={inv.item_id} className={`hover:bg-gray-50 transition-colors ${isCritical ? 'bg-red-50' : ''}`}>
                    <td className="px-6 py-4 text-gray-800 font-medium">{inv.item_id.substring(0,8)}...</td>
                    <td className="px-6 py-4 font-bold">{inv.current_stock}</td>
                    <td className="px-6 py-4 text-gray-600">{inv.reorder_level}</td>
                    <td className={`px-6 py-4 font-medium ${daysRemaining < 7 ? 'text-red-600' : 'text-gray-800'}`}>
                      {daysRemaining} days
                    </td>
                    <td className="px-6 py-4">
                      {isCritical ? (
                        <span className="flex items-center gap-1 text-red-600 font-medium">
                          <AlertCircle size={16} /> Needs Reorder
                        </span>
                      ) : (
                        <span className="flex items-center gap-1 text-green-600 font-medium">
                          <CheckCircle size={16} /> Healthy
                        </span>
                      )}
                    </td>
                    <td className="px-6 py-4">
                      <button className="text-blue-600 hover:text-blue-800 font-medium">Order</button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
