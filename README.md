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

### Backend
- **Django 5.2** - Python web framework
- **Django REST Framework** - API development
- **JWT Authentication** - Secure token-based auth
- **Databricks SDK** - Data platform integration
- **Celery** - Background task processing
- **Redis** - Caching and task queue
- **drf-spectacular** - API documentation

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

### Backend Development

1. **Create virtual environment**
   ```bash
   cd source2target-app-v2
   python3 -m venv backend_env
   source backend_env/bin/activate  # On Windows: backend_env\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp env.template .env
   # Edit .env file with your settings
   ```

4. **Run migrations**
   ```bash
   python manage.py migrate
   ```

5. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

6. **Start development server**
   ```bash
   python manage.py runserver
   ```

7. **Access API documentation**
   ```
   http://localhost:8000/api/docs/swagger/
   ```

### Demo Credentials

- **API Admin**: `admin@gainwell.com` / `admin123`
- **Frontend**: `admin@gainwell.com` (any password)
- **Frontend**: `user@gainwell.com` (any password)

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
├── backend/                  # Django project configuration
├── accounts/                 # User authentication & management
├── mapping/                  # Field mapping functionality
├── config_manager/           # Configuration management
├── manage.py                 # Django management script
├── requirements.txt          # Python dependencies
├── env.template             # Environment configuration template
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
- [x] Vue 3 + TypeScript project setup with PrimeVue
- [x] Django REST API backend with JWT authentication
- [x] User authentication system (login/logout/registration)
- [x] User management and role-based permissions
- [x] Main layout with navigation and header
- [x] Introduction page with system status
- [x] Route protection and navigation guards
- [x] API documentation with Swagger/ReDoc
- [x] Responsive design foundation

### 🔄 In Progress
- [ ] Field mapping interface with DataTable
- [ ] Configuration management views
- [ ] Databricks SDK integration
- [ ] AI model and vector search services

### 📋 Planned
- [ ] AI mapping suggestions with foundation models
- [ ] Template upload/download functionality
- [ ] Real-time updates with WebSockets
- [ ] Advanced filtering and search capabilities
- [ ] Data visualization charts and dashboards
- [ ] Background task processing with Celery
- [ ] Comprehensive error handling and logging
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

