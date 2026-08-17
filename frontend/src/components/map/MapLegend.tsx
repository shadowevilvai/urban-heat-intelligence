

interface MapLegendProps {
  activeLayers: string[];
  lstBounds: { min: number, max: number } | null;
  hotspotCount: number;
  currentZoom: number;
}

export default function MapLegend({ activeLayers, lstBounds, hotspotCount, currentZoom }: MapLegendProps) {
  if (activeLayers.length === 0) return null;

  const isLstActive = activeLayers.includes('lst');
  const isHotspotsActive = activeLayers.includes('hotspots');

  return (
    <div className="absolute bottom-6 left-6 flex flex-col gap-2 z-10">
      {isLstActive && lstBounds && (
        <div className="bg-zinc-900/90 backdrop-blur border border-zinc-800 rounded-md p-3 min-w-[200px]">
          <h4 className="text-xs font-semibold text-zinc-300 mb-2 uppercase tracking-wider">
            LST Observation
          </h4>
          <div className="flex items-center justify-between text-xs text-zinc-400 font-medium mt-3">
            <span>{lstBounds.min.toFixed(1)}°</span>
            <div className="flex-1 mx-3 h-2 rounded-full" style={{ background: 'linear-gradient(to right, #1d4ed8, #7e22ce, #f97316, #dc2626, #7f1d1d)' }}></div>
            <span>{lstBounds.max.toFixed(1)}°</span>
            <span className="ml-1 text-[10px] text-zinc-500">(°C)</span>
          </div>
        </div>
      )}

      {isHotspotsActive && (
        <div className="bg-zinc-900/90 backdrop-blur border border-zinc-800 rounded-md p-3 min-w-[200px]">
          <h4 className="text-xs font-semibold text-zinc-300 mb-2 uppercase tracking-wider flex justify-between">
            <span>P2 Hotspots</span>
            {hotspotCount > 0 && <span className="text-orange-400">{hotspotCount} detected</span>}
          </h4>

          {hotspotCount === 0 ? (
            <div className="text-xs text-zinc-500 italic mt-2">
              No canonical hotspots detected
            </div>
          ) : (
            <div className="flex flex-col gap-2 text-xs text-zinc-400 mt-2">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full border border-white" style={{ backgroundColor: '#dc2626' }}></div>
                <span>Extreme</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full border border-white" style={{ backgroundColor: '#f97316' }}></div>
                <span>High</span>
              </div>
            </div>
          )}
        </div>
      )}

      {currentZoom > 12 && (
        <div className="bg-zinc-900/90 backdrop-blur border border-zinc-800 rounded-md p-2 mt-2 self-start shadow-sm">
          <span className="text-[10px] text-zinc-400 uppercase tracking-wider">
            LST observations: 450m spatial resolution
          </span>
        </div>
      )}
    </div>
  );
}
