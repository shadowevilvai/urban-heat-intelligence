import { useEffect, useRef, useState, useCallback } from 'react';
import Map, { Source, Layer, NavigationControl } from 'react-map-gl/maplibre';
import type { MapLayerMouseEvent, MapRef } from 'react-map-gl/maplibre';
import { useCityMap } from '../../api/queries';
import MapLegend from './MapLegend';

interface MapEngineProps {
  activeCityId: string;
  activeLayers: string[];
  onSelectFeatureId: (featureId: string | null) => void;
}

export default function MapEngine({ activeCityId, activeLayers, onSelectFeatureId }: MapEngineProps) {
  const mapRef = useRef<MapRef>(null);
  const { data: geojsonData, isLoading, isError } = useCityMap(activeCityId);
  const [lstBounds, setLstBounds] = useState<{min: number, max: number} | null>(null);
  const [currentZoom, setCurrentZoom] = useState(11);
  const [hotspotCount, setHotspotCount] = useState(0);

  // Calculate LST bounds and center map when new city data loads
  useEffect(() => {
    if (geojsonData?.features.length) {
      let minLng = Infinity, minLat = Infinity, maxLng = -Infinity, maxLat = -Infinity;
      let minLst = Infinity, maxLst = -Infinity;
      let hsCount = 0;

      geojsonData.features.forEach(f => {
        const lst = f.properties.lst_c;
        if (lst < minLst) minLst = lst;
        if (lst > maxLst) maxLst = lst;

        if (f.properties.hotspot_id) {
          hsCount++;
        }

        if (f.geometry.type === 'Point') {
          const [lng, lat] = f.geometry.coordinates;
          if (lng < minLng) minLng = lng;
          if (lat < minLat) minLat = lat;
          if (lng > maxLng) maxLng = lng;
          if (lat > maxLat) maxLat = lat;
        }
      });

      setLstBounds({ min: minLst, max: maxLst });
      setHotspotCount(hsCount);

      if (mapRef.current && minLng !== Infinity) {
        mapRef.current.fitBounds([
          [minLng, minLat],
          [maxLng, maxLat]
        ], { padding: 40, duration: 1000 });
      }
    } else {
      setLstBounds(null);
      setHotspotCount(0);
    }
  }, [geojsonData]);

  const onMove = useCallback((evt: any) => {
    setCurrentZoom(evt.viewState.zoom);
  }, []);

  const onClick = (event: MapLayerMouseEvent) => {
    const feature = event.features?.[0];
    if (feature && feature.properties && feature.properties.feature_id) {
      onSelectFeatureId(feature.properties.feature_id);
    } else {
      onSelectFeatureId(null);
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

  const isLstActive = activeLayers.includes('lst');
  const isHotspotsActive = activeLayers.includes('hotspots');

  const interactiveLayers = ['feature-interaction'];
  if (isHotspotsActive) {
    interactiveLayers.push('p2-hotspots');
  }

  return (
    <div className="absolute inset-0 bg-zinc-800">
      {isLoading && (
        <div className="absolute top-4 left-1/2 -translate-x-1/2 z-10 bg-zinc-900/80 px-4 py-2 rounded-full border border-zinc-700 shadow-lg text-sm text-zinc-300">
          Loading map data...
        </div>
      )}

      {isError && (
        <div className="absolute top-4 left-1/2 -translate-x-1/2 z-10 bg-red-900/80 px-4 py-2 rounded border border-red-700 shadow-lg text-sm text-red-100">
          Failed to load map data.
        </div>
      )}

      <Map
        ref={mapRef}
        initialViewState={{
          longitude: 72.8777,
          latitude: 19.0760,
          zoom: 11
        }}
        mapStyle="https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json"
        interactiveLayerIds={interactiveLayers}
        onClick={onClick}
        onMove={onMove}
        onMouseEnter={onMouseEnter}
        onMouseLeave={onMouseLeave}
      >
        {geojsonData && (
          <Source id="lst-data" type="geojson" data={geojsonData}>
            <Layer
              id="lst-continuous-points"
              type="heatmap"
              layout={{
                visibility: isLstActive ? 'visible' : 'none'
              }}
              paint={{
                'heatmap-weight': lstBounds ? [
                  'interpolate',
                  ['linear'],
                  ['get', 'lst_c'],
                  lstBounds.min, 0,
                  lstBounds.max, 1
                ] : 0,
                'heatmap-intensity': [
                  'interpolate',
                  ['linear'],
                  ['zoom'],
                  8, 0.5,
                  14, 1.2
                ],
                'heatmap-color': [
                  'interpolate',
                  ['linear'],
                  ['heatmap-density'],
                  0, 'rgba(0, 0, 255, 0)',
                  0.1, '#1d4ed8', // deep blue
                  0.3, '#7e22ce', // muted purple
                  0.6, '#f97316', // orange
                  0.8, '#dc2626', // red
                  1, '#7f1d1d'    // dark red
                ],
                'heatmap-radius': [
                  'interpolate',
                  ['linear'],
                  ['zoom'],
                  8, 10,
                  9, 14,
                  10, 20,
                  11, 28,
                  12, 36,
                  13, 46,
                  14, 60
                ],
                'heatmap-opacity': [
                  'interpolate',
                  ['linear'],
                  ['zoom'],
                  10, 0.65,
                  11.5, 0.60,
                  13, 0.30,
                  14, 0
                ]
              }}
            />
            <Layer
              id="feature-interaction"
              type="circle"
              paint={{
                'circle-opacity': 0,
                'circle-stroke-opacity': 0,
                'circle-color': 'transparent',
                'circle-radius': 10
              }}
            />
            <Layer
              id="p2-hotspots"
              type="circle"
              filter={['has', 'hotspot_id']}
              layout={{
                visibility: isHotspotsActive ? 'visible' : 'none'
              }}
              paint={{
                'circle-radius': [
                  'interpolate',
                  ['linear'],
                  ['zoom'],
                  10, 5,
                  15, 14
                ],
                'circle-color': [
                  'match',
                  ['get', 'risk_category'],
                  'high', '#f97316', // Orange
                  'extreme', '#dc2626', // Red
                  '#ffffff'
                ],
                'circle-stroke-width': 2,
                'circle-stroke-color': '#ffffff'
              }}
            />
          </Source>
        )}

        <NavigationControl position="bottom-right" showCompass={false} />

        <MapLegend
          activeLayers={activeLayers}
          lstBounds={lstBounds}
          hotspotCount={hotspotCount}
          currentZoom={currentZoom}
        />
      </Map>
    </div>
  );
}
