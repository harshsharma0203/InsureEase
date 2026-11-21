import React, { useState, useEffect } from 'react';
import { CreditCard, Download, Plus, CheckCircle2, IndianRupee, Eye, RefreshCw, FileText } from 'lucide-react';
import { billingService } from '../../services/api';
import { DataTable } from '../../components/common/DataTable';
import { Badge } from '../../components/common/Badge';
import { Modal } from '../../components/common/Modal';
import { useToast } from '../../context/ToastContext';
import { useAuth } from '../../context/AuthContext';

export const InvoicesList = () => {
  const [activeTab, setActiveTab] = useState('invoices'); // 'invoices' | 'payments'
  const [invoices, setInvoices] = useState([]);
  const [payments, setPayments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState('');

  // Payment recording modal
  const [paymentModal, setPaymentModal] = useState(null); // invoice
  const [payForm, setPayForm] = useState({
    amount: '',
    payment_method: 'NEFT',
    transaction_id: '',
    payer_name: '',
    notes: 'Premium payment wire transferred via corporate bank account.',
  });
  const [submitting, setSubmitting] = useState(false);

  const { success, error } = useToast();
  const { hasRole } = useAuth();
  const canPay = hasRole(['SUPER_ADMIN', 'INSURANCE_ADMIN', 'FINANCE_OFFICER', 'GROUP_MANAGER']);

  useEffect(() => {
    loadData();
  }, [activeTab, statusFilter]);

  const loadData = async () => {
    setLoading(true);
    try {
      if (activeTab === 'invoices') {
        const params = {};
        if (statusFilter) params.status = statusFilter;
        const res = await billingService.getInvoices(params);
        setInvoices(res.data.results || res.data);
      } else {
        const res = await billingService.getPayments();
        setPayments(res.data.results || res.data);
      }
    } catch (err) {
      error('Failed to load financial records.');
    } finally {
      setLoading(false);
    }
  };

  const handleOpenPayment = (inv) => {
    setPaymentModal(inv);
    setPayForm({
      amount: inv.balance_due,
      payment_method: 'NEFT',
      transaction_id: `TXN-${new Date().toISOString().slice(0, 10).replace(/-/g, '')}-${Math.floor(1000 + Math.random() * 9000)}`,
      payer_name: inv.group_name,
      notes: `Wire transfer received for Invoice ${inv.invoice_number}.`,
    });
  };

  const handleRecordPayment = async (e) => {
    e.preventDefault();
    if (!paymentModal) return;
    setSubmitting(true);
    try {
      await billingService.recordPayment(paymentModal.id, payForm);
      success(`Payment of ₹${Number(payForm.amount).toLocaleString('en-IN')} recorded successfully.`);
      setPaymentModal(null);
      loadData();
    } catch (err) {
      error(err.response?.data?.error || 'Failed to record payment.');
    } finally {
      setSubmitting(false);
    }
  };

  const invoiceColumns = [
    {
      header: 'Invoice Number',
      accessor: 'invoice_number',
      sortable: true,
      render: (val, row) => (
        <div>
          <span className="font-bold text-brand-700">{val}</span>
          <span className="block text-[11px] text-slate-500 font-medium">{row.policy_number}</span>
        </div>
      ),
    },
    {
      header: 'Billed Client',
      accessor: 'group_name',
      sortable: true,
      render: (val) => <span className="font-bold text-slate-800 text-xs">{val}</span>,
    },
    {
      header: 'Invoice & Due Dates',
      accessor: 'invoice_date',
      render: (val, row) => (
        <div className="text-xs text-slate-600">
          <span>Inv: {val}</span>
          <span className="block text-[11px] text-slate-400 font-medium">Due: {row.due_date}</span>
        </div>
      ),
    },
    {
      header: 'Invoice Total',
      accessor: 'total_amount',
      sortable: true,
      render: (val, row) => (
        <div className="text-xs">
          <span className="font-bold text-slate-800">₹{Number(val).toLocaleString('en-IN')}</span>
          <span className="block text-[10px] text-slate-400">GST: ₹{Number(row.tax_amount).toLocaleString('en-IN')}</span>
        </div>
      ),
    },
    {
      header: 'Paid & Balance',
      accessor: 'balance_due',
      render: (val, row) => (
        <div className="text-xs">
          <span className={`font-bold ${parseFloat(val) > 0 ? 'text-rose-600' : 'text-emerald-600'}`}>
            Due: ₹{Number(val).toLocaleString('en-IN')}
          </span>
          <span className="block text-[10px] text-slate-400">Paid: ₹{Number(row.paid_amount).toLocaleString('en-IN')}</span>
        </div>
      ),
    },
    {
      header: 'Status',
      accessor: 'status',
      render: (val) => <Badge status={val} />,
    },
    {
      header: 'Actions',
      accessor: 'id',
      render: (val, row) => (
        <div className="flex items-center gap-1.5">
          <a
            href={billingService.downloadInvoicePdfUrl(val)}
            target="_blank"
            rel="noreferrer"
            className="p-1.5 rounded-lg border border-brand-200 bg-brand-50 hover:bg-brand-100 text-brand-700 transition-colors"
            title="Download Tax Invoice (PDF)"
          >
            <Download className="w-3.5 h-3.5" />
          </a>

          {parseFloat(row.balance_due) > 0 && canPay && (
            <button
              onClick={() => handleOpenPayment(row)}
              className="px-2.5 py-1 text-xs font-bold text-emerald-700 bg-emerald-50 hover:bg-emerald-100 border border-emerald-200 rounded-lg flex items-center gap-1"
            >
              <CreditCard className="w-3.5 h-3.5" /> Pay
            </button>
          )}
        </div>
      ),
    },
  ];

  const paymentColumns = [
    {
      header: 'Payment Ref',
      accessor: 'payment_reference',
      render: (val) => <span className="font-bold text-brand-700 text-xs">{val}</span>,
    },
    {
      header: 'Receipt & UTR',
      accessor: 'receipt_number',
      render: (val, row) => (
        <div>
          <span className="font-semibold text-slate-800 text-xs">{val}</span>
          <p className="text-[11px] text-slate-400 font-mono mt-0.5">{row.transaction_id}</p>
        </div>
      ),
    },
    {
      header: 'Invoice Number',
      accessor: 'invoice_number',
      render: (val) => <span className="text-xs text-slate-700 font-medium">{val}</span>,
    },
    {
      header: 'Client / Payer',
      accessor: 'payer_name',
      render: (val) => <span className="font-bold text-slate-800 text-xs">{val}</span>,
    },
    {
      header: 'Amount Paid',
      accessor: 'amount',
      render: (val) => <span className="font-bold text-emerald-700 text-sm">₹{Number(val).toLocaleString('en-IN')}</span>,
    },
    {
      header: 'Channel & Date',
      accessor: 'payment_date',
      render: (val, row) => (
        <div className="text-xs text-slate-600">
          <span>{row.payment_method_display || row.payment_method}</span>
          <span className="block text-[11px] text-slate-400">{val}</span>
        </div>
      ),
    },
    {
      header: 'Status',
      accessor: 'status',
      render: (val) => <Badge status={val} />,
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-extrabold text-slate-800 tracking-tight flex items-center gap-2">
            <CreditCard className="w-6 h-6 text-brand-600" />
            Billing, Invoicing & Corporate Premium Ledger
          </h2>
          <p className="text-xs text-slate-500 mt-1">
            Automated 18% GST tax calculation, premium collection tracking, wire payment receipts, and PDF generation
          </p>
        </div>

        <button
          onClick={loadData}
          className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl border border-slate-200 bg-white hover:bg-slate-50 text-slate-700 text-xs font-bold transition-all"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Refresh Ledger</span>
        </button>
      </div>

      {/* Navigation Tabs */}
      <div className="flex border-b border-slate-200">
        <button
          onClick={() => setActiveTab('invoices')}
          className={`py-3 px-5 text-xs font-bold border-b-2 transition-all flex items-center gap-2 ${
            activeTab === 'invoices'
              ? 'border-brand-600 text-brand-600'
              : 'border-transparent text-slate-500 hover:text-slate-800'
          }`}
        >
          <FileText className="w-4 h-4" />
          <span>Corporate Tax Invoices ({invoices.length})</span>
        </button>

        <button
          onClick={() => setActiveTab('payments')}
          className={`py-3 px-5 text-xs font-bold border-b-2 transition-all flex items-center gap-2 ${
            activeTab === 'payments'
              ? 'border-brand-600 text-brand-600'
              : 'border-transparent text-slate-500 hover:text-slate-800'
          }`}
        >
          <CreditCard className="w-4 h-4" />
          <span>Payment Transactions ({payments.length})</span>
        </button>
      </div>

      {/* Active Tab View */}
      {activeTab === 'invoices' ? (
        <DataTable
          columns={invoiceColumns}
          data={invoices}
          searchKey="invoice_number"
          searchPlaceholder="Search invoice by number or group..."
          filterOptions={[
            { label: 'Unpaid Invoices', value: 'UNPAID' },
            { label: 'Partially Paid', value: 'PARTIALLY_PAID' },
            { label: 'Paid Invoices', value: 'PAID' },
            { label: 'Overdue Invoices', value: 'OVERDUE' },
          ]}
          selectedFilter={statusFilter}
          onFilterChange={setStatusFilter}
          isLoading={loading}
        />
      ) : (
        <DataTable
          columns={paymentColumns}
          data={payments}
          searchKey="payment_reference"
          searchPlaceholder="Search payment by reference or UTR..."
          isLoading={loading}
        />
      )}

      {/* Record Payment Modal */}
      {paymentModal && (
        <Modal
          isOpen={!!paymentModal}
          onClose={() => setPaymentModal(null)}
          title={`Record Wire Payment: ${paymentModal.invoice_number}`}
          subtitle={`Policy: ${paymentModal.policy_number} • Total Outstanding Balance Due: ₹${Number(paymentModal.balance_due).toLocaleString('en-IN')}`}
        >
          <form onSubmit={handleRecordPayment} className="space-y-4">
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-bold text-slate-600 mb-1">Payment Amount (INR)</label>
                <input
                  type="number"
                  step="0.01"
                  max={paymentModal.balance_due}
                  required
                  value={payForm.amount}
                  onChange={(e) => setPayForm({ ...payForm, amount: e.target.value })}
                  className="w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl font-bold text-emerald-700"
                />
              </div>
              <div>
                <label className="block text-xs font-bold text-slate-600 mb-1">Payment Channel</label>
                <select
                  value={payForm.payment_method}
                  onChange={(e) => setPayForm({ ...payForm, payment_method: e.target.value })}
                  className="w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl"
                >
                  <option value="NEFT">NEFT Transfer</option>
                  <option value="RTGS">RTGS Transfer</option>
                  <option value="BANK_TRANSFER">Direct Wire</option>
                  <option value="CORPORATE_CARD">Corporate Credit Card</option>
                  <option value="CHEQUE">Corporate Cheque</option>
                  <option value="UPI">Corporate UPI</option>
                </select>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-bold text-slate-600 mb-1">Bank UTR / Transaction ID</label>
                <input
                  type="text"
                  required
                  value={payForm.transaction_id}
                  onChange={(e) => setPayForm({ ...payForm, transaction_id: e.target.value })}
                  className="w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl font-mono"
                />
              </div>
              <div>
                <label className="block text-xs font-bold text-slate-600 mb-1">Payer Entity Name</label>
                <input
                  type="text"
                  required
                  value={payForm.payer_name}
                  onChange={(e) => setPayForm({ ...payForm, payer_name: e.target.value })}
                  className="w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-600 mb-1">Payment Notes</label>
              <textarea
                rows="2"
                value={payForm.notes}
                onChange={(e) => setPayForm({ ...payForm, notes: e.target.value })}
                className="w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl"
              />
            </div>

            <div className="p-3 bg-brand-50 rounded-xl border border-brand-200 text-xs text-brand-900">
              <b>Broker Commission Automation:</b> Recording this payment will automatically credit the licensed intermediary's earned commission balance.
            </div>

            <div className="flex items-center justify-end gap-3 pt-4 border-t border-slate-100">
              <button
                type="button"
                onClick={() => setPaymentModal(null)}
                className="px-4 py-2 text-sm font-semibold text-slate-600 hover:bg-slate-100 rounded-xl"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={submitting}
                className="px-5 py-2 text-sm font-bold text-white bg-emerald-600 hover:bg-emerald-700 rounded-xl shadow-md transition-all disabled:opacity-50"
              >
                {submitting ? 'Recording...' : 'Confirm Payment'}
              </button>
            </div>
          </form>
        </Modal>
      )}
    </div>
  );
};
