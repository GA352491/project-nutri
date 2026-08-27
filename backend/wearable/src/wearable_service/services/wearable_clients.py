from typing import Dict, Any

class HealthKitClient:
    """
    Client for abstracting iOS HealthKit data integration.
    In a real app, this would process encrypted JSON payloads sent from the 
    Flutter mobile app's native HealthKit bridge.
    """
    def parse_activity_payload(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parses raw HealthKit payload into standard NutriPlan activity metrics.
        """
        active_energy_burned = payload.get("activeEnergyBurned", 0)
        basal_energy_burned = payload.get("basalEnergyBurned", 0)
        steps = payload.get("stepCount", 0)
        
        return {
            "source": "Apple HealthKit",
            "active_cals": active_energy_burned,
            "basal_cals": basal_energy_burned,
            "total_cals": active_energy_burned + basal_energy_burned,
            "steps": steps
        }

class HealthConnectClient:
    """
    Client for abstracting Android Health Connect data integration.
    """
    def parse_activity_payload(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parses raw Health Connect payload into standard NutriPlan activity metrics.
        """
        active_cals = payload.get("activeCalories", 0)
        bmr = payload.get("bmr", 0)
        steps = payload.get("steps", 0)
        
        return {
            "source": "Google Health Connect",
            "active_cals": active_cals,
            "basal_cals": bmr,
            "total_cals": active_cals + bmr,
            "steps": steps
        }
