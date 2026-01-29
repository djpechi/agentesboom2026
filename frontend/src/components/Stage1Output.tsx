import React, { useState } from 'react';

import { FileText, Download, CheckCircle, TrendingUp, Loader2, ArrowRight, MessageSquare, Database, Server } from 'lucide-react';

interface Stage1OutputProps {
    data: {
        buyerPersona: {
            narrative: string;
            demographics?: any;
        };
        scalingUpTable: {
            criteria: Array<{
                name: string;
                superGreen: string;
                green: string;
                yellow: string;
                red: string;
                notEligible: string;
            }>;
        };
    };
    clientName: string;
    accountId?: string;
    onBackToChat?: () => void;
    onNextStage?: () => void;
}

const Stage1Output: React.FC<Stage1OutputProps> = ({ data, clientName, accountId, onBackToChat, onNextStage }) => {
    const [downloading, setDownloading] = useState<'pdf' | 'excel' | null>(null);

    if (!data) return <div className="p-6 text-center text-slate-400">No output data available</div>;

    // Safe accessors
    const narrative = data.buyerPersona?.narrative || (typeof data.buyerPersona === 'string' ? data.buyerPersona : JSON.stringify(data.buyerPersona || "No narrative generated"));
    const tableCriteria = data.scalingUpTable?.criteria || [];

    const handleDownload = async (type: 'pdf' | 'excel') => {
        if (!accountId) return;
        setDownloading(type);
        try {
            const token = localStorage.getItem('token');
            const response = await fetch(`http://localhost:8000/exports/accounts/${accountId}/${type}`, {
                headers: {
                    ...(token ? { 'Authorization': `Bearer ${token}` } : {})
                }
            });

            if (!response.ok) throw new Error('Download failed');

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `${clientName}_BuyerPersona.${type === 'pdf' ? 'pdf' : 'xlsx'}`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        } catch (error) {
            console.error(`Error downloading ${type}:`, error);
            alert(`Failed to download ${type.toUpperCase()}`);
        } finally {
            setDownloading(null);
        }
    };

    return (
        <div className="space-y-8 animate-in fade-in duration-700">


            {/* 1. Encabezado de Resultados */}
            <div className="bg-white rounded-3xl p-8 border border-slate-100 shadow-xl shadow-slate-200/50">
                <div className="flex justify-between items-start mb-6">
                    <div>
                        <span className="bg-orange-100 text-orange-700 px-3 py-1 rounded-full text-xs font-bold tracking-wider uppercase mb-2 inline-block">
                            Stage 1 Completed
                        </span>
                        <h2 className="text-3xl font-heading font-extrabold text-slate-900">
                            Buyer Persona Profile
                        </h2>
                        <p className="text-slate-500 font-medium mt-1">
                            {clientName}_BuyerPersona
                        </p>
                    </div>
                    {accountId && (
                        <div className="flex gap-2">
                            <button
                                onClick={() => handleDownload('pdf')}
                                disabled={!!downloading}
                                className="flex items-center gap-2 px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl text-sm font-bold transition-colors disabled:opacity-50"
                            >
                                {downloading === 'pdf' ? <Loader2 className="w-4 h-4 animate-spin" /> : <Download className="w-4 h-4" />}
                                PDF
                            </button>
                            <button
                                onClick={() => handleDownload('excel')}
                                disabled={!!downloading}
                                className="flex items-center gap-2 px-4 py-2 bg-green-100 hover:bg-green-200 text-green-700 rounded-xl text-sm font-bold transition-colors disabled:opacity-50"
                            >
                                {downloading === 'excel' ? <Loader2 className="w-4 h-4 animate-spin" /> : <FileText className="w-4 h-4" />}
                                Excel
                            </button>
                        </div>
                    )}
                </div>

                {/* 2. Narrativa Humanizada */}
                <div className="bg-slate-50/50 rounded-2xl p-6 border border-slate-100">
                    <h3 className="text-lg font-bold text-slate-800 mb-4 flex items-center gap-2">
                        <span className="w-8 h-8 rounded-lg bg-orange-500 text-white flex items-center justify-center">
                            <CheckCircle className="w-5 h-5" />
                        </span>
                        Narrativa Humanizada
                    </h3>
                    <div className="prose prose-slate max-w-none text-slate-600 leading-relaxed whitespace-pre-line">
                        {narrative}
                    </div>
                </div>
            </div>

            {/* 3. Tabla Scaling Up */}
            {tableCriteria.length > 0 ? (
                <div className="bg-white rounded-3xl p-8 border border-slate-100 shadow-xl shadow-slate-200/50 overflow-hidden">
                    <h3 className="text-xl font-bold text-slate-900 mb-6 flex items-center gap-2">
                        <TrendingUp className="w-6 h-6 text-green-600" />
                        Tabla Scaling Up
                    </h3>

                    <div className="overflow-x-auto">
                        <table className="w-full text-sm text-left">
                            <thead>
                                <tr className="text-xs font-bold uppercase tracking-wider text-white">
                                    <th className="px-6 py-4 bg-slate-800 rounded-l-xl w-1/6">Criterio</th>
                                    <th className="px-6 py-4 bg-green-600 w-1/6">Super Green (1.0)</th>
                                    <th className="px-6 py-4 bg-emerald-500 w-1/6">Green (0.8)</th>
                                    <th className="px-6 py-4 bg-yellow-400 text-yellow-900 w-1/6">Yellow (0.6)</th>
                                    <th className="px-6 py-4 bg-red-500 w-1/6">Red (0.3)</th>
                                    <th className="px-6 py-4 bg-slate-900 rounded-r-xl w-1/6">Not Eligible</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-slate-100">
                                {tableCriteria.map((row, idx) => (
                                    <tr key={idx} className="hover:bg-slate-50 transition-colors">
                                        <td className="px-6 py-4 font-bold text-slate-700 bg-slate-50 border-r border-slate-100">
                                            {row.name}
                                        </td>
                                        <td className="px-6 py-4 text-slate-600 border-r border-slate-100 bg-green-50/30">
                                            {row.superGreen}
                                        </td>
                                        <td className="px-6 py-4 text-slate-600 border-r border-slate-100 bg-emerald-50/30">
                                            {row.green}
                                        </td>
                                        <td className="px-6 py-4 text-slate-600 border-r border-slate-100 bg-yellow-50/30">
                                            {row.yellow}
                                        </td>
                                        <td className="px-6 py-4 text-slate-600 border-r border-slate-100 bg-red-50/30">
                                            {row.red}
                                        </td>
                                        <td className="px-6 py-4 text-slate-400 bg-slate-100/50 italic">
                                            {row.notEligible}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            ) : (
                <div className="bg-yellow-50 rounded-xl p-6 border border-yellow-100">
                    <h3 className="text-lg font-bold text-yellow-800 mb-2">Tabla de Datos No Generada</h3>
                    <p className="text-sm text-yellow-700 mb-4">La IA no generó la tabla estructurada correctamente. Aquí están los datos crudos:</p>
                    <pre className="text-xs bg-white/50 p-4 rounded overflow-auto max-h-60">
                        {JSON.stringify(data, null, 2)}
                    </pre>
                </div>
            )}

            {/* 4. Orchestrator Handover Confirmation */}
            <div className="bg-slate-900 rounded-3xl p-8 text-white relative overflow-hidden">
                <div className="absolute top-0 right-0 p-32 bg-blue-500 rounded-full blur-[100px] opacity-20"></div>

                <div className="relative z-10">
                    <h3 className="text-xl font-bold mb-6 flex items-center gap-3">
                        <Server className="w-6 h-6 text-blue-400" />
                        Orchestrator Agent Handover
                    </h3>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div className="bg-slate-800/50 rounded-xl p-6 border border-slate-700">
                            <h4 className="text-sm font-bold text-slate-400 uppercase tracking-wider mb-4">Data Transferred</h4>
                            <ul className="space-y-3">
                                <li className="flex items-center gap-3 text-slate-300">
                                    <CheckCircle className="w-5 h-5 text-green-400" />
                                    <span>Buyer Persona Narrative</span>
                                </li>
                                <li className="flex items-center gap-3 text-slate-300">
                                    <CheckCircle className="w-5 h-5 text-green-400" />
                                    <span>Core Demographics</span>
                                </li>
                                <li className="flex items-center gap-3 text-slate-300">
                                    <CheckCircle className="w-5 h-5 text-green-400" />
                                    <span>Scaling Up Criteria Table</span>
                                </li>
                            </ul>
                        </div>

                        <div className="bg-slate-800/50 rounded-xl p-6 border border-slate-700">
                            <h4 className="text-sm font-bold text-slate-400 uppercase tracking-wider mb-4">Next Stage Context</h4>
                            <div className="flex items-start gap-4">
                                <div className="bg-blue-500/20 p-3 rounded-lg">
                                    <Database className="w-6 h-6 text-blue-400" />
                                </div>
                                <div>
                                    <p className="text-slate-300 text-sm leading-relaxed">
                                        The Orchestrator has validated this output. The <strong>Journey Agent (Stage 2)</strong> will now inherit these persona details to map the customer journey with high precision.
                                    </p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* 5. Navigation Footer */}
            <div className="flex items-center justify-between pt-8 border-t border-slate-200">
                <button
                    onClick={onBackToChat}
                    className="flex items-center gap-2 px-6 py-3 text-slate-500 hover:text-slate-800 font-medium transition-colors"
                >
                    <MessageSquare className="w-5 h-5" />
                    Return to Chat
                </button>

                <button
                    onClick={onNextStage}
                    className="flex items-center gap-2 px-8 py-4 bg-slate-900 hover:bg-slate-800 text-white rounded-2xl font-bold shadow-lg shadow-slate-900/20 transition-all hover:scale-[1.02] active:scale-[0.98]"
                >
                    Continue to Stage 2
                    <ArrowRight className="w-5 h-5" />
                </button>
            </div>
        </div>
    );
};

export default Stage1Output;
