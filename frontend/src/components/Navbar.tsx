import React from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { LogOut, User } from 'lucide-react';

const Navbar: React.FC = () => {
  const { user, logout, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  if (!isAuthenticated) return null;

  return (
    <nav className="glass sticky top-0 z-50 px-8 py-3 shadow-lg border-b border-white/20">
      <div className="max-w-7xl mx-auto flex justify-between items-center">
        <div
          className="flex items-center gap-2 cursor-pointer group"
          onClick={() => navigate('/')}
        >
          <img
            src="https://cdn.prod.website-files.com/6895075df5b2d74c09e7ba17/689e19b90c62b3f645801e5a_Group%207%20(2).png"
            alt="BOOMS Logo"
            className="h-8 w-auto group-hover:scale-105 transition-transform"
          />
        </div>

        <div className="flex items-center gap-6">
          <div className="flex items-center gap-3 px-4 py-2 bg-secondary/50 rounded-2xl border border-border">
            <div className="w-8 h-8 bg-background rounded-full flex items-center justify-center text-primary shadow-sm border">
              <User className="w-4 h-4" />
            </div>
            <div className="hidden sm:block">
              <p className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground leading-none mb-0.5">Account</p>
              <p className="text-xs font-bold text-foreground leading-none">{user?.email}</p>
            </div>
          </div>

          <button
            onClick={handleLogout}
            className="p-2.5 text-muted-foreground hover:text-primary hover:bg-primary/10 rounded-xl transition-all duration-300"
            title="Logout"
          >
            <LogOut className="w-5 h-5" />
          </button>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
