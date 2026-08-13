import type * as GeoJSON from 'geojson';

export interface P1SpatialFeatureProperties {
  schema_version: string;
  feature_id: string;
  city: string;
  lst_c: number;
  lst_anomaly_c: number | null;
  source: string;
  satellite: string;
  date_period_start: string;
  date_period_end: string;
  processing_date: string;
  resolution_m_source: number;
  resolution_m_sample: number;
  coordinate_reference_system: string;
  data_quality: string;
  valid_pixel_percent: number;
  ndvi_mean: number;
  ndbi_mean: number;
  ndwi_mean: number;
  land_cover_class: string;

  // P2-owned fields (optional/nullable as P2 determines risk/hotspot logic)
  hotspot_id?: string | null;
  hotspot_score?: number | null;
  confidence?: number | null;
}

export interface SpatialFeature extends GeoJSON.Feature<GeoJSON.Point, P1SpatialFeatureProperties> {}

export interface SpatialFeatureCollection extends GeoJSON.FeatureCollection<GeoJSON.Point, P1SpatialFeatureProperties> {}
