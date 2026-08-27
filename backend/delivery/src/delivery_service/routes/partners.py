from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict, Any
import urllib.parse

router = APIRouter()

class GroceryListRequest(BaseModel):
    items: List[str]
    location: str = "US" # Used to determine which partner to default to

class DeliveryPartner:
    def __init__(self, name: str, base_url: str):
        self.name = name
        self.base_url = base_url

    def generate_deeplink(self, items: List[str]) -> str:
        """
        Generates a partner-specific deep link to automatically populate
        a cart or search query.
        """
        query = " ".join(items)
        encoded_query = urllib.parse.quote(query)
        return f"{self.base_url}?q={encoded_query}"

# MVP Partner configurations
partners = {
    "Instacart": DeliveryPartner("Instacart", "https://www.instacart.com/store/s"),
    "Blinkit": DeliveryPartner("Blinkit", "https://blinkit.com/s"),
    "Zepto": DeliveryPartner("Zepto", "https://www.zeptonow.com/search")
}

@router.post("/checkout-links")
async def get_checkout_links(req: GroceryListRequest) -> Dict[str, Any]:
    """
    Takes a grocery list (missing ingredients) and generates deep links 
    to popular 10-minute grocery delivery apps.
    """
    links = {}
    
    # In a real implementation, we would pass items as an array if the partner API supports it,
    # or just deep link to a search page for the first few items.
    
    # For MVP, we'll just link to a general search of the first 3 items to avoid URL limits
    search_items = req.items[:3]
    
    for partner_name, partner in partners.items():
        links[partner_name] = partner.generate_deeplink(search_items)
        
    return {
        "status": "success",
        "message": "Delivery partner links generated",
        "links": links
    }
