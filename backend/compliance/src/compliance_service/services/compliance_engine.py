"""
Compliance Engine — dispatches to the correct regional rule engine.

Supported regions:
  IN — ICMR-NIN 2020 (India)
  US — USDA DGA 2020-2025 / FDA Daily Values

Both engines support clinical_condition modifiers:
  diabetes, PCOS, CKD, post_partum
"""
from ..schemas.compliance_schemas import UserProfileData, ComplianceReport
from ..rules.in_rules import IndiaICMRRules
from ..rules.us_rules import USFDADGARules


class ComplianceEngine:
    """
    Factory that selects and runs the appropriate regional rule engine
    based on the user's profile region.
    """

    def __init__(self, region: str = "IN"):
        self.region = region.upper()
        if self.region == "US":
            self.rule_engine = USFDADGARules()
        else:
            # Default: India (ICMR-NIN)
            self.rule_engine = IndiaICMRRules()

    def generate_report(self, profile: UserProfileData) -> ComplianceReport:
        return self.rule_engine.evaluate(profile)


def get_engine(region: str = "IN") -> ComplianceEngine:
    return ComplianceEngine(region=region)
