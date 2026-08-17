from typing import List, Dict, Any, Optional
from .domain import InterventionType, SuitabilityCategory, ValueStatus
from .schemas import SuitabilityRequest, SuitabilityResponse, InterventionSuitabilityItem
from .config import default_config

def clip_score(value: float, min_val: float = 0.0, max_val: float = 100.0) -> float:
    return max(min_val, min(max_val, value))

class SuitabilityEngine:
    def __init__(self):
        pass

    def calculate_mitigation_need(self, p1_data: Dict[str, Any], p2_data: Dict[str, Any]) -> float:
        """
        Derives the heat mitigation need based purely on P1 environmental signals and P2 risk signals.
        Weights:
        - 30% Absolute Heat (LST normalized 30-50C)
        - 30% Relative Heat (Anomaly normalized 0-5C)
        - 40% P2 Vulnerability Score
        """
        lst_c = p1_data.get("lst_c", 35.0)
        anomaly_c = p1_data.get("lst_anomaly_c", 0.0)
        vuln = p2_data.get("vulnerability_score", 50.0)

        norm_lst = clip_score((lst_c - 30.0) / (50.0 - 30.0) * 100.0)
        norm_anom = clip_score((anomaly_c - 0.0) / (5.0 - 0.0) * 100.0)
        
        thermal_need = 0.5 * norm_lst + 0.5 * norm_anom
        need_score = 0.6 * thermal_need + 0.4 * vuln
        return clip_score(need_score)

    def evaluate_tree_canopy_feasibility(self, p1_data: Dict[str, Any]) -> Tuple[float, List[str], List[str]]:
        ndbi = p1_data.get("ndbi_mean", 0.0)
        ndvi = p1_data.get("ndvi_mean", 0.0)
        lc = p1_data.get("land_cover_class", "")

        limiting_factors = []
        advantages = []
        
        # Base feasibility 100
        score = 100.0
        
        # Penalize if too heavily built
        if ndbi > 0.1:
            penalty = ((ndbi - 0.1) / 0.9) * 80.0
            score -= penalty
            limiting_factors.append(f"High NDBI ({ndbi:.2f}) indicates dense built environment; limited plantable space.")
        else:
            advantages.append("Moderate/low NDBI indicates availability of unbuilt permeable ground.")
            
        # Penalize if already heavily vegetated (diminishing returns / no space for *new* trees)
        if ndvi > 0.4:
            penalty = ((ndvi - 0.4) / 0.6) * 60.0
            score -= penalty
            limiting_factors.append(f"High NDVI ({ndvi:.2f}) indicates existing dense vegetation; diminishing marginal utility.")
        elif 0.1 <= ndvi <= 0.4:
            advantages.append("Moderate NDVI indicates environment supports vegetation but is not saturated.")
            
        if lc == "Vegetation":
            advantages.append("Land cover supports vegetative growth.")
            
        return clip_score(score), limiting_factors, advantages

    def evaluate_cool_roof_feasibility(self, p1_data: Dict[str, Any]) -> Tuple[float, List[str], List[str]]:
        ndbi = p1_data.get("ndbi_mean", 0.0)
        lc = p1_data.get("land_cover_class", "")
        
        limiting_factors = []
        advantages = []
        
        score = 100.0
        
        # Penalize if lacking built structures
        if ndbi < -0.1:
            penalty = ((-0.1 - ndbi) / 0.9) * 90.0
            score -= penalty
            limiting_factors.append(f"Low NDBI ({ndbi:.2f}) indicates lack of built structures (roofs).")
        else:
            advantages.append("NDBI indicates sufficient built infrastructure for surface coating.")
            
        if lc == "Built-up":
            score += 10.0
            advantages.append("Confirmed built-up land cover.")
        else:
            score -= 20.0
            limiting_factors.append(f"Land cover is '{lc}', which may lack conventional roof structures.")
            
        return clip_score(score), limiting_factors, advantages

    def evaluate(self, hotspot_id: str, p1_data: Dict[str, Any], p2_data: Dict[str, Any], interventions: Optional[List[str]] = None) -> SuitabilityResponse:
        context = p2_data.get("hotspot_context", "terrestrial_other")
        risk = p2_data.get("risk_score", 0.0)
        observed_lst = p1_data.get("lst_c", 0.0)
        
        need_score = self.calculate_mitigation_need(p1_data, p2_data)
        
        supported = [InterventionType.TREE_CANOPY, InterventionType.COOL_ROOF]
        if interventions:
            supported = [InterventionType(i) for i in interventions if i in [t.value for t in InterventionType]]
            
        items = []
        for itype in supported:
            spec = default_config.get(itype)
            
            # Base context filters
            if context == "water":
                feasibility = 0.0
                suit_score = 0.0
                cat = SuitabilityCategory.UNSUITABLE
                lim = ["Water bodies strictly exclude conventional mitigation interventions."]
                adv = []
            elif context == "industrial_mining_candidate":
                if itype == InterventionType.TREE_CANOPY:
                    feasibility = 0.0
                    suit_score = 0.0
                    cat = SuitabilityCategory.UNSUITABLE
                    lim = ["Industrial/mining zones strictly exclude conventional tree planting."]
                    adv = []
                elif itype == InterventionType.COOL_ROOF:
                    lc = p1_data.get("land_cover_class", "")
                    if lc == "Built-up":
                        feasibility, lim, adv = self.evaluate_cool_roof_feasibility(p1_data)
                        suit_score = 0.4 * need_score + 0.6 * feasibility
                        cat = SuitabilityCategory.MEDIUM if suit_score >= 40 else SuitabilityCategory.LOW
                        lim.append("Industrial/mining context requires verification of roof structures.")
                    else:
                        feasibility = 0.0
                        suit_score = 0.0
                        cat = SuitabilityCategory.UNSUITABLE
                        lim = ["No verified built-up/roof evidence in current P1 data."]
                        adv = []
            else:
                # Terrestrial / Urban
                if itype == InterventionType.TREE_CANOPY:
                    feasibility, lim, adv = self.evaluate_tree_canopy_feasibility(p1_data)
                elif itype == InterventionType.COOL_ROOF:
                    feasibility, lim, adv = self.evaluate_cool_roof_feasibility(p1_data)
                else:
                    feasibility, lim, adv = 0.0, ["Unsupported intervention."], []
                    
                suit_score = 0.4 * need_score + 0.6 * feasibility
                
                if suit_score >= 70:
                    cat = SuitabilityCategory.HIGH
                elif suit_score >= 40:
                    cat = SuitabilityCategory.MEDIUM
                else:
                    cat = SuitabilityCategory.LOW
            
            item = InterventionSuitabilityItem(
                intervention=itype.value,
                name=spec.name,
                suitability_score=round(suit_score, 2),
                category=cat,
                heat_mitigation_need_score=round(need_score, 2),
                feasibility_score=round(feasibility, 2),
                limiting_factors=lim,
                advantages=adv,
                status=ValueStatus.DERIVED
            )
            items.append(item)
            
        return SuitabilityResponse(
            hotspot_id=hotspot_id,
            observed_lst_celsius=round(observed_lst, 2),
            risk_score=round(risk, 2),
            suitabilities=items,
            status=ValueStatus.DERIVED
        )

default_suitability_engine = SuitabilityEngine()
