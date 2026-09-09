/**
 * NutriPlan Services Configuration
 * =================================
 * Single client-side source of truth for microservice URLs and proxy routes.
 * 
 * Domain and scheme are read from VITE_APP_DOMAIN and VITE_APP_SCHEME (.env).
 * When running behind the Vite dev server, requests hit the local origin
 * and are proxied to the target microservices.
 */

const DOMAIN = import.meta.env?.VITE_APP_DOMAIN || 'localhost';
const SCHEME = import.meta.env?.VITE_APP_SCHEME || 'http';

export const serviceUrl = (port: number | string): string => `${SCHEME}://${DOMAIN}:${port}`;

export const SERVICE_PORTS = {
  AUTH: 8001,
  COMPLIANCE: 8002,
  PROFILE: 8003,
  RECIPE: 8004,
  DIARY: 8005,
  GROCERY: 8006,
  SUBSCRIPTIONS: 8007,
  MEAL_PLAN: 8009,
  NOTIFICATIONS: 8010,
  FOOD_RECOGNITION: 8011,
  CHAT: 8012,
  APPOINTMENTS: 8013,
  VIDEO: 8014,
  AI_CHAT: 8015,
  PAYMENT: 8016,
  DELIVERY: 8017,
  WEARABLE: 8018,
  ADMIN: 8019,
  FOOD_VISION: 8020,
  MARKETPLACE: 8025,
} as const;

/**
 * Service base URLs constructed dynamically from the configured domain & scheme
 */
export const SERVICES = {
  auth: serviceUrl(SERVICE_PORTS.AUTH),
  compliance: serviceUrl(SERVICE_PORTS.COMPLIANCE),
  profile: serviceUrl(SERVICE_PORTS.PROFILE),
  recipe: serviceUrl(SERVICE_PORTS.RECIPE),
  diary: serviceUrl(SERVICE_PORTS.DIARY),
  grocery: serviceUrl(SERVICE_PORTS.GROCERY),
  subscriptions: serviceUrl(SERVICE_PORTS.SUBSCRIPTIONS),
  mealPlan: serviceUrl(SERVICE_PORTS.MEAL_PLAN),
  notifications: serviceUrl(SERVICE_PORTS.NOTIFICATIONS),
  chat: serviceUrl(SERVICE_PORTS.CHAT),
  appointments: serviceUrl(SERVICE_PORTS.APPOINTMENTS),
  video: serviceUrl(SERVICE_PORTS.VIDEO),
  aiChat: serviceUrl(SERVICE_PORTS.AI_CHAT),
  payment: serviceUrl(SERVICE_PORTS.PAYMENT),
  delivery: serviceUrl(SERVICE_PORTS.DELIVERY),
  wearables: serviceUrl(SERVICE_PORTS.WEARABLE),
  admin: serviceUrl(SERVICE_PORTS.ADMIN),
  foodVision: serviceUrl(SERVICE_PORTS.FOOD_VISION),
  marketplace: serviceUrl(SERVICE_PORTS.MARKETPLACE),
} as const;

/**
 * Helper to generate proxy table for vite.config.ts or custom proxy tools
 */
export const buildProxyRoutes = (domain = DOMAIN, scheme = SCHEME) => {
  const target = (port: number) => `${scheme}://${domain}:${port}`;
  return {
    '/api/v1/auth': target(SERVICE_PORTS.AUTH),
    '/api/v1/compliance': target(SERVICE_PORTS.COMPLIANCE),
    '/api/v1/user': target(SERVICE_PORTS.PROFILE),
    '/api/v1/profile': target(SERVICE_PORTS.PROFILE),
    '/api/v1/onboarding': target(SERVICE_PORTS.PROFILE),
    '/api/v1/recipes': target(SERVICE_PORTS.RECIPE),
    '/api/v1/diary': target(SERVICE_PORTS.DIARY),
    '/api/v1/grocery': target(SERVICE_PORTS.GROCERY),
    '/api/v1/subscriptions': target(SERVICE_PORTS.SUBSCRIPTIONS),
    '/api/v1/subscription': target(SERVICE_PORTS.SUBSCRIPTIONS),
    '/api/v1/referrals': target(SERVICE_PORTS.SUBSCRIPTIONS),
    '/api/v1/family': target(SERVICE_PORTS.SUBSCRIPTIONS),
    '/api/v1/plan': target(SERVICE_PORTS.MEAL_PLAN),
    '/api/v1/notifications': target(SERVICE_PORTS.NOTIFICATIONS),
    '/api/v1/chat': {
      target: target(SERVICE_PORTS.CHAT),
      ws: true,
    },
    '/api/v1/appointments': target(SERVICE_PORTS.APPOINTMENTS),
    '/api/v1/video': target(SERVICE_PORTS.VIDEO),
    '/api/v1/ai-chat': {
      target: target(SERVICE_PORTS.AI_CHAT),
      ws: true,
    },
    '/api/v1/payment': target(SERVICE_PORTS.PAYMENT),
    '/api/v1/delivery': target(SERVICE_PORTS.DELIVERY),
    '/api/v1/wearables': target(SERVICE_PORTS.WEARABLE),
    '/api/v1/wearable': target(SERVICE_PORTS.WEARABLE),
    '/api/v1/admin': target(SERVICE_PORTS.ADMIN),
    '/api/v1/food-recognition': target(SERVICE_PORTS.FOOD_VISION),
    '/api/v1/marketplace': target(SERVICE_PORTS.MARKETPLACE),
  };
};
