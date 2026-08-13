import { useMemo } from 'react';
import Map, { Source, Layer, NavigationControl } from 'react-map-gl/maplibre';
import type { MapLayerMouseEvent } from 'react-map-gl/maplibre';
import type { SpatialFeature, SpatialFeatureCollection } from '../../data/types';
import mockFeatures from '../../data/mock/features.json';

interface MapEngineProps {
  onSelectFeature: (feature: SpatialFeature | null) => void;
}

export default function MapEngine({ onSelectFeature }: MapEngineProps) {
  // Use mock data for now
  const geojsonData = useMemo<SpatialFeatureCollection>(() => mockFeatures as SpatialFeatureCollection, []);

  const onClick = (event: MapLayerMouseEvent) => {
    const feature = event.features?.[0];
    if (feature) {
      // MapLibre's feature object needs to be cast to our SpatialFeature type
      onSelectFeature(feature as unknown as SpatialFeature);
    } else {
      onSelectFeature(null);
    }
  };

  const onMouseEnter = (event: MapLayerMouseEvent) => {
    if (event.target) {
      event.target.getCanvas().style.cursor = 'pointer';
    }
  };

  const onMouseLeave = (event: MapLayerMouseEvent) => {
    if (event.target) {
      event.target.getCanvas().style.cursor = '';
    }
  };

  return (
    <div className="absolute inset-0 bg-zinc-800">
      <Map
        style={{ width: '100%', height: '100%' }}
        initialViewState={{
          longitude: 72.8777,
          latitude: 19.0760,
          zoom: 11
        }}
        mapStyle="https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json"
        interactiveLayerIds={['lst-heatmap-points']}
        onClick={onClick}
        onMouseEnter={onMouseEnter}
        onMouseLeave={onMouseLeave}
      >
        <Source id="lst-data" type="geojson" data={geojsonData}>
          <Layer
            id="lst-heatmap-points"
            type="circle"
            paint={{
              'circle-radius': [
                'interpolate',
                ['linear'],
                ['zoom'],
                10, 15,
                15, 30
              ],
              'circle-color': [
                'interpolate',
                ['linear'],
                ['get', 'lst_c'],
                35, '#fde047', // Yellow
                40, '#f97316', // Orange
                45, '#dc2626'  // Red
              ],
              'circle-opacity': 0.8,
              'circle-stroke-width': 1,
              'circle-stroke-color': '#18181b'
            }}
          />
        </Source>
        
        <NavigationControl position="bottom-right" showCompass={false} />
        
        {/* Simple Legend overlay */}
        <div className="absolute bottom-6 left-6 bg-zinc-900/90 backdrop-blur border border-zinc-800 rounded-md p-3 z-10">
          <h4 className="text-xs font-semibold text-zinc-300 mb-2 uppercase tracking-wider">LST Observation (°C)</h4>
          <div className="flex items-center gap-2 text-xs text-zinc-400">
            <span>35°</span>
            <div className="w-32 h-2 rounded-full bg-gradient-to-r from-yellow-300 via-orange-500 to-red-600"></div>
            <span>45°+</span>
          </div>
        </div>
      </Map>
    </div>
  );
}
