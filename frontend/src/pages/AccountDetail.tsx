import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { accountsAPI, stagesAPI, exportsAPI } from '../services/api';
import type { Account, Stage } from '../types';
import Loading from '../components/Loading';
import { ChevronLeft, FileText, FileSpreadsheet, Lock, CheckCircle2, Circle, ArrowRight, Building2, Globe } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const STAGE_NAMES = [
  'Booms - Buyer Persona Architect',
  'Journey - Customer Journey Mapping',
  'Ofertas 100M',
  'Selector de Canales',
  'Atlas - AEO Strategist',
  'Planner - Content Strategist',
  'Agente de Budgets',
];

const AccountDetail: React.FC = () => {
  const { accountId } = useParams<{ accountId: string }>();
  const [account, setAccount] = useState<Account | null>(null);
  const [stages, setStages] = useState<Stage[]>([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    loadData();
  }, [accountId]);

  const loadData = async () => {
    if (!accountId) return;

    try {
      const [accountData, stagesData] = await Promise.all([
        accountsAPI.getById(accountId),
        stagesAPI.getByAccount(accountId),
      ]);
      setAccount(accountData);
      setStages(stagesData);
    } catch (error) {
      console.error('Error loading account:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStageStyle = (status: string) => {
    switch (status) {
      case 'completed':
        return {
          icon: <CheckCircle2 className="w-6 h-6 text-green-500" />,
          bg: 'bg-green-50',
          border: 'border-green-100',
          text: 'text-green-700'
        };
      case 'in_progress':
        return {
          icon: <motion.div animate={{ scale: [1, 1.2, 1] }} transition={{ repeat: Infinity, duration: 2 }}><Circle className="w-6 h-6 text-primary fill-primary" /></motion.div>,
          bg: 'bg-primary/10',
          border: 'border-primary/20',
          text: 'text-primary'
        };
      case 'locked':
        return {
          icon: <Lock className="w-5 h-5 text-slate-300" />,
          bg: 'bg-slate-50',
          border: 'border-slate-100',
          text: 'text-slate-400'
        };
      default:
        return {
          icon: <Circle className="w-6 h-6 text-slate-300" />,
          bg: 'bg-slate-50',
          border: 'border-slate-100',
          text: 'text-slate-400'
        };
    }
  };

  const canAccessStage = (stage: Stage) => {
    return stage.status !== 'locked';
  };

  if (loading) return <Loading />;
  if (!account) return <div className="p-8 text-center text-muted-foreground">Account not found</div>;

  return (
    <div className="min-h-screen bg-[#F8FAFC] pb-20">
      {/* Header */}
      <div className="bg-card border-b shadow-sm sticky top-0 z-20">
        <div className="max-w-7xl mx-auto px-8 py-6">
          <button
            onClick={() => navigate('/')}
            className="flex items-center gap-2 text-sm font-semibold text-muted-foreground hover:text-primary transition-colors mb-6 group"
          >
            <ChevronLeft className="w-4 h-4 group-hover:-translate-x-1 transition-transform" />
            Back to Dashboard
          </button>

          <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
            <div className="flex items-center gap-5">
              <div className="w-16 h-16 bg-primary rounded-3xl flex items-center justify-center text-white shadow-xl shadow-primary/20">
                <Building2 className="w-8 h-8" />
              </div>
              <div>
                <h1 className="text-3xl font-heading font-extrabold text-foreground leading-tight">
                  {account.client_name}
                </h1>
                {account.company_website && (
                  <div className="flex items-center gap-2 text-muted-foreground mt-1">
                    <Globe className="w-4 h-4" />
                    <span className="text-sm font-medium">{account.company_website}</span>
                  </div>
                )}
              </div>
            </div>

            <div className="flex gap-3">
              <a
                href={exportsAPI.downloadPDF(accountId!)}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-2 px-6 py-3 bg-rose-50 text-rose-600 rounded-2xl font-bold text-sm hover:bg-rose-100 transition-all border border-rose-100"
              >
                <FileText className="w-4 h-4" />
                Export PDF
              </a>
              <a
                href={exportsAPI.downloadExcel(accountId!)}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-2 px-6 py-3 bg-emerald-50 text-emerald-600 rounded-2xl font-bold text-sm hover:bg-emerald-100 transition-all border border-emerald-100"
              >
                <FileSpreadsheet className="w-4 h-4" />
                Export Excel
              </a>
            </div>
          </div>
        </div>
      </div>

      {/* Stages Grid */}
      <div className="max-w-4xl mx-auto px-8 mt-12">
        <div className="mb-10">
          <h2 className="text-xl font-bold text-slate-900 mb-2">Project Roadmap</h2>
          <p className="text-muted-foreground text-sm font-medium">Complete each stage to unlock the full potential of the Booms Platform.</p>
        </div>

        <div className="space-y-4">
          <AnimatePresence>
            {stages.map((stage, idx) => {
              const style = getStageStyle(stage.status);
              const isLocked = stage.status === 'locked';

              return (
                <motion.div
                  key={stage.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: idx * 0.1 }}
                  onClick={() => canAccessStage(stage) && navigate(`/accounts/${accountId}/stages/${stage.stage_number}`)}
                  className={`
                    relative group overflow-hidden
                    ${canAccessStage(stage) ? 'cursor-pointer' : 'cursor-not-allowed'}
                    p-6 rounded-[2rem] border-2 transition-all duration-300
                    ${isLocked ? 'bg-secondary/50 border-border opacity-70' : 'bg-card border-border shadow-sm hover:shadow-xl hover:border-primary/20'}
                  `}
                >
                  <div className="flex items-center justify-between gap-6">
                    <div className="flex items-center gap-6">
                      <div className={`w-14 h-14 rounded-2xl flex items-center justify-center ${style.bg} transition-colors duration-300`}>
                        {style.icon}
                      </div>
                      <div>
                        <div className="flex items-center gap-3 mb-1">
                          <span className="text-[10px] font-bold uppercase tracking-[0.2em] text-slate-400">
                            Stage {stage.stage_number}
                          </span>
                          <span className={`text-[10px] font-bold uppercase tracking-widest px-2 py-0.5 rounded-full ${style.bg} ${style.text}`}>
                            {stage.status.replace('_', ' ')}
                          </span>
                        </div>
                        <h3 className={`text-lg font-bold ${isLocked ? 'text-slate-400' : 'text-slate-900'}`}>
                          {STAGE_NAMES[stage.stage_number - 1]}
                        </h3>
                      </div>
                    </div>

                    <div className="flex items-center gap-4">
                      {stage.completed_at && (
                        <div className="text-right hidden md:block">
                          <p className="text-[10px] font-bold text-slate-300 uppercase underline decoration-blue-500/30">Completed on</p>
                          <p className="text-xs font-bold text-slate-500">{new Date(stage.completed_at).toLocaleDateString()}</p>
                        </div>
                      )}
                      {canAccessStage(stage) && (
                        <ArrowRight className="w-5 h-5 text-primary group-hover:translate-x-1 transition-transform" />
                      )}
                    </div>
                  </div>
                </motion.div>
              );
            })}
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
};

export default AccountDetail;
