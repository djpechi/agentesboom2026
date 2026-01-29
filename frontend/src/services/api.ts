import axios from 'axios';
import type {
  User,
  Account,
  Stage,
  LoginRequest,
  RegisterRequest,
  TokenResponse,
  AccountCreateRequest,
  ChatRequest,
  ChatResponse,
  InitialMessageResponse,
} from '../types';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests if available
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const authAPI = {
  register: async (data: RegisterRequest): Promise<User> => {
    const response = await api.post('/auth/register', data);
    return response.data;
  },
  login: async (data: LoginRequest): Promise<TokenResponse> => {
    const response = await api.post('/auth/login', data);
    return response.data;
  },
  getCurrentUser: async (): Promise<User> => {
    const response = await api.get('/auth/me');
    return response.data;
  },
};

export const accountsAPI = {
  getAll: async (): Promise<Account[]> => {
    const response = await api.get('/accounts');
    return response.data;
  },
  getById: async (id: string): Promise<Account> => {
    const response = await api.get(`/accounts/${id}`);
    return response.data;
  },
  create: async (data: AccountCreateRequest): Promise<Account> => {
    const response = await api.post('/accounts', data);
    return response.data;
  },
  update: async (id: string, data: Partial<AccountCreateRequest>): Promise<Account> => {
    const response = await api.patch(`/accounts/${id}`, data);
    return response.data;
  },
  delete: async (id: string): Promise<void> => {
    await api.delete(`/accounts/${id}`);
  },
};

export const stagesAPI = {
  getByAccount: async (accountId: string): Promise<Stage[]> => {
    const response = await api.get(`/accounts/${accountId}/stages`);
    return response.data;
  },
  getByNumber: async (accountId: string, stageNumber: number): Promise<Stage> => {
    const response = await api.get(`/accounts/${accountId}/stages/${stageNumber}`);
    return response.data;
  },
  update: async (accountId: string, stageNumber: number, data: Partial<Stage>): Promise<Stage> => {
    const response = await api.patch(`/accounts/${accountId}/stages/${stageNumber}`, data);
    return response.data;
  },
  reset: async (accountId: string, stageNumber: number): Promise<Stage> => {
    const response = await api.post(`/accounts/${accountId}/stages/${stageNumber}/reset`);
    return response.data;
  },
};

export const agentsAPI = {
  getInitialMessage: async (accountId: string, stageNumber: number): Promise<InitialMessageResponse> => {
    const response = await api.get(`/agents/accounts/${accountId}/stages/${stageNumber}/init`);
    return response.data;
  },
  chat: async (accountId: string, stageNumber: number, data: ChatRequest): Promise<ChatResponse> => {
    const response = await api.post(`/agents/accounts/${accountId}/stages/${stageNumber}/chat`, data);
    return response.data;
  },
};

export const exportsAPI = {
  downloadPDF: (accountId: string): string => {
    return `${API_BASE_URL}/exports/accounts/${accountId}/pdf`;
  },
  downloadExcel: (accountId: string): string => {
    return `${API_BASE_URL}/exports/accounts/${accountId}/excel`;
  },
};

export const demoAPI = {
  runAutoChat: async (accountId: string, stageNumber: number): Promise<any> => {
    const response = await api.post(`/demo/accounts/${accountId}/stages/${stageNumber}/run`, {
      profile: "dynamic",
      speed: "normal"
    });
    return response.data;
  },
};

export default api;
