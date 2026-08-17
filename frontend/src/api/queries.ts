import { useQuery } from '@tanstack/react-query';
import { apiClient } from './client';
import type { City, MapFeatureCollection, HotspotDetailResponse } from '../data/types';

export const queryKeys = {
  cities: ['cities'] as const,
  cityMap: (cityId: string | null) => ['cityMap', cityId] as const,
  hotspotDetail: (cityId: string | null, featureId: string | null) => 
    ['hotspotDetail', cityId, featureId] as const,
};

export function useCities() {
  return useQuery<City[]>({
    queryKey: queryKeys.cities,
    queryFn: () => apiClient<City[]>('/api/cities'),
    staleTime: Infinity, // City list doesn't change during session
  });
}

export function useCityMap(cityId: string | null) {
  return useQuery<MapFeatureCollection>({
    queryKey: queryKeys.cityMap(cityId),
    queryFn: () => {
      if (!cityId) throw new Error('cityId is required');
      return apiClient<MapFeatureCollection>(`/api/cities/${cityId}/map`);
    },
    enabled: !!cityId,
    staleTime: Infinity, // Spatial P1 data is static for the session
  });
}

export function useHotspotDetail(cityId: string | null, featureId: string | null) {
  return useQuery<HotspotDetailResponse>({
    queryKey: queryKeys.hotspotDetail(cityId, featureId),
    queryFn: () => {
      if (!cityId || !featureId) throw new Error('cityId and featureId are required');
      return apiClient<HotspotDetailResponse>(`/api/hotspots/${cityId}/${featureId}`);
    },
    enabled: !!cityId && !!featureId,
    staleTime: 5 * 60 * 1000, // Cache hotspot details for a reasonable time
  });
}
