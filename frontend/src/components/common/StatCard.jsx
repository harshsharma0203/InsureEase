import React from 'react';
import { TrendingUp, TrendingDown } from 'lucide-react';

export const StatCard = ({
  title,
  value,
  subtitle,
  icon: Icon,
  trend,
  trendLabel,
  color = 'brand', // brand, emerald, amber, rose, indigo, purple
  prefix = '',
  suffix = '',
  onClick,
}) => {
  const colorMap = {
    brand: {
      bg: 'bg-brand-50/70 text-brand-600',
      border: 'border-brand-100/60',
      glow: 'from-brand-500/10 to-transparent',
    },
    emerald: {
      bg: 'bg-emerald-50 text-emerald-600',
      border: 'border-emerald-100',
      glow: 'from-emerald-500/10 to-transparent',
    },
    amber: {
      bg: 'bg-amber-50 text-amber-600',
      border: 'border-amber-100',
      glow: 'from-amber-500/10 to-transparent',
    },
    rose: {
      bg: 'bg-rose-50 text-rose-600',
      border: 'border-rose-100',
      glow: 'from-rose-500/10 to-transparent',
    },
    indigo: {
      bg: 'bg-indigo-50 text-indigo-600',
      border: 'border-indigo-100',
      glow: 'from-indigo-500/10 to-transparent',
    },
    purple: {
      bg: 'bg-purple-50 text-purple-600',
      border: 'border-purple-100',
      glow: 'from-purple-500/10 to-transparent',
    },
  };

  const scheme = colorMap[color] || colorMap.brand;

  return (
    <div
      onClick={onClick}
      className={`relative bg-white rounded-2xl border ${scheme.border} p-5 shadow-sm hover:shadow-md transition-all duration-200 overflow-hidden ${
        onClick ? 'cursor-pointer hover:-translate-y-0.5' : ''
      }`}
    >
      <div className={`absolute top-0 right-0 w-28 h-28 bg-gradient-to-bl ${scheme.glow} rounded-bl-full pointer-events-none`} />
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-1">{title}</p>
          <h4 className="text-2xl font-bold text-slate-800 tracking-tight">
            {prefix}
            {typeof value === 'number' ? value.toLocaleString('en-IN') : value}
            {suffix}
          </h4>
        </div>
        {Icon && (
          <div className={`p-3 rounded-xl ${scheme.bg} flex-shrink-0 shadow-sm`}>
            <Icon className="w-5 h-5" />
          </div>
        )}
      </div>

      {(subtitle || trend) && (
        <div className="mt-3 flex items-center gap-2 text-xs">
          {trend && (
            <span
              className={`inline-flex items-center gap-0.5 font-semibold ${
                trend > 0 ? 'text-emerald-600' : 'text-rose-600'
              }`}
            >
              {trend > 0 ? <TrendingUp className="w-3.5 h-3.5" /> : <TrendingDown className="w-3.5 h-3.5" />}
              {Math.abs(trend)}%
            </span>
          )}
          {trendLabel && <span className="text-slate-400">{trendLabel}</span>}
          {subtitle && !trend && <span className="text-slate-500 font-medium">{subtitle}</span>}
        </div>
      )}
    </div>
  );
};
