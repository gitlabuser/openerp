from osv import osv, fields
from tools.translate import _
from openerp import netsvc

class amazon_shipping(osv.osv):
    
    _name='amazon.shipping'
    
    def _get_total_quantity(self, cr, uid, ids, name, arg, context=None):
        if context is None:
            context = {}
        print'ids',ids
        res = {}
        qty = 0
        for amazon_shipping_data in self.browse(cr, uid, ids, context=context):
            res[amazon_shipping_data.id]=qty
            if amazon_shipping_data.shipping_product_ids:
                for shipping_qtys in amazon_shipping_data.shipping_product_ids:
                    if shipping_qtys.qty:
                        qty += shipping_qtys.qty
                        
                res[amazon_shipping_data.id] = qty
        return res
    def Get_Fulfilment_Center (self, cr, uid, ids, context=None):
        results = self.CreateInboundShipmentPlan_Api(cr, uid, ids, context)
#        print'results',results
        data = ''
        for each_results in results:
            for each_response in each_results:
                data += "----Centre ID:-'"+each_response['CenterId']+"', City:-'"+each_response['City']+"'\n"
                for Item in each_response['Items']:
                    data += ",  SKU:- '"+Item['SellerSKU']+"'"
                    data += ",  Quantity:- '"+Item['Quantity']+"'"
                data += '\n-------'
#        print 'data------------',data
        raise osv.except_osv(_('Response!'),data)
        return True
    
    def CreateInboundShipmentPlan (self, cr, uid, ids,po_id, context=None):
        results = self.CreateInboundShipmentPlan_Api(cr, uid, ids, context)
        print'results',results
        po_ids_list =[]
        for each_results in results:
            for each_response in each_results:
                if len(results) == 1:
                    dest_address_id = self.create_dest_address(cr,uid,each_response)
                    update_vals = {
                                'plan_shipment_id':each_response['ShipmentId'],
                                'fulfillment_centre_id':each_response['CenterId'],
                                'dest_address_id':dest_address_id, 
                                }
                    self.write(cr,uid,ids[0],update_vals)
                    po_ids_list.append(ids[0])
                else:
                    id = self.po_create(cr,uid,ids[0],each_response)
                    po_ids_list.append(id)
                    
        wf_service = netsvc.LocalService("workflow")
        if len(results) > 1:
            wf_service.trg_validate(uid, 'purchase.order', ids[0], 'purchase_cancel', cr)
        cr.commit()
        if po_id:
            return po_ids_list
        else:
            return True
        
    def ConfirmInboundshipment (self, cr, uid, ids, context=None):
        results = self.ConfirmInboundshipment_Api(cr, uid, ids, context)
        print'results',results
        if results.get('ShipmentId',False):
            update_vals = {
                            'inbound_shipment_id':results['ShipmentId'],
                            'origin':results['ShipmentId'],
                            'partner_ref':results['ShipmentId'],
                          }
            self.write(cr,uid,ids[0],update_vals, context)
        return True
    
    def CreateInboundShipmentPlan_and_Confirm (self, cr, uid, ids, context=None):
        po_ids = self.CreateInboundShipmentPlan(cr, uid, ids,True, context)
        for po_id in po_ids:
            self.ConfirmInboundshipment(cr, uid, [po_id], context)
        return True
    
    def CreateInboundShipmentPlan_Api(self, cr, uid, ids, context=None):
        url_params = {}
        url_header = {}
        res_object=self.pool.get('res.partner')
        amazon_api_obj = self.pool.get('amazonerp.osv')
        
        shop_ids =self.pool.get('sales.channel.instance').search(cr,uid,[('module_id','=','oeoo_amazon')])
        shopdata =self.pool.get('sales.channel.instance').browse(cr,uid,shop_ids[0])
        # CreateInboundShipmentPlan------------
        print "shop data ",shopdata
        for amazon_shipping_data in self.browse(cr, uid, ids, context=context):

            if not shopdata.partner_id:
                raise osv.except_osv(_('Error !'),_('Shop Address Mandatory'))

            if not len(amazon_shipping_data.shipping_product_ids):
                raise osv.except_osv(_('Error !'),_('atleast one product should be shipped'))
            
            url_header['ShipFromAddress.Name'] = amazon_shipping_data.partner_id.name.strip()
            
            if not shopdata.partner_id.street:
                raise osv.except_osv(_('Error !'),_('AddressLine1 is mandatory for Supplier.'))
            elif not shopdata.partner_id.country_id.name:
                raise osv.except_osv(_('Error !'),_('Country is mandatory for Supplier.'))
            elif not shopdata.partner_id.city:
                raise osv.except_osv(_('Error !'),_('City is mandatory for Supplier.'))
            elif not shopdata.partner_id.state_id.code:
                raise osv.except_osv(_('Error !'),_('State is mandatory for Supplier.'))
            elif not shopdata.partner_id.zip:
                raise osv.except_osv(_('Error !'),_('Zip is mandatory for Supplier.'))

            url_header['LabelPrepPreference'] = 'SELLER_LABEL'
            url_header['ShipFromAddress.AddressLine1'] = shopdata.partner_id.street.strip()
            url_header['ShipFromAddress.City'] = shopdata.partner_id.city.strip()
            url_header['ShipFromAddress.StateOrProvinceCode'] = shopdata.partner_id.state_id.code.strip()
            url_header['ShipFromAddress.PostalCode'] = shopdata.partner_id.zip.strip()
            url_header['ShipFromAddress.CountryCode'] = shopdata.partner_id.country_id.code.strip()

            if not shopdata.partner_id.street2:
                url_header['ShipFromAddress.AddressLine2'] = 'jdag'
            else:
                url_header['ShipFromAddress.AddressLine2'] = 'fagd'

            url_params.update(url_header)
            count = 1
            for shipping_product_data in amazon_shipping_data.shipping_product_ids:
                if shipping_product_data.product_id.type != 'service':
                    if not shipping_product_data.product_id.default_code:
                        raise osv.except_osv(_('Error !'),_('Internal Reference Not Found for. %s'%shipping_product_data.product_id.name))
#                    if not shipping_product_data.product_id.asin:
#                        raise osv.except_osv(_('Error !'),_('ASIN Not Found for. %s'%product_data.name))
                    url_params['InboundShipmentPlanRequestItems.member.'+str(int(count))+'.SellerSKU'] = str(shipping_product_data.product_id.default_code.strip())
                    url_params['InboundShipmentPlanRequestItems.member.'+str(int(count))+'.Quantity'] = int(shipping_product_data.qty)
                    count += 1
            print'url_params',url_params
            results = amazon_api_obj.call(shopdata, 'CreateInboundShipmentPlan',url_params)
            print'results----',results
            return results
    
    def ConfirmInboundshipment_Api(self, cr, uid, ids, context=None):
#        shop_ids =self.pool.get('amazon.shop').search(cr,uid,[])
#        shopdata =self.pool.get('amazon.shop').browse(cr,uid,shop_ids[0])
        # CreateInboundShipment-------------
        shop_ids =self.pool.get('sales.channel.instance').search(cr,uid,[('module_id','=','oeoo_amazon')])
        shopdata =self.pool.get('sales.channel.instance').browse(cr,uid,shop_ids[0])
        amazon_api_obj = self.pool.get('amazonerp.osv')
#        wf_service = netsvc.LocalService("workflow")
        url_params={}
        url_header = {}
        
        
        for amazon_shipping_data in self.browse(cr, uid, ids, context=context):
            if not amazon_shipping_data.partner_id:
                raise osv.except_osv(_('Error !'),_('Plan Shipment ID Not Created for Amazon Shipment.  %s'%amazon_shipping_data.name))
            url_header['InboundShipmentHeader.ShipFromAddress.Name'] = amazon_shipping_data.partner_id.name.strip()
            url_header['InboundShipmentHeader.ShipmentName'] = amazon_shipping_data.name.strip()
            url_header['InboundShipmentHeader.LabelPrepPreference'] = 'SELLER_LABEL'
            url_header['InboundShipmentHeader.ShipmentStatus'] = 'WORKING'
            url_header['InboundShipmentHeader.ShipFromAddress.AddressLine1'] = amazon_shipping_data.partner_id.street.strip()
            url_header['InboundShipmentHeader.ShipFromAddress.City'] = amazon_shipping_data.partner_id.city.strip()
            url_header['InboundShipmentHeader.ShipFromAddress.StateOrProvinceCode'] = amazon_shipping_data.partner_id.state_id.code.strip()
            url_header['InboundShipmentHeader.ShipFromAddress.PostalCode'] = amazon_shipping_data.partner_id.zip.strip()
            url_header['InboundShipmentHeader.ShipFromAddress.CountryCode'] = amazon_shipping_data.partner_id.country_id.code.strip()
            if not amazon_shipping_data.partner_id.street2:
                url_header['InboundShipmentHeader.ShipFromAddress.AddressLine2'] = ''
            else:
                url_header['InboundShipmentHeader.ShipFromAddress.AddressLine2'] = amazon_shipping_data.partner_id.street2.strip()
            
#            url_header['ShipmentId'] =amazon_shipping_data.partner_id.plan_shipment_id.strip()
#            url_header['InboundShipmentHeader.DestinationFulfillmentCenterId'] = amazon_shipping_data.partner_id.fulfillment_centre_id
            url_params.update(url_header)
            count = 1
            for line in amazon_shipping_data.shipping_product_ids:
                if line.product_id.type != 'service':
                    if not line.product_id.default_code:
                        raise osv.except_osv(_('Error !'),_('SKU No. Not Found for. %s'%line.product_id.name))
#                    if not line.product_id.asin:
#                        raise osv.except_osv(_('Error !'),_('ASIN Not Found for. %s'%line.product_id.name))
                    
                    url_params['InboundShipmentItems.member.'+str(int(count))+'.SellerSKU'] = line.product_id.default_code.strip()
                    url_params['InboundShipmentItems.member.'+str(int(count))+'.Quantity'] = int(line.qty)
                    count += 1
            print'url_params=======',url_params
            results = amazon_api_obj.call(shopdata, 'CreateInboundShipment',url_params)
            print'results========------',results
        return results
    
    _columns={
        'name':fields.char('Name',size=32),
        'partner_id':fields.many2one('res.partner','Partner'),
        'shipping_product_ids':fields.one2many('amazon.shipping.product','amazon_shipping_id','Shipping Product'),
        'inbound_shipment_id': fields.char('Inbound Shipment ID', size=256),
        'plan_shipment_id': fields.char('Plan Shipment ID', size=256),
        'fulfillment_centre_id': fields.char('Fulfilment Centre ID', size=256),
        'total_qty': fields.function(_get_total_quantity, method=True, type='integer', string='Total Quantity'),
    }
amazon_shipping()

class amazon_shipping_product(osv.osv):
    
    _name='amazon.shipping.product'
    _columns={
        
        'product_id':fields.many2one('product.product','Product'),
        'qty':fields.integer('quantity'),
        'amazon_shipping_id':fields.many2one('amazon.shipping','Shipping Product'),
    }
    
amazon_shipping_product()