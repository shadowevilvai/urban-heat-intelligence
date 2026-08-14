export type LayerCategory = 'observations' | 'environmental' | 'risk';

export type LayerAvailability = 'available' | 'pending';

export interface LayerDefinition {
  id: string;
  label: string;
  category: LayerCategory;
  description: string;
  availability: LayerAvailability;
  owner: 'p1' | 'p2';
  pendingReason?: string;
}
