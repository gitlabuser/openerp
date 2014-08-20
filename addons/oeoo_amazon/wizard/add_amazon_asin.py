from osv import fields, osv
from tools.translate import _ 

class add_amazon_asin(osv.osv_memory):
    _name = "add.amazon.asin"
    _description = "Add Amazon ASIN"

    def onchange_type(self, cr, uid, ids, value):
        shop_data = self.pool.get('sale.shop').browse(cr,uid,value)
        res = {'value': {'fulfillment_channel': 'DEFAULT',}}
        if shop_data.amazon_fba_shop:
            res =  {'value': {'fulfillment_channel': 'AMAZON_NA',}}
            
        return res

    def add_amazon_asin_action(self, cr, uid, ids, context=None):
        if context.get('active_id',False):
            (data_asin,) = self.browse(cr, uid, ids, context=context)
            stock_id = self.pool.get('amazon.stock.sync').create(cr,uid,{'shop_id':data_asin.shop_id.id})
            asin_vals = {
                'name' : data_asin.name,
                'sku' : data_asin.sku,
                'listing_name' : data_asin.listing_name,
#                'price' : data_asin.price,
                'fulfillment_channel' : 'AMAZON_NA' if data_asin.shop_id.amazon_fba_shop else 'DEFAULT',
                'shop_id' : data_asin.shop_id.id,
                'product_id' : context['active_id'],
                'stock_sync_id' : stock_id,
                'active_amazon' : True,
#                'created_date' : data_asin.created_date,
            }

            self.pool.get('amazon.product.listing').create(cr,uid,asin_vals,context)
            return {'type': 'ir.actions.act_window_close'}
        
        return True
        
        
    _columns = {
        'name': fields.char('ASIN', size=16, required=True),
        'sku': fields.char('SKU', size=100 ,required=True),
        'listing_name': fields.char('Name', size=100),
        'price': fields.float('Price'),
        'fulfillment_channel': fields.selection([('AMAZON_NA', 'FBA'), ('DEFAULT', 'Default')], 'Fufillment Channel',readonly=True),
        'product_id': fields.many2one('product.product','Product'),
        'shop_id': fields.many2one('sale.shop','Shop',domain=['|',('amazon_shop','=',True),('amazon_fba_shop','=',True)],required=True),
        'created_date': fields.datetime('Created Date')
    }
   
add_amazon_asin()
