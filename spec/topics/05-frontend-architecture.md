# Especificación: Arquitectura Frontend

## Stack Tecnológico

- **Framework**: React 18+ con TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **UI Components**: shadcn/ui
- **Routing**: React Router v6
- **State Management**: React Context API + hooks personalizados
- **HTTP Client**: Axios
- **Forms**: React Hook Form + Zod (validación)

## Estructura de Directorios

```
frontend/
├── src/
│   ├── components/
│   │   ├── ui/              # shadcn/ui components
│   │   ├── layout/
│   │   │   ├── Header.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   └── Layout.tsx
│   │   ├── auth/
│   │   │   ├── LoginForm.tsx
│   │   │   └── RegisterForm.tsx
│   │   ├── dashboard/
│   │   │   ├── AccountCard.tsx
│   │   │   ├── AccountList.tsx
│   │   │   └── CreateAccountModal.tsx
│   │   ├── pipeline/
│   │   │   ├── PipelineView.tsx
│   │   │   ├── StageCard.tsx
│   │   │   └── StageStatusBadge.tsx
│   │   ├── chat/
│   │   │   ├── ChatInterface.tsx
│   │   │   ├── MessageBubble.tsx
│   │   │   ├── ChatInput.tsx
│   │   │   └── ProgressBar.tsx
│   │   ├── output/
│   │   │   ├── OutputView.tsx
│   │   │   ├── ExportButtons.tsx
│   │   │   └── OutputRenderer.tsx
│   │   └── settings/
│   │       ├── AIModelSelector.tsx
│   │       └── AccountSettings.tsx
│   ├── pages/
│   │   ├── LoginPage.tsx
│   │   ├── RegisterPage.tsx
│   │   ├── DashboardPage.tsx
│   │   ├── AccountDetailPage.tsx
│   │   ├── ChatPage.tsx
│   │   └── OutputPage.tsx
│   ├── contexts/
│   │   ├── AuthContext.tsx
│   │   └── AccountContext.tsx
│   ├── hooks/
│   │   ├── useAuth.ts
│   │   ├── useAccounts.ts
│   │   ├── useStages.ts
│   │   └── useChat.ts
│   ├── services/
│   │   ├── api.ts           # Axios instance configurada
│   │   ├── auth.service.ts
│   │   ├── accounts.service.ts
│   │   ├── stages.service.ts
│   │   └── chat.service.ts
│   ├── types/
│   │   ├── auth.types.ts
│   │   ├── account.types.ts
│   │   ├── stage.types.ts
│   │   └── chat.types.ts
│   ├── utils/
│   │   ├── validators.ts
│   │   └── formatters.ts
│   ├── App.tsx
│   ├── main.tsx
│   └── index.css
├── public/
├── package.json
├── tsconfig.json
├── vite.config.ts
└── tailwind.config.js
```

## Tipos TypeScript Principales

### auth.types.ts

```typescript
export interface User {
  id: string;
  email: string;
  fullName: string;
}

export interface AuthResponse {
  user: User;
  token: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  password: string;
  fullName: string;
}
```

### account.types.ts

```typescript
export interface Account {
  id: string;
  userId: string;
  clientName: string;
  aiModel: AIModel;
  completedStages: number;
  lastActivity: string;
  createdAt: string;
}

export type AIModel = 'openai-gpt4o' | 'anthropic-claude-opus-4' | 'google-gemini-2.5-pro';
```

### stage.types.ts

```typescript
export type StageStatus = 'locked' | 'unlocked' | 'in_progress' | 'completed' | 'invalidated';

export interface Stage {
  id: string;
  accountId: string;
  stageNumber: 1 | 2 | 3 | 4 | 5 | 6 | 7;
  status: StageStatus;
  aiModelUsed?: string;
  conversationState?: any;
  output?: any;
  startedAt?: string;
  completedAt?: string;
}

export interface StageConfig {
  number: number;
  name: string;
  description: string;
  icon: string;
}

export const STAGE_CONFIGS: StageConfig[] = [
  { number: 1, name: 'Booms, the Buyer Persona Architect', description: 'Construye buyer persona detallado', icon: '👤' },
  { number: 2, name: 'Arquitecto de Buyer\'s Journey', description: 'Mapea el journey completo', icon: '🗺️' },
  { number: 3, name: 'Agente de Ofertas 100M', description: 'Crea oferta irresistible', icon: '💎' },
  { number: 4, name: 'Selector de Canales', description: 'Prioriza canales de marketing', icon: '📡' },
  { number: 5, name: 'Atlas, the AEO Strategist', description: 'Define pilares de contenido', icon: '📚' },
  { number: 6, name: 'Planner, the Content Strategist', description: 'Calendario editorial 90 días', icon: '📅' },
  { number: 7, name: 'Agente de Budgets para Pauta', description: 'Plan de medios y presupuesto', icon: '💰' }
];
```

### chat.types.ts

```typescript
export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  createdAt: string;
}

export interface ChatRequest {
  accountId: string;
  stageNumber: number;
  userMessage: string;
  conversationState?: any;
  previousOutputs?: any;
}

export interface ChatResponse {
  agentMessage: string;
  updatedState: any;
  progress: number;
  isComplete: boolean;
  output?: any;
  metadata?: {
    modelUsed: string;
    provider: string;
    usage: {
      promptTokens: number;
      completionTokens: number;
      totalTokens: number;
    };
  };
}
```

## Context API

### AuthContext

```typescript
// contexts/AuthContext.tsx
import { createContext, useContext, useState, useEffect } from 'react';

interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (credentials: LoginCredentials) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  logout: () => void;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(
    localStorage.getItem('authToken')
  );
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (token) {
      // Validar token y cargar usuario
      validateToken();
    } else {
      setIsLoading(false);
    }
  }, [token]);

  const login = async (credentials: LoginCredentials) => {
    const response = await authService.login(credentials);
    setUser(response.user);
    setToken(response.token);
    localStorage.setItem('authToken', response.token);
  };

  const register = async (data: RegisterData) => {
    const response = await authService.register(data);
    setUser(response.user);
    setToken(response.token);
    localStorage.setItem('authToken', response.token);
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem('authToken');
  };

  return (
    <AuthContext.Provider value={{ user, token, login, register, logout, isLoading }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within AuthProvider');
  return context;
};
```

## Rutas Protegidas

```typescript
// App.tsx
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';

function PrivateRoute({ children }) {
  const { user, isLoading } = useAuth();

  if (isLoading) return <div>Loading...</div>;
  if (!user) return <Navigate to="/login" />;

  return children;
}

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/" element={
            <PrivateRoute>
              <DashboardPage />
            </PrivateRoute>
          } />
          <Route path="/accounts/:accountId" element={
            <PrivateRoute>
              <AccountDetailPage />
            </PrivateRoute>
          } />
          <Route path="/accounts/:accountId/stages/:stageNumber/chat" element={
            <PrivateRoute>
              <ChatPage />
            </PrivateRoute>
          } />
          <Route path="/accounts/:accountId/stages/:stageNumber/output" element={
            <PrivateRoute>
              <OutputPage />
            </PrivateRoute>
          } />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
```

## Servicios API

### api.ts (Axios configurado)

```typescript
import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:3000/api'
});

// Interceptor para agregar token
api.interceptors.request.use(config => {
  const token = localStorage.getItem('authToken');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Interceptor para manejar errores de auth
api.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      localStorage.removeItem('authToken');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;
```

### chat.service.ts

```typescript
import api from './api';

export const chatService = {
  sendMessage: async (request: ChatRequest): Promise<ChatResponse> => {
    const { data } = await api.post('/agents/chat', request);
    return data;
  },

  getConversationHistory: async (stageId: string): Promise<ChatMessage[]> => {
    const { data } = await api.get(`/stages/${stageId}/history`);
    return data;
  }
};
```

## Hooks Personalizados

### useChat.ts

```typescript
import { useState, useEffect } from 'react';
import { chatService } from '../services/chat.service';

export function useChat(accountId: string, stageNumber: number) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [isComplete, setIsComplete] = useState(false);

  const sendMessage = async (userMessage: string) => {
    setIsLoading(true);

    // Agregar mensaje del usuario
    const userMsg: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: userMessage,
      createdAt: new Date().toISOString()
    };
    setMessages(prev => [...prev, userMsg]);

    try {
      const response = await chatService.sendMessage({
        accountId,
        stageNumber,
        userMessage,
        conversationState: {}, // obtener del estado
        previousOutputs: {} // obtener de context
      });

      // Agregar respuesta del agente
      const assistantMsg: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.agentMessage,
        createdAt: new Date().toISOString()
      };
      setMessages(prev => [...prev, assistantMsg]);

      setProgress(response.progress);
      setIsComplete(response.isComplete);

      return response;
    } catch (error) {
      console.error('Error sending message:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  return {
    messages,
    sendMessage,
    isLoading,
    progress,
    isComplete
  };
}
```

## Variables de Entorno

```env
# .env
VITE_API_URL=http://localhost:3000/api
```

## Dependencias (package.json)

```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.20.0",
    "axios": "^1.6.2",
    "react-hook-form": "^7.48.2",
    "zod": "^3.22.4",
    "@radix-ui/react-select": "^2.0.0",
    "@radix-ui/react-dialog": "^1.0.5",
    "tailwindcss": "^3.3.5",
    "lucide-react": "^0.294.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.43",
    "@types/react-dom": "^18.2.17",
    "@vitejs/plugin-react": "^4.2.1",
    "typescript": "^5.3.3",
    "vite": "^5.0.8"
  }
}
```
