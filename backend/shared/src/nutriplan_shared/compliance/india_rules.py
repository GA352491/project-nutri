class IndiaComplianceEngine:
    """
    Enforces dietary guidelines specific to India, based on 
    ICMR-NIN (Indian Council of Medical Research - National Institute of Nutrition) recommendations
    and FSSAI (Food Safety and Standards Authority of India) regulations.
    """
    
    def __init__(self):
        # ICMR-NIN 2020 Guidelines
        self.min_protein_g_per_kg = 0.83  # RDA for Indian adults
        self.max_free_sugar_g = 25.0      # < 25g/day (WHO/NIN recommendation)
        self.max_sodium_mg = 2000         # < 2000mg per day (5g salt)
        self.min_iron_mg_female = 29.0    # High iron requirement due to predominant plant-based diets
        
    def validate_plan_compliance(self, plan_macros: dict, user_profile: dict) -> list:
        """
        Validates if a generated meal plan meets Indian dietary guidelines.
        Returns a list of warnings if out of compliance.
        """
        warnings = []
        
        weight_kg = user_profile.get("weight_kg", 65)
        gender = user_profile.get("gender", "male").lower()
        
        total_protein = plan_macros.get("protein_g", 0)
        free_sugar = plan_macros.get("added_sugar_g", 0)
        sodium = plan_macros.get("sodium_mg", 0)
        iron = plan_macros.get("iron_mg", 0)
        
        # Protein Check
        target_protein = weight_kg * self.min_protein_g_per_kg
        if total_protein > 0 and total_protein < target_protein:
            warnings.append(f"Protein ({total_protein}g) is below ICMR-NIN minimum RDA for body weight ({target_protein:.1f}g)")
            
        # Sugar Check
        if free_sugar > self.max_free_sugar_g:
            warnings.append(f"Exceeds NIN recommended limit for free sugars ({free_sugar}g > 25g)")
            
        # Sodium Check (FSSAI / NIN)
        if sodium > self.max_sodium_mg:
            warnings.append(f"Exceeds FSSAI/NIN recommended limit for sodium ({sodium}mg > 2000mg / 5g salt)")
            
        # Iron check for females (Very common deficiency in India)
        if gender == "female" and iron > 0 and iron < self.min_iron_mg_female:
            warnings.append(f"Iron ({iron}mg) is below ICMR-NIN minimum RDA for women ({self.min_iron_mg_female}mg). Recommend adding spinach, lentils, or fortified grains.")
            
        return warnings

india_compliance = IndiaComplianceEngine()
