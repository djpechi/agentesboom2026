import React from 'react';
import { AlertCircle, AlertTriangle, ShieldCheck, ShieldAlert } from 'lucide-react';

interface Issue {
    type: 'error' | 'warning';
    severity: 'high' | 'medium' | 'low';
    message: string;
    suggestion?: string;
}

interface Suggestion {
    type: 'improvement';
    message: string;
    priority: 'low' | 'medium' | 'high';
}

interface ValidationResult {
    approved: boolean;
    canProceed: boolean;
    qualityScore: number;
    coherenceScore: number;
    overallScore: number;
    issues: Issue[];
    suggestions: Suggestion[];
}

interface ValidationPanelProps {
    validation: ValidationResult;
    onDismiss?: () => void;
}

const ValidationPanel: React.FC<ValidationPanelProps> = ({ validation }) => {
    if (!validation) return null;

    const isApproved = validation.approved;
    const bgColor = isApproved ? 'bg-green-50' : 'bg-red-50';
    const borderColor = isApproved ? 'border-green-200' : 'border-red-200';
    const iconColor = isApproved ? 'text-green-600' : 'text-red-600';

    return (
        <div className={`rounded-xl border ${borderColor} ${bgColor} p-6 mb-8 animate-in fade-in slide-in-from-bottom-4 duration-500`}>
            <div className="flex items-start justify-between">
                <div className="flex items-center gap-4">
                    <div className={`p-3 rounded-full ${isApproved ? 'bg-green-100' : 'bg-red-100'}`}>
                        {isApproved ? (
                            <ShieldCheck className={`w-8 h-8 ${iconColor}`} />
                        ) : (
                            <ShieldAlert className={`w-8 h-8 ${iconColor}`} />
                        )}
                    </div>
                    <div>
                        <h3 className={`text-xl font-bold ${isApproved ? 'text-green-900' : 'text-red-900'}`}>
                            {isApproved ? 'Orchestrator Approved' : 'Orchestrator Review Required'}
                        </h3>
                        <p className={`text-sm ${isApproved ? 'text-green-700' : 'text-red-700'}`}>
                            {isApproved
                                ? 'Great work! The output meets all quality and coherence standards.'
                                : 'Some issues need to be resolved before completing this stage.'}
                        </p>
                    </div>
                </div>

                <div className="flex gap-4 text-right">
                    <div>
                        <div className="text-xs uppercase text-slate-500 font-bold mb-1">Quality</div>
                        <div className="text-2xl font-bold text-slate-700">{validation.qualityScore.toFixed(1)}<span className="text-sm text-slate-400">/10</span></div>
                    </div>
                    <div>
                        <div className="text-xs uppercase text-slate-500 font-bold mb-1">Coherence</div>
                        <div className="text-2xl font-bold text-slate-700">{validation.coherenceScore.toFixed(1)}<span className="text-sm text-slate-400">/10</span></div>
                    </div>
                </div>
            </div>

            {(validation.issues.length > 0 || validation.suggestions.length > 0) && (
                <div className="mt-6 space-y-4">
                    {validation.issues.map((issue, idx) => (
                        <div key={`issue-${idx}`} className="bg-white/60 p-4 rounded-lg border border-slate-200/50">
                            <div className="flex gap-3">
                                {issue.type === 'error' ? (
                                    <AlertCircle className="w-5 h-5 text-red-500 shrink-0 mt-0.5" />
                                ) : (
                                    <AlertTriangle className="w-5 h-5 text-amber-500 shrink-0 mt-0.5" />
                                )}
                                <div>
                                    <div className="font-semibold text-slate-800 flex items-center gap-2">
                                        {issue.message}
                                        {issue.severity === 'high' && (
                                            <span className="text-[10px] bg-red-100 text-red-600 px-2 py-0.5 rounded-full uppercase tracking-wider">Critical</span>
                                        )}
                                    </div>
                                    {issue.suggestion && (
                                        <div className="text-primary text-sm mt-1 font-medium">Suggestion: {issue.suggestion}</div>
                                    )}
                                </div>
                            </div>
                        </div>
                    ))}

                    {validation.suggestions.map((sug, idx) => (
                        <div key={`sug-${idx}`} className="bg-blue-50/50 p-4 rounded-lg border border-blue-100/50">
                            <div className="flex gap-3">
                                <div className="w-5 h-5 rounded-full bg-blue-100 flex items-center justify-center shrink-0 mt-0.5 text-blue-600">
                                    <span className="text-xs font-bold">i</span>
                                </div>
                                <div>
                                    <div className="text-slate-700 text-sm">
                                        <span className="font-semibold text-blue-900 mr-2">Optimization:</span>
                                        {sug.message}
                                    </div>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default ValidationPanel;
