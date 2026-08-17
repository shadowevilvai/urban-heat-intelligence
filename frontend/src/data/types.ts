import type * as GeoJSON from 'geojson';

export interface City {
  city_id: string;
  display_name: string;
  feature_count: number;
}

export interface MapFeatureProperties {
  feature_id: string;
  lst_c: number;
  risk_category: string;
  hotspot_context: string;
  hotspot_id: string | null;
}
export interface MapFeature extends GeoJSON.Feature<GeoJSON.Point, MapFeatureProperties> {}

export interface MapFeatureCollection extends GeoJSON.FeatureCollection<GeoJSON.Point, MapFeatureProperties> {}

export interface P1FeatureProperties {
  schema_version: string;
  feature_id: string;
  city: string;
  lst_c: number;
  lst_anomaly_c: number | null;
  ndvi_mean: number | null;
  ndbi_mean: number | null;
  ndwi_mean: number | null;
  land_cover_class: string | null;
  source: string;
  satellite: string;
  date_period_start: string;
  date_period_end: string;
  processing_date: string;
  resolution_m_source: number;
  resolution_m_sample: number;
  coordinate_reference_system: string;
  data_quality: string;
  valid_pixel_percent: number | null;
}

export interface P1Feature extends GeoJSON.Feature<GeoJSON.Point, P1FeatureProperties> {
  id?: string;
}

export interface RiskContributor {
  name: string;
  value: number;
  importance: number;
}

export interface P2Analysis {
  risk_score: number;
  risk_category: string;
  vulnerability_score: number | null;
  contributors: RiskContributor[];
  model_version: string;
  hotspot_context: string;
}

export interface P2RiskAnalysis {
  feature_id: string;
  p1_location: {
    city: string;
    geometry: GeoJSON.Point;
  };
  p1_measurements: Partial<P1FeatureProperties>;
  p1_provenance: Partial<P1FeatureProperties>;
  p2_analysis: P2Analysis;
  hotspot_id?: string;
}

export interface HotspotDetailResponse {
  feature: P1Feature;
  risk: P2RiskAnalysis;
}

export interface OptimizationTransportRequest {
  city_id: string;
  hotspot_ids: string[];
  resource_budget: number;
  interventions: string[];
}

export interface HotspotAllocationDetail {
  hotspot_id: string;
  intervention: string;
  intensity_allocated: number;
  resource_units_used: number;
  expected_cooling_celsius: number;
  scenario_lst_celsius: number;
  limiting_constraints: string[];
}

export interface OptimizeResponse {
  status: string;
  resource_budget: number;
  total_resources_used: number;
  portfolio_objective_value: number;
  total_expected_cooling_celsius: number;
  recommendations: Record<string, number>[];
  hotspot_allocations: HotspotAllocationDetail[];
  limiting_constraints: string[];
  evidence_level: string;
  assumptions: string[];
  model_version: string;
  value_status: string;
}
