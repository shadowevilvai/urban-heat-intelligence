import type { LayerDefinition } from './layerTypes';

export const LAYERS: LayerDefinition[] = [
  {
    id: 'lst',
    label: 'Land Surface Temperature',
    category: 'observations',
    description: 'Land Surface Temperature (LST) composite.',
    availability: 'available',
    owner: 'p1'
  },
  {
    id: 'lst_anomaly',
    label: 'LST Anomaly',
    category: 'observations',
    description: 'Deviation from baseline temperature.',
    availability: 'pending',
    owner: 'p1',
    pendingReason: 'Pending baseline'
  },
  {
    id: 'ndvi',
    label: 'NDVI',
    category: 'environmental',
    description: 'Normalized Difference Vegetation Index.',
    availability: 'pending',
    owner: 'p1',
    pendingReason: 'Pending / source integration'
  },
  {
    id: 'ndbi',
    label: 'NDBI',
    category: 'environmental',
    description: 'Normalized Difference Built-up Index.',
    availability: 'pending',
    owner: 'p1',
    pendingReason: 'Pending / source integration'
  },
  {
    id: 'ndwi',
    label: 'NDWI',
    category: 'environmental',
    description: 'Normalized Difference Water Index.',
    availability: 'pending',
    owner: 'p1',
    pendingReason: 'Pending / source integration'
  },
  {
    id: 'land_cover',
    label: 'Land Cover',
    category: 'environmental',
    description: 'Land cover classification.',
    availability: 'pending',
    owner: 'p1',
    pendingReason: 'Pending / source integration'
  },
  {
    id: 'hotspots',
    label: 'Hotspots',
    category: 'risk',
    description: 'Identified urban heat hotspots.',
    availability: 'available',
    owner: 'p2'
  },
  {
    id: 'risk',
    label: 'Risk Score',
    category: 'risk',
    description: 'Heat-health risk predictions.',
    availability: 'pending',
    owner: 'p2',
    pendingReason: 'Pending P2'
  },
  {
    id: 'vulnerability',
    label: 'Vulnerability',
    category: 'risk',
    description: 'Social and structural vulnerability.',
    availability: 'pending',
    owner: 'p2',
    pendingReason: 'Pending P2'
  }
];

export const getLayersByCategory = (category: string) => 
  LAYERS.filter(layer => layer.category === category);
