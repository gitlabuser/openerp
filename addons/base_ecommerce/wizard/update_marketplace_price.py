from openerp.osv import fields, osv
from openerp.tools.translate import _

class update_marketplace_price(osv.osv):
    _name='update.marketplace.price'
    _columns={
      'name':fields.char('Name',size=64),
             }
    def update_price(self,cr,uid,ids,context=None):
        print "=====context==========>",context.get('active_ids', False)
        return True
    def update_stock(self,cr,uid,ids,context=None):
        return True
    def update_stock_price(self,cr,uid,ids,context=None):
        return True
update_marketplace_price()
    