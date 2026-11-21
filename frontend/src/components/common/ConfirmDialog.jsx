import React from 'react';
import { Modal } from './Modal';
import { AlertCircle, CheckCircle, AlertTriangle } from 'lucide-react';

export const ConfirmDialog = ({
  isOpen,
  onClose,
  onConfirm,
  title,
  message,
  confirmText = 'Confirm',
  cancelText = 'Cancel',
  type = 'primary', // primary, danger, success, warning
  loading = false,
}) => {
  const getColors = () => {
    switch (type) {
      case 'danger':
        return {
          icon: <AlertCircle className="w-8 h-8 text-rose-600" />,
          btn: 'bg-rose-600 hover:bg-rose-700 text-white',
        };
      case 'success':
        return {
          icon: <CheckCircle className="w-8 h-8 text-emerald-600" />,
          btn: 'bg-emerald-600 hover:bg-emerald-700 text-white',
        };
      case 'warning':
        return {
          icon: <AlertTriangle className="w-8 h-8 text-amber-600" />,
          btn: 'bg-amber-600 hover:bg-amber-700 text-white',
        };
      default:
        return {
          icon: <AlertCircle className="w-8 h-8 text-brand-600" />,
          btn: 'bg-brand-600 hover:bg-brand-700 text-white',
        };
    }
  };

  const { icon, btn } = getColors();

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={title} maxWidth="max-w-md">
      <div className="flex items-start gap-4 mb-6">
        <div className="p-2.5 rounded-full bg-slate-100 flex-shrink-0">{icon}</div>
        <p className="text-sm text-slate-600 leading-relaxed pt-1">{message}</p>
      </div>
      <div className="flex items-center justify-end gap-3 pt-4 border-t border-slate-100">
        <button
          type="button"
          onClick={onClose}
          disabled={loading}
          className="px-4 py-2 text-sm font-medium text-slate-700 bg-slate-100 hover:bg-slate-200 rounded-xl transition-colors disabled:opacity-50"
        >
          {cancelText}
        </button>
        <button
          type="button"
          onClick={onConfirm}
          disabled={loading}
          className={`px-4 py-2 text-sm font-semibold rounded-xl shadow-sm transition-colors disabled:opacity-50 ${btn}`}
        >
          {loading ? 'Processing...' : confirmText}
        </button>
      </div>
    </Modal>
  );
};
