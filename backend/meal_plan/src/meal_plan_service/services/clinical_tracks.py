from typing import Dict, Any, List

class ClinicalTrackManager:
    """
    Modifies meal plan constraints based on advanced clinical conditions.
    """
    
    def apply_clinical_constraints(self, condition: str, base_constraints: Dict[str, Any]) -> Dict[str, Any]:
        """
        Takes a user's clinical condition and injects mandatory safety constraints 
        into the LLM or Curated engine prompt.
        """
        condition_lower = condition.lower()
        modified = base_constraints.copy()
        
        if "diabetes" in condition_lower:
            modified["max_glycemic_index"] = 55
            modified["clinical_rule"] = "MANDATORY: Focus on complex carbohydrates. No refined sugars. Limit total carbs per meal to 45g."
            
        elif "pcos" in condition_lower:
            modified["clinical_rule"] = "MANDATORY: High protein, low glycemic index. Emphasize anti-inflammatory foods (omega-3s). Avoid dairy and refined carbs if possible."
            
        elif "ckd" in condition_lower or "renal" in condition_lower:
            modified["max_sodium_mg"] = 1500
            modified["max_potassium_mg"] = 2000
            modified["max_phosphorus_mg"] = 800
            modified["clinical_rule"] = "CRITICAL: Renal diet. Strictly limit Sodium to 1500mg, Potassium to 2000mg, and Phosphorus to 800mg daily. Moderate protein."
            
        elif "post-partum" in condition_lower:
            # Calorie surplus if breastfeeding
            modified["calorie_modifier"] = "+500" 
            modified["clinical_rule"] = "MANDATORY: High iron, calcium, and DHA. Include lactation-supporting foods (oats, flaxseed)."
            
        return modified

clinical_tracks = ClinicalTrackManager()
