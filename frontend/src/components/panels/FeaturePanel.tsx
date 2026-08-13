import { X, Info, MapPin, Calendar, Activity } from 'lucide-react';
import type { SpatialFeature } from '../../data/types';

interface FeaturePanelProps {
  feature: SpatialFeature;
  onClose: () => void;
}

export default function FeaturePanel({ feature, onClose }: FeaturePanelProps) {
  const p = feature.properties;
  const isHotspot = p.hotspot_id != null;

  return (
    <div className="w-80 sm:w-96 bg-zinc-900 border border-zinc-700 shadow-xl rounded-lg overflow-hidden flex flex-col max-h-[calc(100vh-2rem)]">
      {/* Header */}
      <div className="p-4 border-b border-zinc-800 bg-zinc-950 flex items-start justify-between">
        <div>
          <h2 className="text-lg font-medium text-white flex items-center gap-2">
            <MapPin className="w-4 h-4 text-zinc-400" />
            Spatial Feature
          </h2>
          <p className="text-xs text-zinc-400 mt-1 uppercase tracking-wider">{p.feature_id}</p>
        </div>
        <button onClick={onClose} className="p-1 hover:bg-zinc-800 rounded-md text-zinc-400 transition-colors">
          <X className="w-5 h-5" />
        </button>
      </div>

      {/* Content */}
      <div className="p-4 overflow-y-auto space-y-6">
        
        {/* P1 Data: Core Observation */}
        <section>
          <h3 className="text-xs font-semibold text-zinc-500 uppercase tracking-wider mb-3">LST Observation</h3>
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-zinc-950 p-3 rounded-md border border-zinc-800">
              <span className="block text-xs text-zinc-400 mb-1">LST (°C)</span>
              <span className="text-xl font-semibold text-white">{p.lst_c.toFixed(1)}°</span>
            </div>
            <div className="bg-zinc-950 p-3 rounded-md border border-zinc-800 flex flex-col justify-center">
              <span className="block text-xs text-zinc-400 mb-1">Anomaly Baseline</span>
              {p.lst_anomaly_c != null ? (
                <span className={`text-xl font-semibold ${p.lst_anomaly_c > 0 ? 'text-red-400' : 'text-blue-400'}`}>
                  {p.lst_anomaly_c > 0 ? '+' : ''}{p.lst_anomaly_c.toFixed(1)}°
                </span>
              ) : (
                <span className="text-sm text-zinc-500 italic">Pending / Not available</span>
              )}
            </div>
          </div>
        </section>

        {/* P1 Data: Metadata */}
        <section>
          <h3 className="text-xs font-semibold text-zinc-500 uppercase tracking-wider mb-3">Acquisition Details</h3>
          <ul className="space-y-2 text-sm text-zinc-300">
            <li className="flex items-start gap-2">
              <Activity className="w-4 h-4 text-zinc-500 mt-0.5 shrink-0" />
              <span><span className="text-zinc-500">Source:</span> {p.source} ({p.satellite})</span>
            </li>
            <li className="flex items-start gap-2">
              <Calendar className="w-4 h-4 text-zinc-500 mt-0.5 shrink-0" />
              <span><span className="text-zinc-500">Acquisition period:</span> {new Date(p.date_period_start).toLocaleDateString()} &mdash; {new Date(p.date_period_end).toLocaleDateString()}</span>
            </li>
            <li className="flex items-start gap-2">
              <Info className="w-4 h-4 text-zinc-500 mt-0.5 shrink-0" />
              <span><span className="text-zinc-500">Data quality:</span> {p.data_quality} ({p.valid_pixel_percent}% valid)</span>
            </li>
          </ul>
        </section>

        {/* P2 Data: Risk & Hotspot (Null graceful fallback) */}
        <section className="pt-4 border-t border-zinc-800">
          <h3 className="text-xs font-semibold text-zinc-500 uppercase tracking-wider mb-3 flex items-center gap-2">
            P2 Risk Analysis
            {!isHotspot && <span className="px-2 py-0.5 rounded-full bg-zinc-800 text-[10px]">Pending</span>}
          </h3>
          
          {isHotspot ? (
            <div className="space-y-3">
              <div className="flex justify-between items-center text-sm">
                <span className="text-zinc-400">Hotspot ID</span>
                <span className="font-mono text-zinc-300">{p.hotspot_id}</span>
              </div>
              <div className="flex justify-between items-center text-sm">
                <span className="text-zinc-400">Hotspot Score</span>
                <span className="text-zinc-300 font-medium">{p.hotspot_score}</span>
              </div>
              <div className="flex justify-between items-center text-sm">
                <span className="text-zinc-400">Confidence</span>
                <span className="text-zinc-300 font-medium">{p.confidence}%</span>
              </div>
            </div>
          ) : (
            <div className="bg-zinc-950 border border-zinc-800 border-dashed rounded-md p-4 text-center">
              <p className="text-sm text-zinc-500">Risk model data not yet available for this feature.</p>
            </div>
          )}
        </section>
      </div>
    </div>
  );
}
