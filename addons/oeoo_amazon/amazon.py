from openerp.osv import osv, fields

class sales_channel_instance(osv.osv):
    _inherit = 'sales.channel.instance'
    _columns = {
        'aws_access_key_id' : fields.char('Access Key',size=64),
        'aws_secret_access_key' : fields.char('Secret Key',size=64),
        'aws_market_place_id' : fields.char('Market Place ID',size=64),
        'aws_merchant_id' : fields.char('Merchant ID',size=64),
        'site': fields.selection([
                                ('mws.amazonservices.at','Austrian FlagAustria'),
                                ('mws.amazonservices.ca','Canada'),
                                ('mws.amazonservices.cn','China'),
                                ('mws.amazonservices.fr','France'),
                                ('mws.amazonservices.de','Germany'),
                                ('mws.amazonservices.it','Italy'),
                                ('mws.amazonservices.co.jp','Japan'),
                                ('mws.amazonservices.es','Spain'),
                                ('mws.amazonservices.co.uk','United Kingdom'),
                                ('mws.amazonservices.com','United States')
                                    ],'Site'),
        'is_fba':fields.boolean('Is Fba?')
    } 
    
    def create_stores(self, cr, uid, ids, context):
        sale_obj = self.pool.get('sale.shop')
        data_create_store=self.browse(cr,uid,ids[0])
        print "data create store",data_create_store.aws_merchant_id
        instance_obj = self.browse(cr, uid, ids[0])
        res = super(sales_channel_instance,self).create_stores(cr, uid, ids, context)
        if instance_obj.module_id == 'oeoo_amazon':
            sale_obj.write(cr, uid, res, {'amazon_shop': True})
        if data_create_store.is_fba:
            self.create_fba_store(cr,uid,ids,context)
        return res
            
            
    def create_fba_store(self, cr, uid, ids, context):
        """ For create store of Sales Channel """
        (instances,) = self.browse(cr, uid, ids, context)  
        shop_obj = self.pool.get('sale.shop')
        shop_ids = shop_obj.search(cr,uid,[('instance_id','=',ids[0]),('amazon_fba_shop','=',True)])
        payment_ids = self.pool.get('account.payment.term').search(cr,uid,[])
        stock_location_obj=self.pool.get('stock.location')
     
                
        if not shop_ids:
            fba_location_id = False
            id_stock_loc=stock_location_obj.search(cr,uid,[('name','=','Stock')])
            print "iodisadasdasdsadasdasdasdsadas",id_stock_loc
            if id_stock_loc:
                loc_vals = {
                    'name':'FBA Location',
                    'location_id':id_stock_loc[0],
                    'active': True,
                    'usage': 'internal',
                    'chained_location_type': 'none',
                    'chained_auto_packing': 'manual',
                }
                fba_location_id = stock_location_obj.create(cr, uid, loc_vals)
            shop_data = {
                        'sale_channel_shop': True,
                        'amazon_fba_shop': True,
                        'name': instances.name + ' FBA Shop',
                        'payment_default_id':payment_ids[0],
                        'warehouse_id':1,
                        'instance_id':ids[0],
                        'order_policy':'prepaid',
                        'fba_location':fba_location_id,
                        'amazon_shop': True
                        
            }
            shop_id = shop_obj.create(cr,uid,shop_data)
        else:
            shop_id = shop_ids[0]
        return shop_id
sales_channel_instance()
