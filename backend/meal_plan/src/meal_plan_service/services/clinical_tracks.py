from typing import Dict, Any, List, Optional
from pydantic import BaseModel

class ClinicalTrackManager:
    """
    Modifies meal plan constraints based on advanced clinical conditions
    and evaluates pre-flight approval gates for high-risk patients.
    """
    
    HIGH_RISK_CONDITIONS = {
        "type_1_diabetes": "High-risk glycemic instability. Requires certified diabetes educator review.",
        "ckd": "Chronic Kidney Disease. Strict restriction on protein, sodium, potassium & phosphorus.",
        "renal_disease": "Renal failure/dialysis protocol. Severe electrolyte imbalance hazard.",
        "gestational_diabetes": "High pregnancy complication risk for maternal & fetal health.",
        "severe_cardiac": "Congestive heart failure or stage-3 hypertension (sodium cap <1200mg)."
    }

    def evaluate_clinical_risk_gate(self, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluates whether a generated AI meal plan requires mandatory pre-flight
        nutritionist approval before being visible to the patient.
        """
        conditions = [str(c).lower() for c in user_profile.get("medical_conditions", [])]
        condition_str = " ".join(conditions) + " " + str(user_profile.get("dietary_restrictions", "")).lower()

        reasons = []
        is_high_risk = False

        for risk_key, explanation in self.HIGH_RISK_CONDITIONS.items():
            if risk_key in condition_str or (risk_key == "ckd" and "kidney" in condition_str):
                is_high_risk = True
                reasons.append(explanation)

        # Biomarker risk check
        hba1c = user_profile.get("hba1c")
        if hba1c and float(hba1c) >= 8.5:
            is_high_risk = True
            reasons.append(f"HbA1c level {hba1c}% exceeds safety threshold (≥8.5%).")

        creatinine = user_profile.get("serum_creatinine")
        if creatinine and float(creatinine) >= 1.4:
            is_high_risk = True
            reasons.append(f"Serum creatinine {creatinine} mg/dL indicates impaired renal function.")

        return {
            "requires_clinical_signoff": is_high_risk,
            "status": "STATUS_REQUIRES_CLINICAL_SIGN_OFF" if is_high_risk else "STATUS_ACTIVE_APPROVED",
            "risk_reasons": reasons,
            "can_auto_assign": not is_high_risk,
            "authorized_roles": ["clinical_nutritionist", "chief_dietitian", "medical_officer"]
        }

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
            modified["calorie_modifier"] = "+500" 
            modified["clinical_rule"] = "MANDATORY: High iron, calcium, and DHA. Include lactation-supporting foods (oats, flaxseed)."
            
        return modified


clinical_tracks = ClinicalTrackManager()

