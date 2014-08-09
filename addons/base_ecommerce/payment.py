from osv import osv, fields

class ecommerce_payment_method(osv.osv):
    _name = 'ecommerce.payment.method'
    _columns = {
       'name' : fields.char('Method',size=255, required=True),
       'val_order' : fields.boolean('Validate Order'),
       'pay_invoice' : fields.boolean('Pay Invoice'),
       'order_policy': fields.selection([
                ('manual', 'On Demand'),
                ('picking', 'On Delivery Order'),
                ('prepaid', 'Before Delivery'),
            ], 'Invoice On'),
        'shop_id': fields.many2one('sale.shop' ,'Shop',domain = [('sale_channel_shop', '=', True)])
    }
ecommerce_payment_method()

class payment_method(osv.osv):
    _name = 'payment.method'
    _columns = {
       'name' : fields.char('Method',size=255),
       'code': fields.char('Code',size=255)
    }
payment_method()