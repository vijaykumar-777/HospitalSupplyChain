import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { fetchOrder, fetchOrderPrediction, fetchAlternateSuppliers, fetchSupplier } from '../api';
import { format } from 'date-fns';
import { AlertTriangle, Clock, Truck, ShieldCheck, ArrowLeft } from 'lucide-react';

export default function OrderDetail() {
  const { id } = useParams();
  const [order, setOrder] = useState(null);
  const [prediction, setPrediction] = useState(null);
  const [supplier, setSupplier] = useState(null);
  const [alternates, setAlternates] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadData = async () => {
      try {
        const orderRes = await fetchOrder(id);
        setOrder(orderRes.data);
        
        const supRes = await fetchSupplier(orderRes.data.supplier_id);
        setSupplier(supRes.data.supplier);

        const predRes = await fetchOrderPrediction(id);
        if (predRes.data.status !== 'pending') {
          setPrediction(predRes.data);
        }

        const altRes = await fetchAlternateSuppliers(orderRes.data.item_id);
        setAlternates(altRes.data.slice(0, 3)); // Top 3 alternates

      } catch (err) {
        console.error("Failed to load order details", err);
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, [id]);

  if (loading) return <div>Loading order details...</div>;
  if (!order) return <div>Order not found.</div>;

  return (
    <div className="space-y-6 max-w-6xl">
      <Link to="/orders" className="flex items-center gap-2 text-gray-500 hover:text-blue-600 transition-colors">
        <ArrowLeft size={20} /> Back to Orders
      </Link>
      
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-2xl font-bold text-gray-800">Order #{order.order_id.substring(0,8)}</h1>
          <p className="text-gray-500 mt-1">Placed on {format(new Date(order.order_date), 'PPP')}</p>
        </div>
        <span className={`px-4 py-2 rounded-full text-sm font-bold uppercase tracking-wider ${
          order.status === 'delayed' ? 'bg-red-100 text-red-800' :
          order.status === 'delivered' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
        }`}>
          {order.status}
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Main Details */}
        <div className="md:col-span-2 space-y-6">
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            <h2 className="text-lg font-bold text-gray-800 mb-4 border-b pb-2">Order Information</h2>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-500">Item ID</p>
                <p className="font-medium text-gray-800">{order.item_id}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Quantity</p>
                <p className="font-medium text-gray-800">{order.quantity}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Expected Delivery</p>
                <p className="font-medium text-gray-800">{format(new Date(order.expected_delivery_date), 'PPP')}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Emergency Status</p>
                <p className="font-medium text-gray-800">{order.is_emergency_order ? '🚨 SOS Emergency' : 'Standard'}</p>
              </div>
            </div>
          </div>

          {/* AI Prediction Card */}
          {prediction ? (
            <div className={`rounded-xl shadow-sm border p-6 ${
              prediction.is_delayed ? 'bg-red-50 border-red-200' : 'bg-green-50 border-green-200'
            }`}>
              <div className="flex items-center gap-3 mb-4">
                {prediction.is_delayed ? <AlertTriangle className="text-red-600" /> : <ShieldCheck className="text-green-600" />}
                <h2 className="text-lg font-bold text-gray-800">AI Delay Prediction</h2>
              </div>
              
              <div className="flex flex-col gap-3">
                <div className="flex justify-between items-center bg-white bg-opacity-60 p-4 rounded-lg">
                  <span className="text-gray-700 font-medium">Status</span>
                  <span className={`font-bold ${prediction.is_delayed ? 'text-red-700' : 'text-green-700'}`}>
                    {prediction.is_delayed ? 'Delay Expected' : 'On Time'}
                  </span>
                </div>
                
                {prediction.is_delayed && (
                  <>
                    <div className="flex justify-between items-center bg-white bg-opacity-60 p-4 rounded-lg">
                      <span className="text-gray-700 font-medium">Extra Days Expected</span>
                      <span className="font-bold text-red-700">+{prediction.extra_days} days</span>
                    </div>
                    <div className="flex justify-between items-center bg-white bg-opacity-60 p-4 rounded-lg">
                      <span className="text-gray-700 font-medium">New ETA</span>
                      <span className="font-bold text-red-700">{format(new Date(prediction.new_eta), 'PPP')}</span>
                    </div>
                  </>
                )}
                
                <div className="bg-white bg-opacity-60 p-4 rounded-lg">
                  <span className="text-gray-700 font-medium block mb-1">AI Reasoning</span>
                  <p className="text-gray-800">{prediction.reason}</p>
                </div>
                
                <div className="text-right text-xs text-gray-500 mt-2">
                  Confidence Score: {Math.round(prediction.confidence * 100)}%
                </div>
              </div>
            </div>
          ) : (
            <div className="bg-gray-50 rounded-xl shadow-sm border border-gray-200 p-6 flex flex-col items-center justify-center text-gray-500 h-48">
              <Clock size={32} className="mb-2 opacity-50" />
              <p>AI prediction is pending...</p>
            </div>
          )}
        </div>

        {/* Sidebar Panel */}
        <div className="space-y-6">
          {/* Current Supplier */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            <h2 className="text-lg font-bold text-gray-800 mb-4 border-b pb-2 flex items-center gap-2">
              <Truck size={18} /> Current Supplier
            </h2>
            {supplier && (
              <div className="space-y-3">
                <p className="font-medium text-gray-800">{supplier.name}</p>
                <p className="text-sm text-gray-500">{supplier.city}, {supplier.state}</p>
                <div className="flex items-center gap-2 mt-2">
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div className={`h-2 rounded-full ${supplier.reliability_score > 0.8 ? 'bg-green-500' : 'bg-yellow-500'}`} style={{width: `${supplier.reliability_score * 100}%`}}></div>
                  </div>
                  <span className="text-xs font-bold">{Math.round(supplier.reliability_score * 100)}%</span>
                </div>
                <p className="text-xs text-gray-500 text-center mt-1">Reliability Score</p>
              </div>
            )}
          </div>

          {/* Alternate Suppliers */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            <h2 className="text-lg font-bold text-gray-800 mb-4 border-b pb-2">Top Alternates</h2>
            <div className="space-y-4">
              {alternates.map((alt, idx) => (
                <div key={alt.supplier_id} className="p-3 bg-gray-50 rounded-lg border border-gray-100">
                  <div className="flex justify-between items-start">
                    <p className="font-medium text-sm text-gray-800">{alt.name}</p>
                    <span className="text-xs font-bold bg-blue-100 text-blue-800 px-2 py-1 rounded">Rank {idx+1}</span>
                  </div>
                  <p className="text-xs text-gray-500 mt-1">{alt.city} • Lead: {alt.avg_lead_days} days</p>
                  {alt.is_emergency_certified && (
                    <p className="text-xs text-red-600 font-medium mt-1">✓ Emergency Certified</p>
                  )}
                </div>
              ))}
            </div>
            <button className="w-full mt-4 bg-gray-100 hover:bg-gray-200 text-gray-700 text-sm font-medium py-2 rounded transition-colors">
              Request Reroute
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
