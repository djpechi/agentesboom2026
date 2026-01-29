import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import type { Stage, Account } from '../types';
import Loading from '../components/Loading';
import { ChevronLeft, Send, Sparkles, User, Bot, Loader2, Zap, RotateCcw, FileText } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import Stage1Output from '../components/Stage1Output';
import Stage2Output from '../components/Stage2Output';
import Stage3Output from '../components/Stage3Output';
import AgentThoughtProcess, { type ThoughtStep } from '../components/AgentThoughtProcess';
import ValidationPanel from '../components/ValidationPanel';
import Stage1TableBubble from '../components/Stage1TableBubble';
import Modal from '../components/Modal';
import { agentsAPI, stagesAPI, accountsAPI } from '../services/api';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  buttons?: string[];
  confidenceScore?: number;
  progressLabel?: string;
  progressStep?: string;
  output?: any;
}

const STAGE_NAMES = [
  'Booms - Buyer Persona Architect',
  'Journey - Customer Journey Mapping',
  'Ofertas 100M',
  'Selector de Canales',
  'Atlas - AEO Strategist',
  'Planner - Content Strategist',
  'Agente de Budgets',
];

const StageChat: React.FC = () => {
  const { accountId, stageNumber } = useParams<{ accountId: string; stageNumber: string }>();
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [sending, setSending] = useState(false);
  const [stage, setStage] = useState<Stage | null>(null);
  const [account, setAccount] = useState<Account | null>(null);
  const [loading, setLoading] = useState(true);
  const [isAutoChatting, setIsAutoChatting] = useState(false);
  const [isResetModalOpen, setIsResetModalOpen] = useState(false);

  // Thought Process State
  const [thoughtSteps, setThoughtSteps] = useState<ThoughtStep[]>([]);
  const [modelName, setModelName] = useState('GPT-4o');

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const navigate = useNavigate();

  useEffect(() => {
    loadStage();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [accountId, stageNumber]);

  // View Mode State
  const [viewMode, setViewMode] = useState<'chat' | 'deliverables'>('chat');

  useEffect(() => {
    // Optional: Auto-switch to deliverables if stage is loaded and completed?
    // Let's stick to 'chat' default but let the user switch easily.
  }, [stage]);

  const loadStage = async () => {
    if (!accountId || !stageNumber) return;

    try {
      const [stageData, accountData] = await Promise.all([
        stagesAPI.getByNumber(accountId, parseInt(stageNumber)),
        accountsAPI.getById(accountId)
      ]);
      setStage(stageData);
      setAccount(accountData);

      const history: Message[] = stageData.state?.messages || [];

      if (history.length === 0) {
        const initialData = await agentsAPI.getInitialMessage(accountId, parseInt(stageNumber));
        setMessages([{
          role: 'assistant',
          content: initialData.message,
          buttons: initialData.buttons
        }]);
      } else {
        setMessages(history);
      }
    } catch (error) {
      console.error('Error loading stage:', error);
    } finally {
      setLoading(false);
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleNextStage = () => {
    if (stageNumber) {
      const nextStage = parseInt(stageNumber) + 1;
      navigate(`/accounts/${accountId}/stages/${nextStage}`);
    }
  };

  const simulateThinking = (stageNum: number) => {
    // Use account's selected model or default
    const currentModel = account?.ai_model || 'GPT-4o';

    // For search-heavy stages (Stage 2 Journey, Stage 4 Channels), we might use a different tool
    // but the BRAIN is still the selected model. 
    // We can display "Model + Tool" if needed, but for now let's show the selected model as requested.
    setModelName(currentModel);

    // Create new steps with unique IDs based on timestamp/random
    const baseId = Date.now();
    const isJourney = stageNum === 2;

    const rawSteps = isJourney ? [
      { label: 'Analyzing User Input...', status: 'pending' as const },
      { label: 'Identifying Search Intent', status: 'pending' as const },
      { label: 'Conducting Web Research', details: 'Searching across 20+ sources via Perplexity...', status: 'pending' as const },
      { label: 'Synthesizing Search Results', status: 'pending' as const },
      { label: 'Mapping Journey Stage', status: 'pending' as const },
    ] : [
      { label: 'Analyzing User Input...', status: 'pending' as const },
      { label: 'Retrieving Business Context', status: 'pending' as const },
      { label: 'Querying Knowledge Base', details: 'Consulting "Scaling Up" methodology...', status: 'pending' as const },
      { label: 'Evaluating Concepts', details: 'Checking Green/SuperGreen criteria...', status: 'pending' as const },
      { label: 'Formulating Response', status: 'pending' as const },
    ];

    const newSessionSteps: ThoughtStep[] = rawSteps.map((s, i) => ({
      id: `${baseId}-${i}`,
      label: s.label,
      status: s.status,
      details: s.details
    }));

    // Add separator if history exists
    setThoughtSteps(prev => {
      if (prev.length > 0) {
        const separator: ThoughtStep = {
          id: `sep-${baseId}`,
          label: '--- New Message ---',
          status: 'completed',
          details: new Date().toLocaleTimeString()
        };
        return [...prev, separator, ...newSessionSteps];
      }
      return newSessionSteps;
    });

    let currentStepIndex = 0; // Index relative to the new batch

    // Activate first step of new batch
    setThoughtSteps(prev => {
      const updated = [...prev];
      // Find the index of the first new step in the full array
      // It's basically the last N items where N is newSessionSteps.length
      const startIndex = updated.length - newSessionSteps.length;
      if (startIndex >= 0) {
        updated[startIndex] = {
          ...updated[startIndex],
          status: 'active',
          timestamp: new Date().toLocaleTimeString()
        };
      }
      return updated;
    });

    const interval = setInterval(() => {
      currentStepIndex++;

      if (currentStepIndex >= newSessionSteps.length) {
        clearInterval(interval);
        return;
      }

      setThoughtSteps(prev => {
        const updated = [...prev];
        const startIndex = updated.length - newSessionSteps.length;

        // Safety check
        if (startIndex < 0) return prev;

        const actualCurrentIndex = startIndex + currentStepIndex;
        const actualPrevIndex = actualCurrentIndex - 1;

        // Complete previous
        if (actualPrevIndex >= startIndex) {
          updated[actualPrevIndex] = { ...updated[actualPrevIndex], status: 'completed' };
        }

        // Activate current
        updated[actualCurrentIndex] = {
          ...updated[actualCurrentIndex],
          status: 'active',
          timestamp: new Date().toLocaleTimeString()
        };

        return updated;
      });

    }, 1500);

    return interval;
  };

  const handleSend = async (messageText?: string) => {
    const textToSend = messageText || input.trim();
    if (!textToSend || !accountId || !stageNumber || sending) return;

    if (!messageText) setInput('');
    setSending(true);

    // Start simulation
    const thinkingInterval = simulateThinking(parseInt(stageNumber));

    const newMessages: Message[] = [...messages, { role: 'user', content: textToSend }];
    setMessages(newMessages);

    try {
      const response = await agentsAPI.chat(accountId, parseInt(stageNumber), {
        message: textToSend,
        state: { messages: newMessages },
      });

      clearInterval(thinkingInterval);

      // Complete active steps immediately
      setThoughtSteps(prev => prev.map(s =>
        s.status !== 'completed' ? { ...s, status: 'completed' as const } : s
      ));

      setMessages([...newMessages, {
        role: 'assistant',
        content: response.response,
        buttons: response.buttons,
        confidenceScore: response.confidenceScore,
        progressLabel: response.progressLabel,
        progressStep: response.progressStep,
        output: response.completed ? response.stage?.output : undefined
      }]);
      setStage(response.stage);

    } catch (error: any) {
      console.error('Error sending message:', error);
      clearInterval(thinkingInterval);
      setMessages([...newMessages, {
        role: 'assistant',
        content: 'Error: ' + (error.response?.data?.detail || 'Failed to send message')
      }]);
    } finally {
      setSending(false);
    }
  };

  const runAutoChat = async () => {
    if (!accountId || !stageNumber || isAutoChatting) return;

    setIsAutoChatting(true);
    setLoading(true);

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`http://localhost:8000/demo/accounts/${accountId}/stages/${stageNumber}/run`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { 'Authorization': `Bearer ${token}` } : {})
        },
        body: JSON.stringify({
          profile: "dynamic",
          speed: "fast"
        })
      });

      if (!response.body) throw new Error('No response body');

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n\n');
        buffer = lines.pop() || ''; // Keep incomplete expected line in buffer

        for (const line of lines) {
          if (!line.trim()) continue;

          try {
            // Remove 'data: ' prefix if present (standard SSE)
            const data = JSON.parse(line.replace(/^data: /, ''));

            if (data.error) {
              console.error('Stream error:', data.error);
              continue;
            }

            if (data.type === 'user_message') {
              setMessages(prev => [...prev, { role: 'user', content: data.content }]);
              await scrollToBottom();

              // Trigger thinking simulation for the UPCOMING agent response
              simulateThinking(parseInt(stageNumber));
            }
            else if (data.type === 'agent_message') {
              // Stop thinking simulation
              setThoughtSteps(prev => prev.map(s =>
                s.status !== 'completed' ? { ...s, status: 'completed' as const } : s
              ));

              setMessages(prev => [...prev, {
                role: 'assistant',
                content: data.content,
                buttons: data.buttons,
                confidenceScore: data.confidenceScore,
                progressLabel: data.progressLabel,
                progressStep: data.progressStep,
                output: data.isComplete ? data.output : undefined
              }]);
              await scrollToBottom();
            }
            else if (data.type === 'complete') {
              await loadStage(); // Refresh stage data to get final state
            }
          } catch (e) {
            console.warn('Error parsing stream chunk:', line, e);
          }
        }
      }

    } catch (error) {
      console.error('Auto-chat failed:', error);
      alert('Auto-chat failed. Check console for details.');
    } finally {
      setIsAutoChatting(false);
      setLoading(false);
      // Ensure thinking is stopped
      setThoughtSteps(prev => prev.map(s => ({ ...s, status: 'completed' as const })));
    }
  };

  const handleResetClick = () => {
    setIsResetModalOpen(true);
  };

  const confirmReset = async () => {
    if (!accountId || !stageNumber) return;

    setLoading(true);
    try {
      const resetStage = await stagesAPI.reset(accountId, parseInt(stageNumber));
      setStage(resetStage);
      setMessages([]);
      setViewMode('chat'); // Reset view to chat

      // Reload initial message
      const initialData = await agentsAPI.getInitialMessage(accountId, parseInt(stageNumber));
      setMessages([{
        role: 'assistant',
        content: initialData.message,
        buttons: initialData.buttons
      }]);
      setThoughtSteps([]);
    } catch (error) {
      console.error('Error resetting stage:', error);
      alert('Failed to reset stage');
    } finally {
      setLoading(false);
    }
  };

  if (loading && !isAutoChatting) return <Loading />;
  if (!stage) return <div className="p-8 text-center text-muted-foreground">Stage not found</div>;

  const showRightPanel = (sending || thoughtSteps.length > 0) || (stage?.status === 'completed' && !!stage?.output);

  return (
    <div className="flex flex-col h-screen bg-[#F8FAFC]">
      {/* Header */}
      <header className="glass sticky top-0 z-10 px-6 py-4 flex justify-between items-center shadow-sm">
        <div className="flex items-center gap-4">
          <button
            onClick={() => navigate(`/accounts/${accountId}`)}
            className="p-2 hover:bg-slate-100 rounded-full transition-colors"
          >
            <ChevronLeft className="w-5 h-5" />
          </button>
          <div className="flex flex-col">
            <h1 className="text-xl font-heading font-bold bg-clip-text text-transparent bg-gradient-to-r from-primary to-orange-400">
              Stage {stageNumber}: {STAGE_NAMES[parseInt(stageNumber || '1') - 1]}
            </h1>
            <p className="text-xs text-muted-foreground font-medium uppercase tracking-wider">
              {stage.status.replace('_', ' ')}
            </p>
          </div>
        </div>

        {/* View Switcher (Only visible when completed) */}
        {stage.status === 'completed' && (
          <div className="absolute left-1/2 transform -translate-x-1/2 bg-slate-100 p-1 rounded-xl flex shadow-inner">
            <button
              onClick={() => setViewMode('chat')}
              className={`px-4 py-1.5 rounded-lg text-sm font-bold transition-all ${viewMode === 'chat'
                ? 'bg-white text-slate-900 shadow-sm'
                : 'text-slate-500 hover:text-slate-700'
                }`}
            >
              Chat & Context
            </button>
            <button
              onClick={() => setViewMode('deliverables')}
              className={`px-4 py-1.5 rounded-lg text-sm font-bold transition-all ${viewMode === 'deliverables'
                ? 'bg-white text-primary shadow-sm'
                : 'text-slate-500 hover:text-slate-700'
                }`}
            >
              <span className="flex items-center gap-2">
                <FileText className="w-4 h-4" />
                Deliverables
              </span>
            </button>
          </div>
        )}

        <div className="flex flex-col items-end gap-2">
          <div className="flex gap-3">
            {stage.status !== 'completed' && !isAutoChatting && (
              <button
                onClick={runAutoChat}
                className="flex items-center gap-2 px-4 py-2 bg-amber-500 hover:bg-amber-600 text-white rounded-full text-sm font-semibold transition-all btn-premium shadow-amber-200"
              >
                <Zap className="w-4 h-4 fill-current" />
                Auto-Chat
              </button>
            )}
            <span className={`px-4 py-2 rounded-full text-sm font-bold ${stage.status === 'completed' ? 'bg-green-100 text-green-700' : 'bg-primary/10 text-primary'
              }`}>
              {stage.status.toUpperCase()}
            </span>
            <button
              onClick={handleResetClick}
              className="flex items-center gap-2 px-3 py-1.5 hover:bg-red-50 text-slate-400 hover:text-red-600 rounded-lg transition-all text-xs font-bold border border-transparent hover:border-red-100"
              title="Reset Stage and Clear History"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              Reset
            </button>
          </div>
          {stage.status !== 'completed' && (stage.state?.progress !== undefined || (messages.length > 0 && messages[messages.length - 1]?.progressLabel)) && (
            <div className="w-64 text-right">
              <div className="flex justify-between items-center mb-1">
                <span className="text-[10px] font-bold text-muted-foreground">
                  {messages.length > 0 && messages[messages.length - 1]?.progressLabel?.split(']')[0].replace('[', '') || 'PROGRESS'}
                </span>
                <span className="text-[10px] font-bold text-primary">
                  {messages.length > 0 && messages[messages.length - 1]?.progressStep || `${Math.round(stage.state.progress || 0)}%`}
                </span>
              </div>
              <div className="w-full bg-secondary rounded-full h-1.5 overflow-hidden">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${messages.length > 0 && messages[messages.length - 1]?.progressLabel ? (messages[messages.length - 1]?.progressLabel?.match(/\d+/) || [stage.state.progress])[0] : stage.state.progress}%` }}
                  className="bg-primary h-full rounded-full"
                />
              </div>
            </div>
          )}
        </div>
      </header >

      {/* Main Content Area */}
      {viewMode === 'chat' ? (
        <div className="flex flex-1 overflow-hidden">
          {/* Left Column: Chat */}
          <div className="flex flex-col flex-1">
            {/* Messages */}
            <main className="flex-1 overflow-y-auto p-6 space-y-6">
              <div className="max-w-4xl mx-auto space-y-6">
                <AnimatePresence initial={false}>
                  {messages.map((msg, idx) => (
                    <motion.div
                      key={idx}
                      initial={{ opacity: 0, y: 10, scale: 0.95 }}
                      animate={{ opacity: 1, y: 0, scale: 1 }}
                      className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                      <div className={`flex gap-3 max-w-[85%] ${msg.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
                        <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 shadow-sm ${msg.role === 'user' ? 'bg-primary text-white' : 'bg-card border text-primary'
                          }`}>
                          {msg.role === 'user' ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
                        </div>
                        <div className={`p-4 rounded-2xl shadow-sm text-sm leading-relaxed ${msg.role === 'user'
                          ? 'bg-primary text-white rounded-tr-none'
                          : 'bg-card border text-foreground rounded-tl-none'
                          }`}>
                          {(() => {
                            try {
                              const content = msg.content.trim();
                              // Handle potential markdown JSON blocks
                              let jsonStr = content;
                              if (content.includes('```json')) {
                                jsonStr = content.split('```json')[1].split('```')[0].trim();
                              } else if (content.startsWith('{')) {
                                jsonStr = content;
                              } else {
                                return msg.content;
                              }

                              const parsed = JSON.parse(jsonStr);
                              // Fallback if agentMessage is present, otherwise stringify or show content
                              return parsed.agentMessage || msg.content;
                            } catch (e) {
                              return msg.content;
                            }
                          })()}

                          {msg.confidenceScore !== undefined && (
                            <div className="mt-3 pt-3 border-t border-primary/10 flex items-center justify-between">
                              <span className="text-[10px] font-bold uppercase tracking-wider opacity-60">Confidence Score</span>
                              <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${msg.confidenceScore > 80 ? 'bg-green-100 text-green-700' : 'bg-orange-100 text-orange-700'}`}>
                                {msg.confidenceScore}%
                              </span>
                            </div>
                          )}

                          {msg.buttons && msg.buttons.length > 0 && (
                            <div className="mt-4 flex flex-wrap gap-2">
                              {msg.buttons.map((btn, bIdx) => (
                                <button
                                  key={bIdx}
                                  onClick={() => handleSend(btn)}
                                  disabled={sending || isAutoChatting}
                                  className="px-3 py-1.5 bg-primary/10 hover:bg-primary/20 text-primary border border-primary/20 rounded-lg text-xs font-bold transition-all"
                                >
                                  {btn}
                                </button>
                              ))}
                            </div>
                          )}

                          {/* Render Stage 1 Table Bubble if present */}
                          {msg.output?.scalingUpTable && (
                            <Stage1TableBubble data={msg.output} />
                          )}
                        </div>
                      </div>
                    </motion.div>
                  ))}
                </AnimatePresence>

                {(sending || isAutoChatting) && (
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="flex justify-start"
                  >
                    <div className="flex gap-3 items-center text-muted-foreground text-xs font-medium">
                      <div className="w-8 h-8 rounded-full bg-slate-100 flex items-center justify-center animate-pulse">
                        <Bot className="w-4 h-4" />
                      </div>
                      {isAutoChatting ? 'Running Auto-Chat demo...' : 'AI is thinking...'}
                      <Loader2 className="w-3 h-3 animate-spin" />
                    </div>
                  </motion.div>
                )}

                {stage?.orchestrator_feedback && (
                  <ValidationPanel
                    validation={{
                      approved: stage.orchestrator_approved ?? false,
                      canProceed: stage.status === 'completed', // Simplified derived state
                      qualityScore: stage.orchestrator_score ?? 0,
                      coherenceScore: stage.orchestrator_score ?? 0, // Mock if missing separate score
                      overallScore: stage.orchestrator_score ?? 0,
                      issues: stage.orchestrator_feedback.issues || [],
                      suggestions: stage.orchestrator_feedback.suggestions || []
                    }}
                  />
                )}

                <div ref={messagesEndRef} />
              </div>
            </main>

            {/* Input Area */}
            <footer className="p-6 bg-white border-t border-slate-100">
              <div className="max-w-4xl mx-auto">
                {stage?.status === 'completed' ? (
                  <div className="text-center p-4 bg-green-50 rounded-xl border border-green-100">
                    <Sparkles className="w-6 h-6 text-green-600 mx-auto mb-2" />
                    <p className="text-green-800 font-semibold mb-3">Stage Completed Successfully!</p>
                    <div className="flex gap-3 justify-center">
                      <button
                        onClick={handleResetClick}
                        className="px-4 py-2 bg-white text-slate-600 border border-slate-200 hover:bg-red-50 hover:text-red-600 hover:border-red-100 rounded-lg text-sm font-bold transition-all flex items-center gap-2"
                      >
                        <RotateCcw className="w-4 h-4" />
                        Retry
                      </button>
                      <button
                        onClick={() => setViewMode('deliverables')}
                        className="px-6 py-2 bg-primary text-white rounded-lg text-sm font-bold hover:bg-primary/90 transition-colors shadow-sm flex items-center gap-2"
                      >
                        <FileText className="w-4 h-4" />
                        View Deliverables
                      </button>
                    </div>
                  </div>
                ) : (
                  <form
                    onSubmit={(e) => {
                      e.preventDefault();
                      handleSend(input);
                    }}
                    className="relative group"
                  >
                    <input
                      type="text"
                      value={input}
                      onChange={(e) => setInput(e.target.value)}
                      disabled={sending || isAutoChatting}
                      placeholder={isAutoChatting ? "Agent running..." : "Type your message..."}
                      className="w-full pl-6 pr-14 py-4 bg-secondary/50 border-border border rounded-2xl focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none transition-all"
                    />
                    <button
                      type="submit"
                      disabled={sending || !input.trim() || isAutoChatting}
                      className="absolute right-2 top-2 p-3 bg-primary text-white rounded-xl disabled:opacity-50 disabled:cursor-not-allowed hover:bg-primary/90 transition-all shadow-lg shadow-primary/20"
                    >
                      {sending ? <Loader2 className="w-5 h-5 animate-spin" /> : <Send className="w-5 h-5" />}
                    </button>
                  </form>
                )}
                <p className="text-[10px] text-center text-muted-foreground mt-4 uppercase tracking-tighter">
                  Powered by Booms Platform AI • Agentes 1-7 Sequential Flow
                </p>
              </div>
            </footer>
          </div>

          {/* Right Column: Output / Artifacts / Thought Process */}
          <div className={`
              hidden lg:block
              transition-all duration-500 ease-in-out border-l border-slate-100 bg-slate-50
              ${showRightPanel ? 'w-[35%] opacity-100 translate-x-0' : 'w-0 opacity-0 translate-x-20 overflow-hidden'}
            `}>
            {/* Prioritize Output if Stage is Completed */}
            {stage?.status === 'completed' && stage?.output ? (
              <div className="h-full overflow-y-auto p-6 scrollbar-thin">
                {/* Specialized Outputs per Stage - currently only Stage 1 implemented visually */}
                {parseInt(stageNumber || '0') === 1 ? (
                  <Stage1Output data={stage.output as any} clientName={account?.client_name || 'Client'} accountId={accountId} />
                ) : parseInt(stageNumber || '0') === 2 ? (
                  <Stage2Output data={stage.output as any} clientName={account?.client_name || 'Client'} />
                ) : parseInt(stageNumber || '0') === 3 ? (
                  <Stage3Output data={stage.output as any} clientName={account?.client_name || 'Client'} />
                ) : (
                  <div className="p-4 bg-white rounded-xl border border-slate-200 shadow-sm">
                    <h3 className="font-bold text-lg mb-2">Stage Output</h3>
                    <pre className="text-xs bg-slate-50 p-4 rounded-lg overflow-x-auto">
                      {JSON.stringify(stage.output, null, 2)}
                    </pre>
                  </div>
                )}
              </div>
            ) : (sending || thoughtSteps.length > 0) ? (
              <AgentThoughtProcess
                steps={thoughtSteps}
                modelName={modelName}
                isThinking={sending}
                agentName={STAGE_NAMES[parseInt(stageNumber || '1') - 1]}
              />
            ) : null}
          </div>
        </div>
      ) : (
        /* Deliverables View (Full Width) */
        <div className="flex-1 overflow-y-auto bg-slate-50/50 p-8">
          <div className="max-w-7xl mx-auto animate-in fade-in duration-500">
            <div className="mb-6 flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-heading font-bold text-slate-900">Stage Deliverables</h2>
                <p className="text-slate-500">Review and download the finalized assets for this stage.</p>
              </div>
            </div>

            {stage?.output && (
              parseInt(stageNumber || '0') === 1 ? (
                <Stage1Output
                  data={stage.output as any}
                  clientName={account?.client_name || 'Client'}
                  accountId={accountId}
                  onBackToChat={() => setViewMode('chat')}
                  onNextStage={handleNextStage}
                />
              ) : parseInt(stageNumber || '0') === 2 ? (
                <Stage2Output data={stage.output as any} clientName={account?.client_name || 'Client'} />
              ) : parseInt(stageNumber || '0') === 3 ? (
                <Stage3Output data={stage.output as any} clientName={account?.client_name || 'Client'} />
              ) : (
                <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-8">
                  <pre>{JSON.stringify(stage.output, null, 2)}</pre>
                </div>
              )
            )}
          </div>
        </div>
      )}

      {/* Reset Confirmation Modal */}
      <Modal
        isOpen={isResetModalOpen}
        onClose={() => setIsResetModalOpen(false)}
        onConfirm={confirmReset}
        title="Reset Stage?"
        description="This will permanently delete the current conversation history and any generated outputs. This action cannot be undone."
        confirmText="Yes, Reset"
        cancelText="Cancel"
        isDestructive={true}
      />
    </div>
  );
};

export default StageChat;
