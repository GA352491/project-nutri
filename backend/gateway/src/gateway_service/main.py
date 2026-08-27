from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from contextlib import asynccontextmanager

from nutriplan_shared.middleware import apply_security_middleware
from .aggregator import aggregate_openapi_specs, fetch_service_health, SERVICES

app = FastAPI(
    title="NutriPlan Unified API Gateway",
    description="Central Documentation & Microservices Directory Portal",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Apply shared security middleware
apply_security_middleware(app, None)

@app.get("/openapi.json", tags=["Gateway"])
async def get_aggregated_openapi():
    """Aggregated OpenAPI JSON from all running microservices."""
    return await aggregate_openapi_specs()

@app.get("/services", tags=["Gateway"])
async def get_services():
    """List all registered microservices and their live health status."""
    return await fetch_service_health()

@app.get("/", response_class=HTMLResponse, tags=["Gateway"])
async def portal_dashboard():
    """Landing portal displaying service cards and direct documentation links."""
    services = await fetch_service_health()
    
    rows = ""
    for svc in services:
        badge_color = "#10b981" if svc["status"] == "online" else "#ef4444"
        badge_text = "ONLINE" if svc["status"] == "online" else "OFFLINE"
        rows += f"""
        <tr style="border-bottom: 1px solid #27352b;">
            <td style="padding: 12px; font-weight: 600; color: #f0fdf4;">{svc['name']}</td>
            <td style="padding: 12px; color: #9ca3af;"><code>{svc['prefix']}</code></td>
            <td style="padding: 12px; color: #9ca3af;"><a href="{svc['url']}" target="_blank" style="color: #4ade80;">{svc['url']}</a></td>
            <td style="padding: 12px;">
                <span style="background: {badge_color}22; color: {badge_color}; border: 1px solid {badge_color}; padding: 3px 8px; border-radius: 9999px; font-size: 11px; font-weight: bold;">
                    {badge_text}
                </span>
            </td>
            <td style="padding: 12px;">
                <a href="{svc['docs']}" target="_blank" style="color: #60a5fa; text-decoration: none; font-size: 13px;">Swagger Docs &rarr;</a>
            </td>
        </tr>
        """

    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>NutriPlan API Gateway Portal</title>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                background-color: #0d130e;
                color: #e5e7eb;
                margin: 0;
                padding: 40px 20px;
                display: flex;
                flex-direction: column;
                align-items: center;
            }}
            .container {{
                max-width: 1000px;
                width: 100%;
            }}
            .header {{
                margin-bottom: 30px;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }}
            h1 {{
                color: #4ade80;
                font-size: 28px;
                margin: 0;
            }}
            .nav-links a {{
                color: #ffffff;
                background: #1e2920;
                border: 1px solid #2e4032;
                padding: 8px 14px;
                border-radius: 6px;
                text-decoration: none;
                margin-left: 10px;
                font-size: 14px;
                font-weight: 500;
            }}
            .nav-links a:hover {{
                background: #27352b;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                background: #141b15;
                border-radius: 8px;
                overflow: hidden;
                box-shadow: 0 4px 6px rgba(0,0,0,0.3);
            }}
            th {{
                background: #1e2920;
                color: #a7f3d0;
                text-align: left;
                padding: 12px;
                font-size: 13px;
                text-transform: uppercase;
                letter-spacing: 0.05em;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div>
                    <h1>🥗 NutriPlan API Gateway</h1>
                    <p style="color: #9ca3af; margin-top: 6px;">Consolidated Microservices Hub & API Registry</p>
                </div>
                <div class="nav-links">
                    <a href="/docs" target="_blank">Unified Swagger UI</a>
                    <a href="/redoc" target="_blank">Unified Redoc</a>
                    <a href="/services" target="_blank">Raw JSON Health</a>
                </div>
            </div>

            <table>
                <thead>
                    <tr>
                        <th>Microservice</th>
                        <th>API Prefix</th>
                        <th>Host & Port</th>
                        <th>Status</th>
                        <th>Quick Link</th>
                    </tr>
                </thead>
                <tbody>
                    {rows}
                </tbody>
            </table>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html)

@app.get("/health", tags=["Gateway"])
async def health():
    return {"status": "ok", "service": "gateway-service"}
