# Chariot Security - Frontend

React + TypeScript frontend for the Chariot Security Platform.

## 🚀 Quick Start

\\\ash
# Install dependencies
npm install

# Copy environment variables
cp .env.example .env

# Start development server
npm run dev
\\\

The application will be available at http://localhost:3000

## 📁 Project Structure

\\\
src/
├── components/      # Reusable UI components
├── pages/          # Page components (Dashboard, Login, etc.)
├── services/       # API and WebSocket services
├── utils/          # Helper functions
└── App.tsx         # Main application component
\\\

## 🔧 Available Scripts

- \
pm run dev\ - Start development server
- \
pm run build\ - Build for production
- \
pm run preview\ - Preview production build
- \
pm run lint\ - Run ESLint

## 🎨 Tech Stack

- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **React Router** - Routing
- **Axios** - HTTP client
- **Socket.IO** - Real-time communication
- **Recharts** - Data visualization

## 🔌 API Integration

The frontend connects to the backend at \http://localhost:8000\ by default.

### Authentication
All authenticated requests include JWT token in Authorization header:
\\\	ypescript
Authorization: Bearer <token>
\\\

### Available Services

1. **authService** - User authentication
2. **securityService** - Security threats and analysis
3. **websocket** - Real-time updates

## 🎯 Key Features to Build

### Phase 1: Core Features
- [ ] User authentication (login/logout)
- [ ] Security dashboard with real-time stats
- [ ] Threat alerts list
- [ ] Transaction analysis interface

### Phase 2: Advanced Features
- [ ] User profile management
- [ ] Subscription management
- [ ] Payment integration (USDT + Paystack)
- [ ] Community/affiliate dashboard
- [ ] Advanced filtering and search

### Phase 3: Polish
- [ ] Dark mode support
- [ ] Mobile responsive design
- [ ] Loading states and error handling
- [ ] Notifications system
- [ ] Analytics dashboard
- [ ] Export reports functionality

## 🎨 UI Components to Create

### Priority Components
1. **SecurityCard** - Display security metrics
2. **ThreatList** - List of security threats
3. **RiskMeter** - Visual risk score indicator
4. **TransactionAnalyzer** - Input for transaction analysis
5. **AlertBanner** - Real-time alert notifications
6. **ChartComponent** - Data visualization
7. **Navigation** - Sidebar/header navigation
8. **Modal** - Reusable modal dialogs

### Form Components
- Input fields with validation
- Select dropdowns
- Date pickers
- File upload
- Multi-step forms

## 🔔 Real-time Events

Listen to these WebSocket events:

\\\	ypescript
websocket.on('security_alert', (alert) => {
  // Handle new security alert
})

websocket.on('transaction_analysis', (result) => {
  // Handle transaction analysis result
})

websocket.on('subscription_update', (status) => {
  // Handle subscription changes
})
\\\

## 🎨 Design Guidelines

- Use Tailwind utility classes
- Follow mobile-first responsive design
- Maintain consistent spacing (4px grid)
- Use provided color palette
- Ensure WCAG AA accessibility

### Color Palette
- Primary: \#6366f1\ (Indigo)
- Secondary: \#8b5cf6\ (Purple)
- Danger: \#ef4444\ (Red)
- Success: \#10b981\ (Green)
- Warning: \#f59e0b\ (Amber)

## 📝 Code Style

- Use functional components with hooks
- Use TypeScript interfaces for props
- Follow naming conventions:
  - Components: PascalCase
  - Functions: camelCase
  - Constants: UPPER_SNAKE_CASE
- Add proper error handling
- Include loading states
- Write meaningful comments

## 🧪 Testing (To Be Implemented)

\\\ash
npm run test
\\\

## 📦 Build for Production

\\\ash
npm run build
\\\

Build output will be in the \dist/\ directory.

## 🤝 Working with Backend

The backend API documentation will be available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 📞 Support

Contact the backend team for:
- API endpoint documentation
- WebSocket event specifications
- Authentication flow issues
- Data structure questions
