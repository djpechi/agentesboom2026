import React from 'react';
import { CheckCircle2, Clock, Loader2, Cpu, BrainCircuit } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

export interface ThoughtStep {
    id: string;
    label: string;
    status: 'pending' | 'active' | 'completed';
    timestamp?: string;
    details?: string;
}

interface AgentThoughtProcessProps {
    steps: ThoughtStep[];
    modelName: string;
    isThinking: boolean;
    agentName: string;
}

const AgentThoughtProcess: React.FC<AgentThoughtProcessProps> = ({
    steps,
    modelName,
    isThinking,
    agentName
}) => {
    return (
        <div className="flex flex-col h-full bg-white border-l border-slate-100 shadow-xl shadow-slate-200/50">
            {/* Header */}
            <div className="p-5 border-b border-slate-100 flex justify-between items-center bg-slate-50/50">
                <div className="flex items-center gap-2">
                    <BrainCircuit className="w-5 h-5 text-primary" />
                    <h3 className="font-heading font-bold text-slate-800">Agent Thought Process</h3>
                </div>
                {isThinking && <Loader2 className="w-4 h-4 animate-spin text-primary" />}
            </div>

            {/* Model Info */}
            <div className="p-5 bg-slate-50 border-b border-slate-100">
                <div className="flex items-center gap-3 mb-2">
                    <div className="w-10 h-10 rounded-xl bg-white border border-slate-100 flex items-center justify-center shadow-sm">
                        <Cpu className="w-5 h-5 text-indigo-500" />
                    </div>
                    <div>
                        <p className="text-xs font-bold text-muted-foreground uppercase tracking-wider">Active Model</p>
                        <p className="text-sm font-bold text-slate-800">{modelName}</p>
                    </div>
                </div>
                <div className="flex justify-between items-center mt-3">
                    <span className="px-2 py-0.5 bg-indigo-50 text-indigo-600 rounded text-[10px] font-bold border border-indigo-100">
                        {agentName}
                    </span>
                    {isThinking ? (
                        <span className="text-[10px] font-bold text-primary animate-pulse flex items-center gap-1">
                            <span className="w-1.5 h-1.5 rounded-full bg-current"></span>
                            PROCESSING
                        </span>
                    ) : (
                        <span className="text-[10px] font-bold text-green-600 flex items-center gap-1">
                            <CheckCircle2 className="w-3 h-3" />
                            IDLE
                        </span>
                    )}
                </div>
            </div>

            {/* Steps List */}
            <div className="flex-1 overflow-y-auto p-5 scrollbar-thin">
                <div className="relative pl-4 border-l-2 border-slate-100 space-y-8">
                    <AnimatePresence>
                        {steps.map((step, idx) => (
                            <motion.div
                                key={step.id}
                                initial={{ opacity: 0, x: -10 }}
                                animate={{ opacity: 1, x: 0 }}
                                transition={{ delay: idx * 0.1 }}
                                className="relative"
                            >
                                {/* Status Dot */}
                                <div className={`
                            absolute -left-[21px] top-1 w-3 h-3 rounded-full border-2 
                            ${step.status === 'completed' ? 'bg-green-500 border-green-500' :
                                        step.status === 'active' ? 'bg-primary border-primary animate-pulse' :
                                            'bg-white border-slate-300'}
                        `}>
                                    {step.status === 'completed' && <CheckCircle2 className="w-full h-full text-white p-[1px]" />}
                                </div>

                                <div className={`transition-all duration-300 ${step.status === 'pending' ? 'opacity-50' : 'opacity-100'}`}>
                                    <h4 className={`text-sm font-bold mb-1 ${step.status === 'active' ? 'text-primary' : 'text-slate-800'}`}>
                                        {step.label}
                                    </h4>
                                    {step.details && step.status !== 'pending' && (
                                        <p className="text-xs text-slate-500 leading-relaxed mb-2">
                                            {step.details}
                                        </p>
                                    )}
                                    <div className="flex items-center gap-2">
                                        {step.timestamp && (
                                            <span className="text-[10px] text-slate-400 flex items-center gap-1">
                                                <Clock className="w-3 h-3" />
                                                {step.timestamp}
                                            </span>
                                        )}
                                        {step.status === 'active' && (
                                            <span className="text-[10px] text-primary font-medium">
                                                Working...
                                            </span>
                                        )}
                                    </div>
                                </div>
                            </motion.div>
                        ))}
                    </AnimatePresence>
                </div>
            </div>

            {/* Footer Info */}
            <div className="p-4 bg-slate-50 border-t border-slate-100 text-center">
                <p className="text-[10px] text-slate-400">
                    AI reasoning allows for more accurate and context-aware responses.
                </p>
            </div>
        </div>
    );
};

export default AgentThoughtProcess;
