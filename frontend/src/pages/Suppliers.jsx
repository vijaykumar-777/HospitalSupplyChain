import { useEffect, useState } from 'react';
import { fetchSuppliers } from '../api';
import { ShieldCheck, ShieldAlert } from 'lucide-react';

export default function Suppliers() {
  const [suppliers, setSuppliers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadData = async () => {
      try {
        const res = await fetchSuppliers();
        setSuppliers(res.data);
      } catch (err) {
        console.error("Failed to load suppliers", err);
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, []);

  if (loading) return <div>Loading suppliers...</div>;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-800">Supplier Directory</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {suppliers.map(sup => (
          <div key={sup.supplier_id} className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 flex flex-col hover:shadow-md transition-shadow">
            <div className="flex justify-between items-start mb-4">
              <div>
                <h3 className="font-bold text-lg text-gray-800">{sup.name}</h3>
                <p className="text-sm text-gray-500">{sup.city}, {sup.state}</p>
              </div>
              {sup.is_emergency_certified && (
                <span className="bg-red-100 text-red-700 px-2 py-1 rounded text-xs font-bold whitespace-nowrap">Emergency</span>
              )}
            </div>
            
            <div className="space-y-4 mt-auto">
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-500">Reliability Score</span>
                  <span className="font-bold">{Math.round(sup.reliability_score * 100)}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className={`h-2 rounded-full ${sup.reliability_score >= 0.8 ? 'bg-green-500' : sup.reliability_score >= 0.6 ? 'bg-yellow-500' : 'bg-red-500'}`} 
                    style={{width: `${sup.reliability_score * 100}%`}}
                  ></div>
                </div>
              </div>
              
              <div className="flex justify-between items-center text-sm border-t pt-4">
                <span className="text-gray-500">Avg Lead Time</span>
                <span className="font-medium text-gray-800">{sup.avg_lead_days} days</span>
              </div>
              
              <div className="flex justify-between items-center text-sm border-t pt-4">
                <span className="text-gray-500">Categories</span>
                <div className="flex flex-wrap gap-1 justify-end max-w-[60%]">
                  {sup.supply_categories.map(cat => (
                    <span key={cat} className="bg-gray-100 text-gray-600 px-2 py-0.5 rounded text-xs">
                      {cat}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
