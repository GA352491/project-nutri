class USComplianceEngine:
    """
    Enforces USDA/FDA specific dietary guidelines.
    """
    
    def __init__(self):
        # USDA 2020-2025 Dietary Guidelines limits
        self.max_added_sugar_pct = 0.10  # < 10% of total calories
        self.max_sat_fat_pct = 0.10      # < 10% of total calories
        self.max_sodium_mg = 2300        # < 2300mg per day
        
    def validate_plan_compliance(self, plan_macros: dict) -> list:
        """
        Validates if a generated meal plan meets US federal dietary guidelines.
        Returns a list of warnings if out of compliance.
        """
        warnings = []
        
        total_cals = plan_macros.get("calories", 0)
        added_sugar = plan_macros.get("added_sugar_g", 0)
        sat_fat = plan_macros.get("saturated_fat_g", 0)
        sodium = plan_macros.get("sodium_mg", 0)
        
        if total_cals == 0:
            return warnings
            
        # 1g sugar = 4 cals, 1g fat = 9 cals
        sugar_cals = added_sugar * 4
        sat_fat_cals = sat_fat * 9
        
        if (sugar_cals / total_cals) > self.max_added_sugar_pct:
            warnings.append("Exceeds USDA recommended limit for added sugars (>10% total calories)")
            
        if (sat_fat_cals / total_cals) > self.max_sat_fat_pct:
            warnings.append("Exceeds USDA recommended limit for saturated fats (>10% total calories)")
            
        if sodium > self.max_sodium_mg:
            warnings.append(f"Exceeds FDA recommended limit for sodium ({sodium}mg > 2300mg)")
            
        return warnings

us_compliance = USComplianceEngine()
