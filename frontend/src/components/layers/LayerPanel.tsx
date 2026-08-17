import { Check, Lock } from 'lucide-react';
import { getLayersByCategory } from '../../data/layers';

interface LayerPanelProps {
  activeLayers: string[];
  toggleLayer: (id: string) => void;
}

export default function LayerPanel({ activeLayers, toggleLayer }: LayerPanelProps) {
  const categories = [
    { id: 'observations', label: 'Observations' },
    { id: 'environmental', label: 'Environmental' },
    { id: 'risk', label: 'Risk / Derived' }
  ];

  return (
    <div className="w-72 bg-zinc-950 border-r border-zinc-800 flex flex-col h-full overflow-y-auto">
      <div className="p-4 border-b border-zinc-800 sticky top-0 bg-zinc-950 z-10">
        <h2 className="text-sm font-semibold text-white">Data Layers</h2>
        <p className="text-xs text-zinc-400 mt-1">Configure map visualization</p>
      </div>
      
      <div className="p-4 space-y-6">
        {categories.map(category => (
          <section key={category.id}>
            <h3 className="text-[10px] font-bold text-zinc-500 uppercase tracking-wider mb-3">
              {category.label}
            </h3>
            <div className="space-y-1">
              {getLayersByCategory(category.id).map(layer => {
                const isAvailable = layer.availability === 'available';
                const isActive = activeLayers.includes(layer.id);
                
                return (
                  <button
                    key={layer.id}
                    disabled={!isAvailable}
                    onClick={() => isAvailable && toggleLayer(layer.id)}
                    className={`w-full flex flex-col items-start p-2 rounded-md transition-colors ${
                      !isAvailable 
                        ? 'opacity-60 cursor-not-allowed' 
                        : isActive 
                          ? 'bg-zinc-800/80 border border-zinc-700' 
                          : 'hover:bg-zinc-800/40 border border-transparent'
                    }`}
                  >
                    <div className="flex items-center gap-2 w-full">
                      <div className={`w-4 h-4 rounded border flex items-center justify-center shrink-0 ${
                        !isAvailable ? 'border-zinc-700 bg-zinc-900' :
                        isActive ? 'bg-zinc-300 border-zinc-300' : 'border-zinc-600'
                      }`}>
                        {isActive && <Check className="w-3 h-3 text-zinc-900" />}
                      </div>
                      <span className={`text-sm font-medium ${isActive ? 'text-white' : 'text-zinc-300'}`}>
                        {layer.label}
                      </span>
                      {!isAvailable && <Lock className="w-3 h-3 text-zinc-600 ml-auto" />}
                    </div>
                    
                    <div className="ml-6 mt-1 text-left">
                      {!isAvailable ? (
                        <span className="text-[10px] font-mono text-zinc-500 bg-zinc-900 px-1.5 py-0.5 rounded">
                          {layer.pendingReason}
                        </span>
                      ) : (
                        <span className="text-[10px] text-zinc-400">
                          {isActive ? layer.description : 'Available'}
                        </span>
                      )}
                    </div>
                  </button>
                );
              })}
            </div>
          </section>
        ))}
      </div>
    </div>
  );
}
