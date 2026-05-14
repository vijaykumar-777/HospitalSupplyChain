import { useEffect, useState } from 'react';
import { fetchActiveDisaster, fetchDisasterEvents, triggerDisasterCheck, simulateDisaster } from '../api';
import { MapContainer, TileLayer, Marker, Popup, Circle } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import { AlertTriangle, RefreshCw, Radio, PlayCircle } from 'lucide-react';
import { format } from 'date-fns';
import L from 'leaflet';

// Fix leaflet icon issue in react
import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';
let DefaultIcon = L.icon({
    iconUrl: icon,
    shadowUrl: iconShadow,
    iconSize: [25, 41],
    iconAnchor: [12, 41]
});
L.Marker.prototype.options.icon = DefaultIcon;

export default function Disaster() {
  const [activeEvent, setActiveEvent] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [checking, setChecking] = useState(false);

  // Default hospital location (approximate center for demo)
  const hospitalPos = [21.1458, 79.0882]; // Updated to Nagpur

  const loadData = async () => {
    setLoading(true);
    try {
      const activeRes = await fetchActiveDisaster();
      if (activeRes.data.active) {
        setActiveEvent(activeRes.data.event);
      } else {
        setActiveEvent(null);
      }

      const histRes = await fetchDisasterEvents();
      setHistory(histRes.data);
    } catch (err) {
      console.error("Failed to load disaster info", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleManualTrigger = async () => {
    setChecking(true);
    try {
      await triggerDisasterCheck();
      await loadData();
    } catch (err) {
      console.error("Manual trigger failed", err);
    } finally {
      setChecking(false);
    }
  };

  const handleSimulate = async () => {
    setChecking(true);
    try {
      await simulateDisaster();
      await loadData();
    } catch (err) {
      console.error("Simulate failed", err);
    } finally {
      setChecking(false);
    }
  };

  if (loading) return <div>Loading disaster intelligence...</div>;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-800">Disaster Intelligence</h1>
        <div className="flex gap-3">
          <button 
            onClick={handleSimulate}
            disabled={checking}
            className="flex items-center gap-2 bg-red-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-red-700 transition disabled:opacity-50"
          >
            <PlayCircle size={18} />
            Simulate Disaster
          </button>
          <button 
            onClick={handleManualTrigger}
            disabled={checking}
            className="flex items-center gap-2 bg-gray-800 text-white px-4 py-2 rounded-lg font-medium hover:bg-gray-700 transition disabled:opacity-50"
          >
            <RefreshCw size={18} className={checking ? 'animate-spin' : ''} />
            {checking ? 'Scanning APIs...' : 'Force Live Scan'}
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Map View */}
        <div className="lg:col-span-2 bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden h-[500px] relative z-0">
          <MapContainer center={hospitalPos} zoom={5} scrollWheelZoom={false} className="h-full w-full">
            <TileLayer
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
              url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png"
            />
            {/* Hospital Marker */}
            <Marker position={hospitalPos}>
              <Popup>
                <strong>Central Hospital</strong><br />
                Main supply hub.
              </Popup>
            </Marker>

            {/* Active Disaster Highlight */}
            {activeEvent && (
              <Circle 
                center={hospitalPos} // Demo uses hospital pos as center if no coords
                radius={150000} // 150km 
                pathOptions={{ color: 'red', fillColor: 'red', fillOpacity: 0.2 }}
              >
                <Popup>
                  <strong>{activeEvent.disaster_type.toUpperCase()} Zone</strong><br/>
                  Severity: {activeEvent.severity}/5
                </Popup>
              </Circle>
            )}
          </MapContainer>
        </div>

        {/* Active Alert Sidebar */}
        <div className="space-y-6">
          <div className={`rounded-xl shadow-sm border p-6 ${activeEvent ? 'bg-red-50 border-red-200' : 'bg-green-50 border-green-200'}`}>
            <h2 className="text-lg font-bold flex items-center gap-2 mb-4">
              {activeEvent ? <AlertTriangle className="text-red-600" /> : <Radio className="text-green-600" />}
              {activeEvent ? 'Active Incident' : 'All Clear'}
            </h2>
            
            {activeEvent ? (
              <div className="space-y-4">
                <div className="bg-white bg-opacity-60 p-4 rounded-lg">
                  <span className="text-red-800 font-bold block mb-1 text-lg">{activeEvent.raw_text}</span>
                  <p className="text-sm text-gray-700">Source: <span className="font-semibold capitalize">{activeEvent.source}</span></p>
                  <p className="text-sm text-gray-700">Detected: {format(new Date(activeEvent.detected_at), 'MMM dd HH:mm')}</p>
                </div>
                
                <div className="bg-white bg-opacity-60 p-4 rounded-lg border-l-4 border-red-500">
                  <span className="text-gray-800 font-medium block mb-1 text-sm uppercase tracking-wider">AI Analysis</span>
                  <p className="text-gray-800 text-sm">{activeEvent.ai_summary || 'Analyzing...'}</p>
                  <div className="mt-3 flex justify-between">
                    <span className="text-xs font-bold text-red-600">Severity: {activeEvent.severity}/5</span>
                    <span className="text-xs font-bold text-red-600">Type: {activeEvent.disaster_type}</span>
                  </div>
                </div>
              </div>
            ) : (
              <p className="text-gray-600">No active disasters detected near supply routes.</p>
            )}
          </div>

          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 max-h-[220px] overflow-y-auto">
            <h2 className="text-md font-bold text-gray-800 mb-3 sticky top-0 bg-white pb-2 border-b">Recent Events</h2>
            <div className="space-y-3">
              {history.filter(h => !h.is_active).slice(0, 5).map(event => (
                <div key={event.event_id} className="text-sm border-b border-gray-50 pb-2">
                  <p className="font-medium text-gray-800 truncate" title={event.raw_text}>{event.raw_text}</p>
                  <div className="flex justify-between text-xs text-gray-500 mt-1">
                    <span className="capitalize">{event.source}</span>
                    <span>{format(new Date(event.detected_at), 'MMM dd')}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
