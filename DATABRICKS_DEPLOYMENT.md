# Databricks Frontend Deployment Guide

This guide explains how to deploy the Source-to-Target Mapping Platform frontend to Databricks as a static web application.

## Overview

The frontend has been configured for **frontend-only deployment** with:
- ✅ All backend API calls disabled
- ✅ Dummy data for all functionality
- ✅ No external dependencies
- ✅ Self-contained static files

## Prerequisites

1. **Node.js** (v20.19.0 or higher)
2. **npm** or **yarn**
3. **Databricks workspace** with file upload capabilities

## Build for Databricks

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Build for Production

```bash
npm run build:databricks
```

This creates optimized static files in the `dist/` directory.

### 3. Verify Build

```bash
npm run preview
```

Visit `http://localhost:4173` to test the built application.

## Deployment Options

### Option 1: Databricks File System (DBFS)

1. **Upload to DBFS**:
   ```bash
   # Upload the entire dist folder to DBFS
   databricks fs cp -r dist/ dbfs:/FileStore/shared_uploads/s2t-mapping-app/
   ```

2. **Access via DBFS**:
   - Navigate to: `https://<your-workspace>.cloud.databricks.com/files/shared_uploads/s2t-mapping-app/index.html`

### Option 2: Databricks Repos

1. **Create a Repo**:
   - Go to Databricks workspace → Repos
   - Create new repo or clone this repository

2. **Upload Built Files**:
   - Upload the contents of `dist/` to the repo
   - Access via the repo's web interface

### Option 3: Databricks Apps (Recommended)

1. **Create Databricks App**:
   ```python
   # In a Databricks notebook
   import os
   import shutil
   
   # Copy built files to app directory
   app_dir = "/Workspace/Users/<your-email>/s2t-mapping-app"
   os.makedirs(app_dir, exist_ok=True)
   
   # Upload your dist files here
   ```

2. **Configure App**:
   - Set up routing for the SPA
   - Configure any necessary permissions

## Application Features (Frontend-Only Mode)

### ✅ Fully Functional
- **Configuration Management**: All 7 tabs with import/export
- **Field Mapping Interface**: 3 tabs with dummy healthcare data
- **User Interface**: Complete Gainwell branding and responsive design
- **Navigation**: All pages accessible
- **Interactive Elements**: Forms, tables, dialogs, file upload/download

### 🔄 Simulated (Dummy Data)
- **Database Connections**: Simulated test results
- **AI Suggestions**: Pre-defined mapping suggestions
- **Vector Search**: Mock search results
- **Template Upload**: File processing simulation
- **User Authentication**: Demo user automatically loaded

## File Structure

```
dist/
├── index.html              # Main application entry point
├── assets/
│   ├── index-[hash].js     # Application JavaScript
│   ├── index-[hash].css    # Application styles
│   └── gainwell-logo-*.png # Gainwell branding assets
└── [other static assets]
```

## Configuration

The app is configured via `src/config/app.ts`:

```typescript
export const APP_CONFIG = {
  FRONTEND_ONLY: true,        // Disables all API calls
  DEMO_MODE: true,           // Uses dummy data
  DEPLOYMENT_TARGET: 'databricks'
}
```

## Troubleshooting

### Issue: App doesn't load
- **Solution**: Ensure all files are uploaded and `index.html` is accessible

### Issue: Routing problems
- **Solution**: Configure your web server to serve `index.html` for all routes (SPA routing)

### Issue: Assets not loading
- **Solution**: Check that the `assets/` directory is uploaded with correct permissions

## Development vs Production

| Feature | Development | Frontend-Only Production |
|---------|-------------|-------------------------|
| Backend API | ✅ Connected | ❌ Disabled |
| Database | ✅ Real data | 🔄 Dummy data |
| Authentication | ✅ Databricks auth | 🔄 Demo user |
| AI Suggestions | ✅ Real AI | 🔄 Pre-defined |
| File Operations | ✅ Real upload/download | 🔄 Simulated |

## Next Steps

After testing the frontend deployment:

1. **Backend Integration**: Deploy Django backend to connect real data
2. **Databricks Authentication**: Integrate with Databricks user context
3. **Real AI Models**: Connect to Databricks Foundation Models
4. **Vector Search**: Implement actual vector search functionality

## Support

For deployment issues:
1. Check Databricks workspace permissions
2. Verify file upload locations
3. Test with simple HTML file first
4. Contact Databricks support for platform-specific issues
