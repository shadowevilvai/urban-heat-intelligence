import { LAYERS } from '../../data/layers';

interface MapLegendProps {
  activeLayerId: string | null;
}

export default function MapLegend({ activeLayerId }: MapLegendProps) {
  if (!activeLayerId) return null;
  
  const activeLayer = LAYERS.find(l => l.id === activeLayerId);
  
  if (!activeLayer) return null;

  return (
    <div className="absolute bottom-6 left-6 bg-zinc-900/90 backdrop-blur border border-zinc-800 rounded-md p-3 z-10 min-w-[200px]">
      <h4 className="text-xs font-semibold text-zinc-300 mb-2 uppercase tracking-wider">
        {activeLayer.label}
      </h4>
      
      {activeLayer.availability === 'available' ? (
        activeLayerId === 'lst' ? (
          <div className="flex items-center gap-2 text-xs text-zinc-400">
            <span>35°</span>
            <div className="w-32 h-2 rounded-full bg-gradient-to-r from-yellow-300 via-orange-500 to-red-600"></div>
            <span>45°+</span>
            <span className="ml-1 text-[10px] text-zinc-500">(°C)</span>
          </div>
        ) : (
          <div className="text-xs text-zinc-500 italic">No legend available</div>
        )
      ) : (
        <div className="flex flex-col gap-1 text-xs">
          <span className="text-zinc-500">Data unavailable</span>
          <span className="text-[10px] text-zinc-600">{activeLayer.pendingReason}</span>
        </div>
      )}
    </div>
  );
}
