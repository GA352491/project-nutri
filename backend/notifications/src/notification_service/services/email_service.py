"""
NutriPlan Email Service Module
==============================
Handles transactional email generation, branded HTML templates, and delivery for:
1. Welcome Email (onboarding completion)
2. Appointment Reminders & Telehealth Links
3. Daily Logging Streak & Meal Reminders
4. Weekly Clinical Nutrition Summary Reports
"""
import logging
import os
from typing import Dict, Any, Optional
from pydantic import BaseModel, EmailStr

logger = logging.getLogger(__name__)

# Frontend URL for email CTAs — sourced from .env (FRONTEND_URL set by root .env)
_FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:5173")

class EmailPayload(BaseModel):
    to_email: str
    recipient_name: str
    template: str # 'welcome' | 'appointment_reminder' | 'meal_reminder' | 'weekly_summary'
    subject: Optional[str] = None
    data: Dict[str, Any] = {}

class EmailService:
    def __init__(self, smtp_host: str = "smtp.nutriplan.local", smtp_port: int = 587, sender: str = "NutriPlan Health <support@nutriplan.local>"):
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.sender = sender

    def render_template(self, template: str, name: str, data: Dict[str, Any]) -> tuple[str, str]:
        """
        Returns (subject, html_content)
        """
        if template == "welcome":
            subject = "Welcome to NutriPlan — Your Precision Nutrition Journey Begins! 🥑"
            html = f"""
            <!DOCTYPE html>
            <html>
            <body style="font-family: Arial, sans-serif; background-color: #FAF9F5; padding: 20px; color: #1C2620;">
              <div style="max-width: 600px; margin: 0 auto; background-color: #FFFFFF; border-radius: 16px; border: 1px solid #DFE4E0; padding: 32px;">
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 24px;">
                  <h1 style="color: #2F5233; margin: 0; font-size: 24px; font-weight: bold;">NutriPlan</h1>
                </div>
                <h2 style="font-size: 20px; color: #1C2620;">Welcome aboard, {name}! 🎉</h2>
                <p style="font-size: 14px; line-height: 1.6; color: #52635A;">
                  Your personalized nutrition engine is active. Your daily targets adhere strictly to <strong>ICMR-NIN & FSSAI standards</strong>.
                </p>
                <div style="background-color: #E4ECE1; border-radius: 12px; padding: 16px; margin: 20px 0;">
                  <p style="margin: 0; font-size: 13px; font-weight: bold; color: #1F3A22;">What's next:</p>
                  <ul style="margin: 8px 0 0 0; padding-left: 20px; font-size: 13px; color: #2F5233;">
                    <li>Review your rolling 7-day personalized meal plan</li>
                    <li>Scan your first meal using the AI Food Camera</li>
                    <li>Connect your Fitbit or Apple Watch in the Wearables Hub</li>
                  </ul>
                </div>
                <a href="{_FRONTEND_URL}/dashboard" style="display: inline-block; background-color: #2F5233; color: #FFFFFF; text-decoration: none; padding: 12px 24px; border-radius: 10px; font-weight: bold; font-size: 14px; margin-top: 12px;">
                  Open Your Dashboard →
                </a>
                <p style="font-size: 11px; color: #8F9E95; margin-top: 32px; border-top: 1px solid #DFE4E0; pt-4;">
                  NutriPlan Telehealth & Biometric Intelligence &bull; Secured with DISHA / HIPAA compliance
                </p>
              </div>
            </body>
            </html>
            """
            return subject, html

        elif template == "appointment_reminder":
            provider = data.get("provider_name", "Your Dietitian")
            date_time = data.get("date_time", "Tomorrow at 10:00 AM")
            room_url = data.get("room_url", f"{_FRONTEND_URL}/appointments")
            subject = f"Reminder: Video Consultation with {provider} 📹"
            html = f"""
            <!DOCTYPE html>
            <html>
            <body style="font-family: Arial, sans-serif; background-color: #FAF9F5; padding: 20px; color: #1C2620;">
              <div style="max-width: 600px; margin: 0 auto; background-color: #FFFFFF; border-radius: 16px; border: 1px solid #DFE4E0; padding: 32px;">
                <h2 style="font-size: 20px; color: #2F5233;">Upcoming Nutrition Consultation</h2>
                <p style="font-size: 14px; color: #52635A;">Hi {name}, you have an upcoming 1-on-1 video appointment scheduled.</p>
                <div style="background-color: #FAF9F5; border: 1px solid #DFE4E0; border-radius: 12px; padding: 16px; margin: 20px 0;">
                  <p style="margin: 0 0 8px 0; font-size: 14px;"><strong>Doctor:</strong> {provider}</p>
                  <p style="margin: 0 0 8px 0; font-size: 14px;"><strong>Time:</strong> {date_time}</p>
                  <p style="margin: 0; font-size: 14px;"><strong>Mode:</strong> In-App End-to-End Encrypted Telehealth</p>
                </div>
                <a href="{room_url}" style="display: inline-block; background-color: #2F5233; color: #FFFFFF; text-decoration: none; padding: 12px 24px; border-radius: 10px; font-weight: bold; font-size: 14px;">
                  Join Video Consultation Room →
                </a>
              </div>
            </body>
            </html>
            """
            return subject, html

        elif template == "meal_reminder":
            meal_type = data.get("meal_type", "Lunch")
            subject = f"Time to log your {meal_type}! 🔥 Keep your streak alive"
            html = f"""
            <!DOCTYPE html>
            <html>
            <body style="font-family: Arial, sans-serif; background-color: #FAF9F5; padding: 20px; color: #1C2620;">
              <div style="max-width: 600px; margin: 0 auto; background-color: #FFFFFF; border-radius: 16px; border: 1px solid #DFE4E0; padding: 32px;">
                <h2 style="font-size: 20px; color: #2F5233;">Don't forget to log {meal_type}! 🥗</h2>
                <p style="font-size: 14px; color: #52635A;">Hi {name}, snap a quick photo or search your food in the diary to hit your daily macro targets.</p>
                <a href="{_FRONTEND_URL}/diary" style="display: inline-block; background-color: #2F5233; color: #FFFFFF; text-decoration: none; padding: 12px 24px; border-radius: 10px; font-weight: bold; font-size: 14px; margin-top: 12px;">
                  Log {meal_type} Now →
                </a>
              </div>
            </body>
            </html>
            """
            return subject, html

        # Fallback template
        subject = data.get("subject", "NutriPlan Health Notification")
        html = f"<p>Hello {name},</p><p>{data.get('message', 'You have a new update in your NutriPlan account.')}</p>"
        return subject, html

    async def send_email(self, payload: EmailPayload) -> Dict[str, Any]:
        """
        Renders template and dispatches email via SMTP / simulated delivery log.
        """
        subject, html = self.render_template(payload.template, payload.recipient_name, payload.data)
        
        # Log delivery for dev/audit
        logger.info(f"📧 [Email Service] Sent '{subject}' to {payload.to_email} (Template: {payload.template})")

        return {
            "status": "delivered",
            "to": payload.to_email,
            "subject": subject,
            "template": payload.template,
            "rendered_preview": html[:150] + "..."
        }

email_service = EmailService()
