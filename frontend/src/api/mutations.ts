import { useMutation } from '@tanstack/react-query';
import { apiClient } from './client';
import type { OptimizationTransportRequest, OptimizeResponse } from '../data/types';

export function useOptimizationMutation() {
  return useMutation<OptimizeResponse, Error, OptimizationTransportRequest>({
    mutationFn: (requestData) => {
      return apiClient<OptimizeResponse>('/api/optimization/optimize', {
        method: 'POST',
        body: JSON.stringify(requestData),
      });
    },
  });
}
