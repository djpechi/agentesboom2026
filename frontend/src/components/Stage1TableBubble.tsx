import React from 'react';
import { TrendingUp, Download } from 'lucide-react';

interface Stage1TableBubbleProps {
    data: {
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
}

const Stage1TableBubble: React.FC<Stage1TableBubbleProps> = ({ data }) => {
    const tableCriteria = data?.scalingUpTable?.criteria || [];

    if (tableCriteria.length === 0) return null;

    return (
        <div className="mt-4 bg-white rounded-xl overflow-hidden shadow-sm border border-slate-200 font-sans">
            <div className="p-4 border-b border-slate-100 flex justify-between items-center bg-slate-50">
                <div className="flex items-center gap-2">
                    <TrendingUp className="w-4 h-4 text-emerald-600" />
                    <h3 className="text-sm font-bold text-slate-800">Tabla Scaling Up</h3>
                </div>
                <button className="text-xs flex items-center gap-1.5 px-3 py-1.5 bg-white hover:bg-slate-50 text-slate-600 rounded-lg transition-colors border border-slate-200 shadow-sm">
                    <Download className="w-3 h-3" />
                    Descargar Excel
                </button>
            </div>

            <div className="overflow-x-auto">
                <table className="w-full text-xs text-left">
                    <thead>
                        <tr className="font-bold text-white">
                            <th className="px-4 py-3 bg-slate-800 text-white min-w-[150px]">Criterio</th>
                            <th className="px-4 py-3 bg-emerald-500 min-w-[120px]">Super Green</th>
                            <th className="px-4 py-3 bg-green-500 min-w-[120px]">Green</th>
                            <th className="px-4 py-3 bg-amber-400 text-amber-900 min-w-[120px]">Yellow</th>
                            <th className="px-4 py-3 bg-red-500 min-w-[120px]">Red</th>
                            <th className="px-4 py-3 bg-slate-200 text-slate-500 min-w-[100px]">Not Eligible</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                        {tableCriteria.map((row, idx) => (
                            <tr key={idx} className="hover:bg-slate-50 transition-colors">
                                <td className="px-4 py-3 font-medium text-slate-700 bg-slate-50/50 border-r border-slate-100">
                                    {row.name}
                                </td>
                                <td className="px-4 py-3 text-slate-600 border-r border-slate-100 bg-emerald-50/50">
                                    {row.superGreen}
                                </td>
                                <td className="px-4 py-3 text-slate-600 border-r border-slate-100 bg-green-50/50">
                                    {row.green}
                                </td>
                                <td className="px-4 py-3 text-slate-600 border-r border-slate-100 bg-amber-50/50">
                                    {row.yellow}
                                </td>
                                <td className="px-4 py-3 text-slate-600 border-r border-slate-100 bg-red-50/50">
                                    {row.red}
                                </td>
                                <td className="px-4 py-3 text-slate-400 italic bg-slate-100/50">
                                    {row.notEligible}
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
            <div className="p-2 bg-slate-50 text-center border-t border-slate-100">
                <span className="text-[10px] text-slate-400 uppercase tracking-wider">
                    Powered by Booms AI
                </span>
            </div>
        </div>
    );
};

export default Stage1TableBubble;
