import uuid
from typing import Dict, Any

class JitsiRoomProvisioner:
    """
    Provisions Jitsi Meet rooms for nutritionist-patient video calls.
    Uses Jitsi's open protocol — no server-side installation needed for MVP.
    The client (web/mobile) simply opens a URL with the room name.
    """

    def __init__(self, jitsi_domain: str = "meet.jit.si"):
        self.jitsi_domain = jitsi_domain

    def create_room(self, appointment_id: str, nutritionist_name: str) -> Dict[str, Any]:
        """
        Generates a unique, secure Jitsi room URL tied to an appointment.
        """
        # Create a unique room name that's hard to guess
        room_token = uuid.uuid4().hex[:12]
        room_name = f"nutriplan-{appointment_id}-{room_token}"

        return {
            "room_name": room_name,
            "join_url": f"https://{self.jitsi_domain}/{room_name}",
            "appointment_id": appointment_id,
            "display_name": f"Session with {nutritionist_name}",
            "config": {
                "startWithAudioMuted": False,
                "startWithVideoMuted": False,
                "disableDeepLinking": True,
                "prejoinPageEnabled": True,
            }
        }

jitsi_provisioner = JitsiRoomProvisioner()
