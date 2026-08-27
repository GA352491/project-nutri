from abc import ABC, abstractmethod
from ..schemas.compliance_schemas import UserProfileData, ComplianceReport

class ComplianceRuleEngine(ABC):
    
    @abstractmethod
    def evaluate(self, profile: UserProfileData) -> ComplianceReport:
        pass
