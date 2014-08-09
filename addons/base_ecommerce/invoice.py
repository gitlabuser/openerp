from osv import fields, osv
import time
import netsvc
from tools.translate import _

class account_invoice(osv.osv):
    _inherit = "account.invoice"

    def invoice_pay_customer(self, cr, uid, ids, context=None):
        if context is None:
            context={}
        wf_service = netsvc.LocalService("workflow")
        accountinvoice_link = self.browse(cr,uid,ids[0])
        saleorder_obj = self.pool.get('sale.order')
        journal_obj = self.pool.get('account.journal')
        currentTime = time.strftime("%Y-%m-%d")
        if accountinvoice_link.type == 'out_invoice':
            cr.execute("SELECT invoice_id, order_id FROM sale_order_invoice_rel WHERE invoice_id =%d" % (ids[0],))
            saleorder_res = dict(cr.fetchall())
            print "============>",saleorder_res
            saleorder_id = saleorder_res[ids[0]]
            saleorder_link = saleorder_obj.browse(cr,uid,saleorder_id)
            period_id = self.pool.get('account.period').search(cr,uid,[('date_start','<=',currentTime),('date_stop','>=',currentTime),('company_id','=',saleorder_link.company_id.id)])
            if not period_id:
                raise osv.except_osv(_('Error !'), _('Period is not defined.'))
            else:
                period_id = period_id[0]
            context['type'] = 'out_invoice'
            journal_ids = journal_obj.search(cr, uid, [('type','=','bank')])
            if journal_ids:
                journal_id= journal_ids[0]
            else:
                journal_id = self._get_journal(cr,uid,context)
            journal =journal_obj.browse(cr,uid,journal_id)
            acc_id = journal.default_credit_account_id and journal.default_credit_account_id.id or False
            if not acc_id:
                raise wizard.except_wizard(_('Error !'), _('Your journal must have a default credit and debit account.'))

            paid = True
            currency_id = self._get_currency(cr, uid, context)
            context['currency_id'] = currency_id
            voucher_id = saleorder_obj.generate_payment_with_journal(cr, uid, journal_id, saleorder_link.partner_id.id, saleorder_link.amount_total, accountinvoice_link.reference, accountinvoice_link.origin, currentTime, paid, context)
            print "voucher_id:*************************** ",voucher_id
            self.pay_and_reconcile(cr, uid, [ids[0]], saleorder_link.amount_total, acc_id, period_id, journal_id, False, period_id, False)

            wf_service.trg_write(uid, 'account.invoice', ids[0], cr)
            wf_service.trg_write(uid, 'sale.order', saleorder_id, cr)
        
        self.pool.get('account.voucher').action_move_line_create(cr, uid, [voucher_id], context)
        cr.commit()
        return True


#    def confirm_paid(self, cr, uid, ids, context=None):
#        res = super(account_invoice, self).confirm_paid(cr, uid, ids, context=None)
#        type_chk = self.browse(cr,uid,ids[0]).type
#        if type_chk == 'out_invoice':
#            cr.execute("SELECT invoice_id, order_id FROM sale_order_invoice_rel WHERE invoice_id =%d" % (ids[0],))
#            saleorder_res = dict(cr.fetchall())
#            saleorder_id = saleorder_res[ids[0]]
#            saleorder_obj = self.pool.get('sale.order')
#            order_policy = saleorder_obj.browse(cr,uid,saleorder_id).order_policy
#            if order_policy == 'prepaid':
#                saleorder_obj.write(cr,uid,saleorder_id,{'state':'progress'})
#            else:
#                saleorder_obj.write(cr,uid,saleorder_id,{'state':'done'})
#                picking_ids = saleorder_obj.browse(cr,uid,saleorder_id).picking_ids
#                for picking_id in picking_ids:
#                    self.pool.get('stock.picking').write(cr,uid,picking_id.id,{'invoice_state':'invoiced'})
#        return res

account_invoice()