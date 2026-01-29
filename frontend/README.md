# BOOMS Platform - Frontend

React + TypeScript + Vite frontend for BOOMS Platform.

## Features

- 🔐 JWT Authentication (Login/Register)
- 📊 Account Management Dashboard
- 🤖 AI Chat Interface for Stages 1-2
- 📥 PDF/Excel Export
- 🎨 Modern UI with Tailwind CSS
- 🚀 Fast Development with Vite

## Tech Stack

- **React 18** - UI Library
- **TypeScript** - Type Safety
- **Vite** - Build Tool
- **React Router** - Navigation
- **Axios** - HTTP Client
- **Tailwind CSS** - Styling
- **Lucide React** - Icons

## Getting Started

### Prerequisites

- Node.js 18+ installed
- Backend server running on http://localhost:8000

### Installation

```bash
npm install
```

### Development

```bash
npm run dev
```

The app will be available at http://localhost:5173/

### Build for Production

```bash
npm run build
npm run preview  # Preview production build
```

## Project Structure

```
src/
├── components/          # Reusable components
│   ├── CreateAccountModal.tsx
│   ├── Loading.tsx
│   ├── Navbar.tsx
│   └── ProtectedRoute.tsx
├── context/             # React Context
│   └── AuthContext.tsx  # Auth state management
├── pages/               # Page components
│   ├── Login.tsx
│   ├── Register.tsx
│   ├── Dashboard.tsx
│   ├── AccountDetail.tsx
│   └── StageChat.tsx
├── services/            # API services
│   └── api.ts           # Axios API client
├── types/               # TypeScript types
│   └── index.ts
├── App.tsx              # Main app component
├── main.tsx             # Entry point
└── index.css            # Global styles
```

## Usage

### 1. Register/Login

Navigate to http://localhost:5173/register to create an account or http://localhost:5173/login to sign in.

### 2. Create Account

On the dashboard, click "New Account" to create a client account. This automatically creates all 7 stages.

### 3. Work Through Stages

- Click on a stage to start the AI conversation
- Stage 1 (BOOMS) analyzes brand and market
- Stage 2 (Journey) maps customer journey
- Stages unlock sequentially as you complete them

### 4. Export Results

Once stages are completed, use the "Export PDF" or "Export Excel" buttons on the account detail page.

## API Configuration

The frontend connects to the backend at `http://localhost:8000` by default.

To change this, edit `src/services/api.ts`:

```typescript
const API_BASE_URL = 'http://localhost:8000';
```

## Environment Variables

Create a `.env` file if needed:

```
VITE_API_URL=http://localhost:8000
```

## Available Routes

- `/` - Dashboard (list of accounts)
- `/login` - Login page
- `/register` - Registration page
- `/accounts/:id` - Account detail with stages
- `/accounts/:id/stages/:num` - Chat with AI agent for specific stage

## Features by Page

### Dashboard
- List all client accounts
- Create new accounts
- Quick access to account details

### Account Detail
- View all 7 stages with status
- Export completed work to PDF/Excel
- Navigate to individual stages

### Stage Chat
- Real-time chat with AI agents
- STATELESS - full conversation history maintained
- Auto-completion detection
- Stage unlocking after completion

## Development Tips

- Use React DevTools for debugging
- Check Network tab in browser for API calls
- TypeScript will catch type errors during development
- Tailwind CSS IntelliSense extension recommended for VS Code

## Troubleshooting

### Backend Connection Issues

Make sure the backend is running on http://localhost:8000:
```bash
cd ../backend
poetry run uvicorn app.main:app --port 8000
```

### CORS Errors

The backend is configured to allow requests from http://localhost:5173. If using a different port, update `backend/app/config.py`:

```python
CORS_ORIGINS=["http://localhost:5173"]
```

### Build Errors

Clear node_modules and reinstall:
```bash
rm -rf node_modules package-lock.json
npm install
```

## Future Enhancements

- Add Stages 3-7 agents
- Real-time progress indicators
- Advanced export options
- Team collaboration features
- Analytics dashboard
- Dark mode support

## License

Proprietary - BOOMS Platform
