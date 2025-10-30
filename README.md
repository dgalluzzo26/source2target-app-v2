# Source-to-Target Mapping Platform v2

A modern Vue.js + Django implementation of the Gainwell Source-to-Target mapping platform with enhanced UI/UX and API-first architecture.

## 🚀 Features

- **Modern Frontend**: Vue 3 + TypeScript + PrimeVue components
- **Professional UI**: Responsive design with Aura theme
- **Authentication**: JWT-based user authentication with role management
- **AI-Powered Mapping**: Intelligent field mapping suggestions
- **Data Discovery**: Browse and analyze source tables and columns
- **Template System**: Bulk upload/download of mappings via CSV
- **Real-time Updates**: WebSocket support for live updates
- **API-First**: Django REST Framework backend

## 🛠 Tech Stack

### Frontend
- **Vue 3** - Progressive JavaScript framework
- **TypeScript** - Type-safe development
- **PrimeVue** - Rich UI component library
- **Pinia** - State management
- **Vue Router** - Client-side routing
- **Axios** - HTTP client
- **Vite** - Fast build tool

### Backend (Coming Soon)
- **Django 4.2** - Python web framework
- **Django REST Framework** - API development
- **Databricks SDK** - Data platform integration
- **JWT Authentication** - Secure token-based auth
- **Celery** - Background task processing

## 🏃‍♂️ Quick Start

### Frontend Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/dgalluzzo26/source2target-app-v2.git
   cd source2target-app-v2/frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start development server**
   ```bash
   npm run dev
   ```

4. **Open in browser**
   ```
   http://localhost:5173
   ```

### Demo Credentials

- **Admin User**: `admin@gainwell.com` (any password)
- **Regular User**: `user@gainwell.com` (any password)

## 📁 Project Structure

```
source2target-app-v2/
├── frontend/                 # Vue.js application
│   ├── src/
│   │   ├── components/       # Reusable Vue components
│   │   ├── views/           # Page components
│   │   ├── stores/          # Pinia state management
│   │   ├── router/          # Vue Router configuration
│   │   └── assets/          # Static assets
│   ├── package.json
│   └── vite.config.ts
├── backend/                  # Django API (coming soon)
└── README.md
```

## 🎨 UI Components

The application uses PrimeVue components for a professional look and feel:

- **DataTable** - Advanced data grids with filtering, sorting, pagination
- **Card** - Content containers with headers and actions
- **Button** - Various button styles and states
- **InputText/Password** - Form inputs with validation
- **Tag/Badge** - Status indicators and labels
- **Message/Toast** - User feedback and notifications
- **Dialog/Sidebar** - Modal and overlay components

## 🔐 Authentication Flow

1. User visits protected route
2. Redirected to login page if not authenticated
3. Login with email/password
4. JWT token stored in localStorage
5. User redirected to requested page
6. Navigation guards protect admin routes

## 📱 Responsive Design

- **Desktop**: Full sidebar navigation with header
- **Tablet**: Collapsible sidebar with responsive layout
- **Mobile**: Hidden sidebar with hamburger menu (coming soon)

## 🚧 Development Status

### ✅ Completed
- [x] Vue 3 + TypeScript project setup
- [x] PrimeVue integration with Aura theme
- [x] Authentication system with login/logout
- [x] Main layout with navigation and header
- [x] Introduction page with system status
- [x] Route protection and navigation guards
- [x] Responsive design foundation

### 🔄 In Progress
- [ ] Field mapping interface with DataTable
- [ ] Configuration management views
- [ ] API service layer integration

### 📋 Planned
- [ ] Django REST API backend
- [ ] Databricks integration
- [ ] AI mapping suggestions
- [ ] Template upload/download
- [ ] Real-time updates with WebSockets
- [ ] Advanced filtering and search
- [ ] Data visualization charts
- [ ] Mobile-optimized interface

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is proprietary software developed for Gainwell Technologies.

## 📞 Support

For questions or support, please contact the development team.
