/**
 * Application configuration for frontend-only deployment
 */

export const APP_CONFIG = {
  // Frontend-only mode - no backend API calls
  FRONTEND_ONLY: true,
  
  // App metadata
  APP_TITLE: 'Source-to-Target Mapping Platform',
  APP_VERSION: '2.0.0',
  
  // API configuration (disabled for frontend-only)
  API_BASE_URL: '',
  API_ENABLED: false,
  
  // Demo/dummy data configuration
  DEMO_MODE: true,
  
  // Deployment target
  DEPLOYMENT_TARGET: 'databricks'
}

export default APP_CONFIG
