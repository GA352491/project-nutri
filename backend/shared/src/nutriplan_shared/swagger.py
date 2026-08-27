from typing import Any, Dict

def get_swagger_metadata(title: str, description: str, version: str) -> Dict[str, Any]:
    """
    Returns common FastAPI kwargs for Swagger/OpenAPI documentation.
    """
    return {
        "title": title,
        "description": description,
        "version": version,
        "contact": {
            "name": "NutriPlan Engineering",
            "url": "https://nutriplan.local",
        },
        "license_info": {
            "name": "Proprietary",
        },
    }
