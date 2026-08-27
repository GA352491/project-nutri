from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Any
from ..services.jitsi_provisioner import jitsi_provisioner

router = APIRouter()

class ProvisionRoomRequest(BaseModel):
    appointment_id: str
    nutritionist_name: str

@router.post("/provision")
async def provision_room(req: ProvisionRoomRequest) -> Dict[str, Any]:
    """
    Provisions a Jitsi meeting room for a specific appointment.
    """
    room_details = jitsi_provisioner.create_room(
        appointment_id=req.appointment_id,
        nutritionist_name=req.nutritionist_name
    )
    return room_details
