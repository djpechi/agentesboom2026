import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { accountsAPI } from '../services/api';
import type { Account } from '../types';
import Loading from '../components/Loading';
import { Plus, Building2, Globe, Cpu, MoreVertical, Search, Sparkles, X, Trash2, RefreshCw, AlertTriangle } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '../context/AuthContext';

const Dashboard: React.FC = () => {
  const { user } = useAuth();
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [loading, setLoading] = useState(true);

  // Create Account Modal State
  const [showModal, setShowModal] = useState(false);
  const [clientName, setClientName] = useState('');
  const [companyWebsite, setCompanyWebsite] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [aiModel, setAiModel] = useState('openai-gpt4o');

  // Menu & Delete Modal State
  const [activeMenuId, setActiveMenuId] = useState<string | null>(null);
  const [deleteTargetId, setDeleteTargetId] = useState<string | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  const navigate = useNavigate();

  // Calculate Stats
  const completedAccounts = accounts.filter(acc =>
    acc.stages?.find(s => s.stage_number === 7)?.status === 'completed'
  ).length;
  const pendingAccounts = accounts.length - completedAccounts;

  useEffect(() => {
    loadAccounts();

    // Close menu when clicking outside
    const handleClickOutside = () => setActiveMenuId(null);
    window.addEventListener('click', handleClickOutside);
    return () => window.removeEventListener('click', handleClickOutside);
  }, []);

  const loadAccounts = async () => {
    try {
      const data = await accountsAPI.getAll();
      setAccounts(data);
    } catch (error) {
      console.error('Error loading accounts:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateAccount = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await accountsAPI.create({
        client_name: clientName,
        company_website: companyWebsite || undefined,
        ai_model: aiModel
      });
      setShowModal(false);
      setClientName('');
      setCompanyWebsite('');
      setAiModel('openai-gpt4o');
      loadAccounts();
    } catch (error) {
      console.error('Error creating account:', error);
    }
  };

  const toggleMenu = (e: React.MouseEvent, accountId: string) => {
    e.stopPropagation(); // Prevent card click
    setActiveMenuId(activeMenuId === accountId ? null : accountId);
  };

  const handleDeleteClick = (e: React.MouseEvent, accountId: string) => {
    e.stopPropagation();
    setActiveMenuId(null);
    setDeleteTargetId(accountId);
  };

  const confirmDelete = async () => {
    if (!deleteTargetId) return;

    setIsDeleting(true);
    try {
      await accountsAPI.delete(deleteTargetId);
      await loadAccounts();
      setDeleteTargetId(null);
    } catch (error) {
      console.error('Error deleting account:', error);
    } finally {
      setIsDeleting(false);
    }
  };

  const filteredAccounts = accounts.filter(acc =>
    acc.client_name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const accountToDelete = accounts.find(a => a.id === deleteTargetId);

  if (loading) return <Loading />;

  return (
    <div className="min-h-screen bg-[#F8FAFC] pb-12">
      {/* Hero Section */}
      <section className="bg-card border-b px-8 py-12 mb-8 shadow-sm">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-end gap-6">
          <div className="space-y-2">
            <h1 className="text-4xl font-heading font-extrabold tracking-tight text-foreground flex items-center gap-3">
              <Sparkles className="text-primary w-8 h-8" />
              Bienvenido a BOOMS, {user?.full_name || 'Consultor'}
            </h1>
            <p className="text-muted-foreground text-lg">
              Actualmente tienes <span className="font-bold text-foreground">{completedAccounts}</span> cuentas completadas y <span className="font-bold text-foreground">{pendingAccounts}</span> por completar.
            </p>
          </div>
          <button
            onClick={() => setShowModal(true)}
            className="btn-premium px-8 py-4 bg-primary text-white rounded-2xl font-bold flex items-center gap-2 shadow-lg shadow-primary/20"
          >
            <Plus className="w-5 h-5" />
            New Account
          </button>
        </div>
      </section>

      <div className="max-w-7xl mx-auto px-8">
        {/* Search & Filters */}
        <div className="mb-8 relative max-w-md">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-muted-foreground w-4 h-4" />
          <input
            type="text"
            placeholder="Search clients..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-3 bg-card border border-border rounded-xl focus:ring-2 focus:ring-primary/10 focus:border-primary transition-all outline-none"
          />
        </div>

        {filteredAccounts.length === 0 ? (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center py-20 bg-card border border-border rounded-3xl shadow-sm"
          >
            <div className="w-20 h-20 bg-secondary/50 rounded-full flex items-center justify-center mx-auto mb-4">
              <Building2 className="w-10 h-10 text-muted-foreground" />
            </div>
            <h2 className="text-xl font-bold text-foreground mb-2">No accounts found</h2>
            <p className="text-muted-foreground mb-8">Ready to start a new project?</p>
            <button
              onClick={() => setShowModal(true)}
              className="text-primary font-bold hover:underline"
            >
              Create your first account
            </button>
          </motion.div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <AnimatePresence mode="popLayout">
              {filteredAccounts.map((account, idx) => (
                <motion.div
                  key={account.id}
                  layout
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: idx * 0.05 }}
                  onClick={() => navigate(`/accounts/${account.id}`)}
                  className="card-premium group cursor-pointer relative"
                >
                  <div className="flex justify-between items-start mb-6">
                    <div className="w-12 h-12 bg-primary/10 text-primary rounded-xl flex items-center justify-center group-hover:bg-primary group-hover:text-white transition-colors duration-300">
                      <Building2 className="w-6 h-6" />
                    </div>
                    <div className="relative">
                      <button
                        onClick={(e) => toggleMenu(e, account.id)}
                        className={`p-2 rounded-lg transition-colors ${activeMenuId === account.id ? 'bg-secondary text-primary' : 'hover:bg-secondary text-muted-foreground'}`}
                      >
                        <MoreVertical className="w-4 h-4" />
                      </button>

                      {/* Dropdown Menu */}
                      <AnimatePresence>
                        {activeMenuId === account.id && (
                          <motion.div
                            initial={{ opacity: 0, scale: 0.95, y: 10 }}
                            animate={{ opacity: 1, scale: 1, y: 0 }}
                            exit={{ opacity: 0, scale: 0.95, y: 10 }}
                            transition={{ duration: 0.1 }}
                            className="absolute right-0 top-full mt-2 w-48 bg-white border border-border rounded-xl shadow-xl z-30 overflow-hidden"
                            onClick={(e) => e.stopPropagation()}
                          >
                            <div className="py-1.5">
                              <button
                                onClick={(e) => { e.stopPropagation(); /* Add logic */ setActiveMenuId(null); }}
                                className="w-full text-left px-4 py-2.5 text-sm font-medium text-slate-700 hover:bg-slate-50 flex items-center gap-2 transition-colors"
                              >
                                <RefreshCw className="w-4 h-4 text-slate-400" />
                                Reiniciar
                              </button>
                              <div className="h-px bg-slate-100 my-1" />
                              <button
                                onClick={(e) => handleDeleteClick(e, account.id)}
                                className="w-full text-left px-4 py-2.5 text-sm font-medium text-red-600 hover:bg-red-50 flex items-center gap-2 transition-colors"
                              >
                                <Trash2 className="w-4 h-4 text-red-500" />
                                Eliminar
                              </button>
                            </div>
                          </motion.div>
                        )}
                      </AnimatePresence>
                    </div>
                  </div>

                  <h3 className="text-xl font-bold text-slate-900 mb-2 truncate">
                    {account.client_name}
                  </h3>

                  <div className="space-y-3 mb-6">
                    {account.company_website && (
                      <div className="flex items-center gap-2 text-sm text-muted-foreground group-hover:text-slate-600 transition-colors">
                        <Globe className="w-3.5 h-3.5" />
                        <span className="truncate">{account.company_website}</span>
                      </div>
                    )}
                    <div className="flex items-center gap-2 text-sm text-muted-foreground group-hover:text-slate-600 transition-colors">
                      <Cpu className="w-3.5 h-3.5" />
                      <span>{account.ai_model}</span>
                    </div>

                    {/* Progress Bar */}
                    <div className="mt-4 pt-4 border-t border-slate-50">
                      <div className="flex justify-between items-center mb-1.5">
                        <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Progreso</span>
                        <span className="text-[10px] font-bold text-primary">{Math.round((account.stages?.filter(s => s.status === 'completed').length || 0) / 7 * 100)}%</span>
                      </div>
                      <div className="h-1.5 w-full bg-slate-100 rounded-full overflow-hidden">
                        <motion.div
                          className="h-full bg-primary"
                          initial={{ width: 0 }}
                          animate={{ width: `${(account.stages?.filter(s => s.status === 'completed').length || 0) / 7 * 100}%` }}
                          transition={{ duration: 1, ease: "easeOut" }}
                        />
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center justify-between pt-4 border-t border-border group-hover:border-primary/20 transition-colors">
                    <span className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground bg-secondary px-2 py-1 rounded">
                      ID: {account.id.slice(0, 8)}
                    </span>
                    <div className="flex -space-x-2">
                      {[1, 2, 3].map(i => (
                        <div key={i} className="w-6 h-6 rounded-full bg-primary/10 border-2 border-white" />
                      ))}
                    </div>
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
        )}
      </div>

      {/* Create Account Modal */}
      <AnimatePresence>
        {showModal && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-slate-900/40 backdrop-blur-sm z-50 flex justify-center items-center py-10"
            onClick={() => setShowModal(false)}
          >
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 20 }}
              className="bg-card rounded-[2rem] shadow-2xl p-10 w-full max-w-xl relative mx-4 overflow-hidden border border-border"
              onClick={(e) => e.stopPropagation()}
            >
              <button
                onClick={() => setShowModal(false)}
                className="absolute right-6 top-6 p-2 hover:bg-secondary rounded-full transition-colors"
              >
                <X className="w-5 h-5 text-muted-foreground" />
              </button>

              <div className="mb-8">
                <h2 className="text-3xl font-heading font-extrabold text-foreground mb-2">Initialize Project</h2>
                <p className="text-muted-foreground">Start by providing basic information about your client.</p>
              </div>

              <form onSubmit={handleCreateAccount} className="space-y-6">
                <div className="space-y-2">
                  <label className="text-sm font-bold text-foreground/70 ml-1">Client / Brand Name</label>
                  <input
                    type="text"
                    value={clientName}
                    onChange={(e) => setClientName(e.target.value)}
                    required
                    placeholder="e.g. Acme SaaS"
                    className="w-full px-6 py-4 bg-secondary/50 border border-border rounded-2xl focus:ring-4 focus:ring-primary/10 focus:border-primary transition-all outline-none"
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-bold text-foreground/70 ml-1">Company Website</label>
                  <input
                    type="text"
                    value={companyWebsite}
                    onChange={(e) => setCompanyWebsite(e.target.value)}
                    placeholder="example.com"
                    className="w-full px-6 py-4 bg-secondary/50 border border-border rounded-2xl focus:ring-4 focus:ring-primary/10 focus:border-primary transition-all outline-none"
                  />
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-bold text-foreground/70 ml-1">AI Intelligence Model</label>
                  <select
                    value={aiModel}
                    onChange={(e) => setAiModel(e.target.value)}
                    className="w-full px-6 py-4 bg-secondary/50 border border-border rounded-2xl focus:ring-4 focus:ring-primary/10 focus:border-primary transition-all outline-none appearance-none cursor-pointer"
                  >
                    <option value="openai-gpt4o">OpenAI GPT-4o (Standard)</option>
                    <option value="gemini-2.0-flash">Google Gemini 2.0 Flash (Fast & Smart)</option>
                    <option value="gemini-1.5-pro">Google Gemini 1.5 Pro (Extreme Reasoning)</option>
                  </select>
                </div>

                <div className="pt-4 flex gap-4">
                  <button
                    type="button"
                    onClick={() => setShowModal(false)}
                    className="flex-1 py-4 px-6 rounded-2xl font-bold bg-secondary text-muted-foreground hover:bg-secondary/80 transition-colors"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="flex-1 py-4 px-6 rounded-2xl font-bold bg-primary text-white hover:bg-primary/90 transition-all btn-premium shadow-lg shadow-primary/20"
                  >
                    Initialize Account
                  </button>
                </div>
              </form>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Delete Confirmation Modal */}
      <AnimatePresence>
        {deleteTargetId && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-slate-900/40 backdrop-blur-sm z-50 flex justify-center items-center py-10"
            onClick={() => setDeleteTargetId(null)}
          >
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 20 }}
              className="bg-white rounded-[2rem] shadow-2xl p-8 w-full max-w-md relative mx-4 overflow-hidden border border-red-100"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="w-16 h-16 bg-red-50 rounded-full flex items-center justify-center mx-auto mb-6">
                <AlertTriangle className="w-8 h-8 text-red-500" />
              </div>

              <div className="text-center mb-8">
                <h2 className="text-2xl font-heading font-extrabold text-slate-900 mb-2">Are you sure?</h2>
                <p className="text-slate-500">
                  You are about to delete <span className="font-bold text-slate-800">{accountToDelete?.client_name}</span>. This action cannot be undone.
                </p>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <button
                  onClick={() => setDeleteTargetId(null)}
                  className="py-3 px-4 rounded-xl font-bold bg-slate-100 text-slate-600 hover:bg-slate-200 transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={confirmDelete}
                  disabled={isDeleting}
                  className="py-3 px-4 rounded-xl font-bold bg-red-500 text-white hover:bg-red-600 transition-all shadow-lg shadow-red-500/20 disabled:opacity-70 flex justify-center items-center"
                >
                  {isDeleting ? 'Deleting...' : 'Delete Account'}
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default Dashboard;
