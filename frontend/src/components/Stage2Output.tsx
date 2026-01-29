import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Map, Database, FileText, Download, Table as TableIcon } from 'lucide-react';

interface Stage2Data {
    narrative: string;
    markdown_table: string;
    csv_block: string;
    hubspot_props: string[];
}

interface Stage2OutputProps {
    data: Stage2Data;
    clientName: string;
}

const Stage2Output: React.FC<Stage2OutputProps> = ({ data, clientName }) => {
    const [activeTab, setActiveTab] = useState<'narrative' | 'table' | 'hubspot' | 'csv'>('narrative');

    if (!data) return null;

    // Helper to clean and parse markdown table
    const parseMarkdownTable = (md: string) => {
        if (!md) return { headers: [], rows: [] };
        const lines = md.trim().split('\n').filter(line => line.trim().startsWith('|'));
        if (lines.length < 2) return { headers: [], rows: [] };

        const headers = lines[0].split('|').map(c => c.trim()).filter(c => c);
        const rows = lines.slice(2).map(line =>
            line.split('|').map(c => c.trim()).filter(c => c)
        );
        return { headers, rows };
    };

    const { headers, rows } = parseMarkdownTable(data.markdown_table);

    const downloadCsv = () => {
        const blob = new Blob([data.csv_block], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${clientName.replace(/\s+/g, '_')}_journey_map.csv`;
        a.click();
        window.URL.revokeObjectURL(url);
    };

    return (
        <div className="space-y-8 pb-12">
            {/* Header */}
            <div className="bg-gradient-to-br from-blue-50 to-indigo-50 p-6 rounded-2xl border border-blue-100">
                <div className="flex items-center gap-3 mb-2">
                    <div className="p-2 bg-blue-100 rounded-lg">
                        <Map className="w-5 h-5 text-blue-600" />
                    </div>
                    <h2 className="text-xl font-bold text-slate-800">Customer Journey Map</h2>
                </div>
                <p className="text-slate-600 text-sm">
                    Comprehensive journey mapping for <span className="font-semibold text-blue-700">{clientName}</span>.
                </p>
            </div>

            {/* Tabs */}
            <div className="flex gap-2 border-b border-slate-200">
                <button
                    onClick={() => setActiveTab('narrative')}
                    className={`px-4 py-2 text-sm font-semibold border-b-2 transition-colors flex items-center gap-2 ${activeTab === 'narrative' ? 'border-primary text-primary' : 'border-transparent text-slate-500 hover:text-slate-700'}`}
                >
                    <FileText className="w-4 h-4" /> Narrative
                </button>
                <button
                    onClick={() => setActiveTab('table')}
                    className={`px-4 py-2 text-sm font-semibold border-b-2 transition-colors flex items-center gap-2 ${activeTab === 'table' ? 'border-primary text-primary' : 'border-transparent text-slate-500 hover:text-slate-700'}`}
                >
                    <TableIcon className="w-4 h-4" /> Journey Table
                </button>
                <button
                    onClick={() => setActiveTab('hubspot')}
                    className={`px-4 py-2 text-sm font-semibold border-b-2 transition-colors flex items-center gap-2 ${activeTab === 'hubspot' ? 'border-primary text-primary' : 'border-transparent text-slate-500 hover:text-slate-700'}`}
                >
                    <Database className="w-4 h-4" /> HubSpot Props
                </button>
                <button
                    onClick={() => setActiveTab('csv')}
                    className={`px-4 py-2 text-sm font-semibold border-b-2 transition-colors flex items-center gap-2 ${activeTab === 'csv' ? 'border-primary text-primary' : 'border-transparent text-slate-500 hover:text-slate-700'}`}
                >
                    <Download className="w-4 h-4" /> CSV Export
                </button>
            </div>

            {/* Content Content */}
            <div className="bg-white rounded-xl border border-slate-200 shadow-sm min-h-[400px]">

                {activeTab === 'narrative' && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        className="p-8 prose prose-slate max-w-none prose-headings:font-heading prose-headings:text-slate-800 prose-p:text-slate-600"
                    >
                        {/* Simple newline to paragraph conversion for now if raw text often lacks markdown blocks */}
                        {data.narrative?.split('\n').map((para, i) => (
                            para.trim() && <p key={i} className="mb-4">{para}</p>
                        ))}
                    </motion.div>
                )}

                {activeTab === 'table' && (
                    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="p-0 overflow-x-auto">
                        <table className="w-full text-sm text-left">
                            <thead className="bg-slate-50 text-slate-700 font-bold border-b border-slate-200">
                                <tr>
                                    {headers.map((h, i) => (
                                        <th key={i} className="px-6 py-4 whitespace-nowrap">{h}</th>
                                    ))}
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-slate-100">
                                {rows.map((row, i) => (
                                    <tr key={i} className="hover:bg-slate-50/50 transition-colors">
                                        {row.map((cell, j) => (
                                            <td key={j} className="px-6 py-4 align-top text-slate-600 min-w-[150px]">
                                                {cell}
                                            </td>
                                        ))}
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                        {rows.length === 0 && (
                            <div className="p-8 text-center text-muted-foreground italic">No table data available</div>
                        )}
                    </motion.div>
                )}

                {activeTab === 'hubspot' && (
                    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="p-8">
                        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                            {data.hubspot_props?.map((prop, i) => (
                                <div key={i} className="p-4 bg-orange-50 rounded-lg border border-orange-100 flex items-start gap-3">
                                    <div className="mt-1 p-1 bg-orange-100 rounded text-orange-600">
                                        <Database className="w-4 h-4" />
                                    </div>
                                    <div className="text-sm font-mono text-orange-900 break-all">{prop}</div>
                                </div>
                            )) || <div className="col-span-3 text-center text-slate-400">No properties defined</div>}
                        </div>
                    </motion.div>
                )}

                {activeTab === 'csv' && (
                    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="p-8">
                        <div className="mb-6 flex justify-between items-center">
                            <h3 className="font-bold text-slate-800">Raw CSV Data</h3>
                            <button
                                onClick={downloadCsv}
                                className="flex items-center gap-2 px-4 py-2 bg-slate-900 text-white rounded-lg hover:bg-slate-800 transition-colors text-sm font-bold"
                            >
                                <Download className="w-4 h-4" /> Download CSV
                            </button>
                        </div>
                        <div className="bg-slate-900 rounded-lg p-4 overflow-x-auto shadow-inner">
                            <pre className="text-xs font-mono text-slate-300 whitespace-pre">{data.csv_block}</pre>
                        </div>
                    </motion.div>
                )}
            </div>
        </div>
    );
};

export default Stage2Output;
