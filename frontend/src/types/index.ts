export interface User {
  id: string;
  email: string;
  full_name: string | null;
  created_at: string;
  updated_at: string;
}

export interface Account {
  id: string;
  user_id: string;
  client_name: string;
  company_website: string | null;
  ai_model: string;
  created_at: string;
  updated_at: string;
  stages?: Stage[];
}

export interface Stage {
  id: string;
  account_id: string;
  stage_number: number;
  status: 'locked' | 'in_progress' | 'completed';
  state: Record<string, any>;
  output: Record<string, any> | null;
  ai_model_used: string | null;
  created_at: string;
  updated_at: string;
  completed_at?: string;
  orchestrator_approved?: boolean;
  orchestrator_score?: number;
  orchestrator_feedback?: {
    issues: any[];
    suggestions: any[];
  };
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  full_name?: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface AccountCreateRequest {
  client_name: string;
  company_website?: string;
  ai_model?: string;
}

export interface ChatMessage {
  role: 'system' | 'user' | 'assistant';
  content: string;
}

export interface ChatRequest {
  message: string;
  state?: Record<string, any>;
}

export interface ChatResponse {
  response: string;
  completed: boolean;
  stage: Stage;
  buttons?: string[];
  confidenceScore?: number;
  progressLabel?: string;
  progressStep?: string;
}

export interface InitialMessageResponse {
  message: string;
  stage_number: number;
  status: string;
  buttons?: string[];
}
