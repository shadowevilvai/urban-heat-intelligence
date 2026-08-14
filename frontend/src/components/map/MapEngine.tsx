import { useMemo } from 'react';
import Map, { Source, Layer, NavigationControl } from 'react-map-gl/maplibre';
import type { MapLayerMouseEvent } from 'react-map-gl/maplibre';
import type { SpatialFeature, SpatialFeatureCollection } from '../../data/types';
import mockFeatures from '../../data/mock/features.json';
import MapLegend from './MapLegend';

interface MapEngineProps {
  activeLayerId: string | null;
  onSelectFeature: (feature: SpatialFeature | null) => void;
}

export default function MapEngine({ activeLayerId, onSelectFeature }: MapEngineProps) {
  // Use mock data for now
  const geojsonData = useMemo<SpatialFeatureCollection>(() => mockFeatures as SpatialFeatureCollection, []);

  const onClick = (event: MapLayerMouseEvent) => {
    // Only allow clicking features if the active layer is lst since our mock data is just lst
    if (activeLayerId !== 'lst') {
      onSelectFeature(null);
      return;
    }

    const feature = event.features?.[0];
    if (feature) {
      onSelectFeature(feature as unknown as SpatialFeature);
    } else {
      onSelectFeature(null);
    }
  };

  const onMouseEnter = (event: MapLayerMouseEvent) => {
    if (event.target && activeLayerId === 'lst') {
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
        interactiveLayerIds={activeLayerId === 'lst' ? ['lst-heatmap-points'] : []}
        onClick={onClick}
        onMouseEnter={onMouseEnter}
        onMouseLeave={onMouseLeave}
      >
        <Source id="lst-data" type="geojson" data={geojsonData}>
          <Layer
            id="lst-heatmap-points"
            type="circle"
            layout={{
              visibility: activeLayerId === 'lst' ? 'visible' : 'none'
            }}
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
        
        <MapLegend activeLayerId={activeLayerId} />
      </Map>
    </div>
  );
}
