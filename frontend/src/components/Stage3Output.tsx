import React from 'react';
import {
    Zap, Star, Clock, TrendingUp, ShieldCheck, Gift,
    Target, Info, Check
} from 'lucide-react';

interface ValueEquation {
    dream_outcome: string;
    perceived_likelihood: string;
    time_delay: string;
    effort_sacrifice: string;
}

interface StoryBrand {
    character: string;
    problem: string;
    guide: string;
    plan: string;
    call_to_action: string;
    success: string;
    failure: string;
}

interface OfferStack {
    core_offer: string;
    bonuses: string[];
    guarantees: string[];
    scarcity_urgency?: string;
    naming?: string;
}

interface Stage3Data {
    value_equation?: ValueEquation;
    storybrand?: StoryBrand;
    offer_stack?: OfferStack;
}

interface Stage3OutputProps {
    data: Stage3Data;
    clientName: string;
}

const Stage3Output: React.FC<Stage3OutputProps> = ({ data, clientName }) => {
    if (!data) return null;

    return (
        <div className="space-y-10 pb-12">
            {/* Header */}
            <div className="bg-gradient-to-br from-purple-50 to-pink-50 p-6 rounded-2xl border border-purple-100">
                <div className="flex items-center gap-3 mb-2">
                    <div className="p-2 bg-purple-100 rounded-lg">
                        <Zap className="w-5 h-5 text-purple-600" />
                    </div>
                    <h2 className="text-xl font-bold text-slate-800">$100M Offer Construction</h2>
                </div>
                <p className="text-slate-600 text-sm">
                    Building an irresistible offer for <span className="font-semibold text-purple-700">{clientName}</span> using Hormozi & StoryBrand frameworks.
                </p>
            </div>

            {/* 1. Value Equation */}
            {data.value_equation && (
                <div className="space-y-4">
                    <h3 className="flex items-center gap-2 font-bold text-slate-800 text-lg">
                        <TrendingUp className="w-5 h-5 text-green-600" />
                        The Value Equation
                    </h3>
                    <div className="bg-slate-900 text-white p-6 rounded-xl shadow-lg relative overflow-hidden">
                        {/* Abstract visual background */}
                        <div className="absolute top-0 right-0 w-64 h-64 bg-purple-500/10 rounded-full blur-3xl -mr-32 -mt-32"></div>

                        <div className="relative z-10 grid grid-cols-2 gap-8">
                            {/* Numerator (Increase these) */}
                            <div className="space-y-6">
                                <div>
                                    <div className="flex items-center gap-2 text-green-400 mb-1 text-xs font-bold uppercase tracking-wider">
                                        <Star className="w-3 h-3" /> Dream Outcome
                                    </div>
                                    <p className="text-lg font-medium leading-snug">{data.value_equation.dream_outcome || "Pending..."}</p>
                                </div>
                                <div>
                                    <div className="flex items-center gap-2 text-green-400 mb-1 text-xs font-bold uppercase tracking-wider">
                                        <Target className="w-3 h-3" /> Perceived Likelihood
                                    </div>
                                    <p className="text-lg font-medium leading-snug">{data.value_equation.perceived_likelihood || "Pending..."}</p>
                                </div>
                            </div>

                            {/* Divider */}
                            <div className="absolute left-1/2 top-0 bottom-0 w-px bg-white/10 hidden md:block"></div>
                            <div className="absolute top-1/2 left-4 right-4 h-px bg-white/20 md:hidden"></div>

                            {/* Denominator (Decrease these) */}
                            <div className="space-y-6">
                                <div>
                                    <div className="flex items-center gap-2 text-red-400 mb-1 text-xs font-bold uppercase tracking-wider">
                                        <Clock className="w-3 h-3" /> Time Delay
                                    </div>
                                    <p className="text-lg font-medium leading-snug opacity-90">{data.value_equation.time_delay || "Pending..."}</p>
                                </div>
                                <div>
                                    <div className="flex items-center gap-2 text-red-400 mb-1 text-xs font-bold uppercase tracking-wider">
                                        <TrendingUp className="w-3 h-3 rotate-180" /> Effort & Sacrifice
                                    </div>
                                    <p className="text-lg font-medium leading-snug opacity-90">{data.value_equation.effort_sacrifice || "Pending..."}</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* 2. StoryBrand Framework */}
            {data.storybrand && (
                <div className="space-y-4">
                    <h3 className="flex items-center gap-2 font-bold text-slate-800 text-lg">
                        <Info className="w-5 h-5 text-blue-600" />
                        StoryBrand (SB7)
                    </h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                        <SB7Card step="1. Character" content={data.storybrand.character} bg="bg-blue-50" border="border-blue-100" />
                        <SB7Card step="2. Problem" content={data.storybrand.problem} bg="bg-red-50" border="border-red-100" />
                        <SB7Card step="3. Guide" content={data.storybrand.guide} bg="bg-indigo-50" border="border-indigo-100" />
                        <SB7Card step="4. Plan" content={data.storybrand.plan} bg="bg-emerald-50" border="border-emerald-100" />
                        <SB7Card step="5. Call to Action" content={data.storybrand.call_to_action} bg="bg-amber-50" border="border-amber-100" />
                        <div className="md:col-span-2 grid grid-cols-2 gap-3">
                            <SB7Card step="6. Success" content={data.storybrand.success} bg="bg-green-50" border="border-green-100" />
                            <SB7Card step="7. Failure" content={data.storybrand.failure} bg="bg-slate-50" border="border-slate-200" />
                        </div>
                    </div>
                </div>
            )}

            {/* 3. Offer Stack */}
            {data.offer_stack && (
                <div className="space-y-4">
                    <h3 className="flex items-center gap-2 font-bold text-slate-800 text-lg">
                        <Gift className="w-5 h-5 text-pink-600" />
                        The Offer Stack
                    </h3>
                    <div className="bg-white rounded-xl border-2 border-slate-100 overflow-hidden shadow-sm">
                        {/* Named Offer Header */}
                        <div className="bg-slate-50 p-6 text-center border-b border-slate-100">
                            <span className="text-xs font-bold text-slate-400 uppercase tracking-widest">Grand Slam Offer</span>
                            <h4 className="text-2xl font-black text-slate-900 mt-2">{data.offer_stack.naming || "Untitled Offer"}</h4>
                            <p className="text-slate-600 mt-2">{data.offer_stack.core_offer}</p>
                        </div>

                        <div className="p-6 space-y-8">
                            {/* Bonuses */}
                            <div>
                                <h5 className="font-bold text-sm text-slate-500 uppercase tracking-wider mb-4 flex items-center gap-2">
                                    <Gift className="w-4 h-4 text-pink-500" /> Bonuses (Value Adds)
                                </h5>
                                <ul className="space-y-3">
                                    {data.offer_stack.bonuses?.map((bonus, i) => (
                                        <li key={i} className="flex items-start gap-3 p-3 bg-pink-50/50 rounded-lg">
                                            <Check className="w-5 h-5 text-pink-600 shrink-0 mt-0.5" />
                                            <span className="text-slate-800 font-medium text-sm">{bonus}</span>
                                        </li>
                                    )) || <li className="text-slate-400 text-sm italic">No bonuses defined yet.</li>}
                                </ul>
                            </div>

                            {/* Guarantees */}
                            <div>
                                <h5 className="font-bold text-sm text-slate-500 uppercase tracking-wider mb-4 flex items-center gap-2">
                                    <ShieldCheck className="w-4 h-4 text-emerald-500" /> Risk Reversal
                                </h5>
                                <ul className="space-y-2">
                                    {data.offer_stack.guarantees?.map((g, i) => (
                                        <li key={i} className="flex items-center gap-2 text-sm text-slate-700">
                                            <ShieldCheck className="w-4 h-4 text-emerald-500 shrink-0" />
                                            {g}
                                        </li>
                                    )) || <li className="text-slate-400 text-sm italic">No guarantees defined yet.</li>}
                                </ul>
                            </div>

                            {/* Scarcity */}
                            {data.offer_stack.scarcity_urgency && (
                                <div className="bg-amber-50 border border-amber-100 rounded-lg p-3 text-sm text-amber-800 flex items-start gap-2">
                                    <Clock className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
                                    {data.offer_stack.scarcity_urgency}
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

const SB7Card = ({ step, content, bg, border }: { step: string, content: string, bg: string, border: string }) => (
    <div className={`p-4 rounded-lg border ${bg} ${border}`}>
        <div className="text-xs font-bold opacity-60 uppercase tracking-wider mb-1">{step}</div>
        <div className="text-sm font-medium text-slate-800 leading-snug">{content || "..."}</div>
    </div>
);

export default Stage3Output;
