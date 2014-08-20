from osv import osv, fields
class update_marketplace_price(osv.osv):
    _name='update.marketplace.price'
    _inherit='update.marketplace.price'
    _columns={
        'on_amazon':fields.boolean('On Amazon'),
        'amazon_shop_id': fields.many2one('sale.shop','Shop Name',domain=[('amazon_shop','=',True)]),
    }
    
    def update_price(self,cr,uid,ids,context):
        shop_obj = self.pool.get('sale.shop')
        prod_obj = self.pool.get('product.product')
        (data,) = self.browse(cr,uid,ids)
        if data.on_amazon:
            shop = data.amazon_shop_id.id
            listing_ids = []
            for prod in prod_obj.browse(cr, uid, context.get('active_ids', False)):
                for listing in prod.amazon_listing_ids:
                    if listing.id not in listing_ids:
                        listing_ids.append(listing.id)
            context.update({'listing_ids': listing_ids})
            shop_obj.export_amazon_price(cr,uid, [shop], context)
        else:
            super(update_marketplace_price,self).update_price(cr,uid,ids,context)
        return True
    
    def update_stock(self,cr,uid,ids,context=None):
        shop_obj = self.pool.get('sale.shop')
        prod_obj = self.pool.get('product.product')
        (data,) = self.browse(cr,uid,ids)
        if data.on_amazon:
            shop = data.amazon_shop_id.id
            listing_ids = []
            for prod in prod_obj.browse(cr, uid, context.get('active_ids', False)):
                for listing in prod.amazon_listing_ids:
                    if listing.id not in listing_ids:
                        listing_ids.append(listing.id)
            context.update({'listing_ids': listing_ids})
            shop_obj.export_amazon_stock(cr,uid, [shop], context)
        else:
            super(update_marketplace_price,self).update_stock(cr,uid,ids,context)
        return True
    
    def update_stock_price(self,cr,uid,ids,context=None):
        shop_obj = self.pool.get('sale.shop')
        prod_obj = self.pool.get('product.product')
        (data,) = self.browse(cr,uid,ids)
        if data.on_amazon:
            shop = data.amazon_shop_id.id
            listing_ids = []
            for prod in prod_obj.browse(cr, uid, context.get('active_ids', False)):
                for listing in prod.amazon_listing_ids:
                    if listing.id not in listing_ids:
                        listing_ids.append(listing.id)
            context.update({'listing_ids': listing_ids})
            shop_obj.export_amazon_price(cr,uid, [shop], context)
            shop_obj.export_amazon_stock(cr,uid, [shop], context)
        else:
            super(update_marketplace_price,self).update_stock(cr,uid,ids,context)
        return True
update_marketplace_price()