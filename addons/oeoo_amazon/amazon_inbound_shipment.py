from osv import osv, fields
from tools.translate import _
import binascii
from base64 import b64decode
class amazon_shipping_product1(osv.osv):
    _name='amazon.shipping.product1'

    _columns={
        'product_id':fields.many2one('product.product','Product', required=True),
        'amazon_sku': fields.many2one('amazon.product.listing','Amazon SKU'),
        'qty':fields.integer('Quantity', required=True),
        'intransit_qty': fields.integer('In Tansit'),
        'moved_qty' : fields.integer('Moved Quantity'),
        'amazon_inbound_shipping_id':fields.many2one('amazon.inbound.shipment','Shipping Product'),
    }
amazon_shipping_product1()

class fba_shipment_packaging(osv.osv):
    _name = 'fba.shipment.packaging'
    _columns = {
        'weight': fields.float('Weight(lbs)'),
        'length': fields.float('Length(in.)'),
        'width': fields.float('Width(in.)'),
        'height': fields.float('Height(in.)'),
        'package_no': fields.integer('Package / Pallet Number'),
        'is_stacked': fields.boolean('Is Stacked'),
        'fba_shipment_processing_id' : fields.many2one('amazon.inbound.shipment','FBA Shipment'),
    }
fba_shipment_packaging()

class fba_packaging_nonpartnered(osv.osv):
    _name = 'fba.shipment.packaging.nonpartnered'
    _columns = {
        'tracking_no': fields.integer('Tracking Id'),
        'package_no': fields.integer('Package Number'),
        'fba_shipment_processing_id' : fields.many2one('amazon.inbound.shipment','FBA Shipment'),
    }
fba_packaging_nonpartnered()

class amazon_inbound_shipment(osv.osv):
    _name='amazon.inbound.shipment'
    _columns={
        'name':fields.char('Name',size=32, readonly=True),
        'origin': fields.many2one('amazon.inbound.shipment','Origin', readonly=True),
        'partner_id':fields.many2one('res.partner','Destination Center', readonly=True),
        'inbound_shipment_id': fields.char('Inbound Shipment ID', size=256, readonly=True),
        'plan_shipment_id': fields.char('Plan Shipment ID', size=256, readonly=True),
        'shop_id': fields.many2one('sale.shop','Shop'),
        'shipping_product_ids':fields.one2many('amazon.shipping.product1','amazon_inbound_shipping_id','Shipping Product'),
        'shipment_type':fields.selection([('SPD','Small Parcel Delivery'),('LTL','Less Than Truckload')], 'Shipment Type',select=1),
        'spd_ltl_carrier':fields.selection([('Amazon','Amazon-Partnered Carrier (UPS)'),('Other','Other Carrier')], 'Select Carrier'),
        'packaging_ids': fields.one2many('fba.shipment.packaging','fba_shipment_processing_id'),
        'nonpartnered_packaging_ids': fields.one2many('fba.shipment.packaging.nonpartnered','fba_shipment_processing_id'),
#        'ltl_total_weight': fields.float('Total Weight'),
        'shipment_charges': fields.float('Shipment Charges',readonly=True),
        'state': fields.selection([('draft','Draft'),
                                    ('processing', 'Processing'),
                                    ('confirm','Confirm'),
                                    ('transfer','Transfer'),
#                                    ('confrim_charges', 'Confirm Charges')
                                    ('in_transit', 'In Transit'),
                                    ('done','Done'),
                                    ('cancel','Cancel'),
                                    ],'State')
    }
    _defaults = {
        'state': 'draft',
        'shipment_type': 'SPD',
        'spd_ltl_carrier': 'Amazon'
    }
    
    def ConfirmInboundshipment_Api(self, cr, uid, ids, context=None):
        # CreateInboundShipment-------------
        url_params={}
        url_header = {}
        amazon_api_obj = self.pool.get('amazonerp.osv')
        for amazon_shipping_data in self.browse(cr, uid, ids, context=context):
            shopdata = amazon_shipping_data.shop_id
            partner_address_data = shopdata.shop_address
            url_header['InboundShipmentHeader.ShipFromAddress.Name'] = shopdata.shop_address.name.strip()
            url_header['InboundShipmentHeader.ShipmentName'] = amazon_shipping_data.name.strip()
            url_header['InboundShipmentHeader.LabelPrepPreference'] = 'SELLER_LABEL'
            url_header['InboundShipmentHeader.ShipmentStatus'] = 'WORKING'
            url_header['InboundShipmentHeader.ShipFromAddress.AddressLine1'] = partner_address_data.street.strip()
            url_header['InboundShipmentHeader.ShipFromAddress.City'] = partner_address_data.city.strip()
            url_header['InboundShipmentHeader.ShipFromAddress.StateOrProvinceCode'] =  partner_address_data.state_id.code.strip()
            url_header['InboundShipmentHeader.ShipFromAddress.PostalCode'] = partner_address_data.zip.strip()
            url_header['InboundShipmentHeader.ShipFromAddress.CountryCode'] = partner_address_data.country_id.code.strip()
            if not partner_address_data.street2:
                url_header['InboundShipmentHeader.ShipFromAddress.AddressLine2'] = ''
            else:
                url_header['InboundShipmentHeader.ShipFromAddress.AddressLine2'] = partner_address_data.street2.strip()
            
            url_header['ShipmentId'] = amazon_shipping_data.plan_shipment_id.strip()
            url_header['InboundShipmentHeader.DestinationFulfillmentCenterId'] = amazon_shipping_data.partner_id.ref
            url_params.update(url_header)
            count = 1
            for line in amazon_shipping_data.shipping_product_ids:
                if line.product_id.type != 'service':
                    if not line.amazon_sku.name:
                        raise osv.except_osv(_('Error !'),_('SKU No. Not Found for. %s'%line.amazon_sku))
#                    if not line.product_id.asin:
#                        raise osv.except_osv(_('Error !'),_('ASIN Not Found for. %s'%line.product_id.name))
                    
                    url_params['InboundShipmentItems.member.'+str(int(count))+'.SellerSKU'] =  line.amazon_sku.name.strip()
                    url_params['InboundShipmentItems.member.'+str(int(count))+'.Quantity'] = int(line.qty)
                    count += 1
            print'url_params=======',url_params
            results = amazon_api_obj.call(shopdata.instance_id, 'CreateInboundShipment',url_params)
            print'results========------',results
        return results
    
    def ConfirmInboundshipment(self, cr, uid, ids, context=None):
        print "innnnnnnnnnn"
#        try:
        results = self.ConfirmInboundshipment_Api(cr, uid, ids, context)
        print'results',results
        if results:
            update_vals = {
                            'inbound_shipment_id':results,
                            'state': 'confirm'
                          }
            self.write(cr,uid,ids[0],update_vals, context)
#        except Exception, e:
#            print 
        return True
    
    def create_dest_address(self, cr, uid,vals, context=None):
        partner_obj = self.pool.get('res.partner')
        partner_ids = partner_obj.search(cr,uid,[('ref','=',vals['CenterId'])])
        if not len(partner_ids):
            country_id = self.pool.get('res.country').search(cr,uid,[('code','=',vals['CountryCode'])])
#            state_id = self.pool.get('res.country.state').search(cr,uid,[('code','=',vals['StateOrProvinceCode'])])
            partner_id = partner_obj.create(cr,uid,
                                                            {
                                                                'name':vals['AddressName'],
                                                                'ref':vals['CenterId'],
                                                                'type':'delivery',
                                                                'name':vals['AddressName'],
                                                                'street':vals['AddressLine1'],
                                                                'city':vals['City'],
#                                                                'state_id':state_id[0],
                                                                'country_id':country_id[0],
                                                                'zip':vals['PostalCode'],
                                                            }
                                                        )
        else:
            partner_id = partner_ids[0]
        return partner_id
    
    def CreateInboundShipmentPlan(self, cr, uid, ids, context={}):
        fba_shipment_processing_obj = self.pool.get('amazon.inbound.shipment')
        fba_shipment_line_obj = self.pool.get('amazon.shipping.product1')
        amazon_product_listing_obj = self.pool.get('amazon.product.listing')
        (data,) = self.browse(cr,uid,ids)
        results = self.CreateInboundShipmentPlan_Api(cr, uid, ids, context)
        print'results',results
        if results:
                if len(results) > 1:
                    for each_results in results:
                        dest_address_id = self.create_dest_address(cr,uid,each_results)
                        data_shipment = {
                            'partner_id': dest_address_id,
                            'shop_id':data.shop_id.id,
                            'plan_shipment_id':each_results['ShipmentId'],
                            'origin':data.id,
                            'state':'processing',

                        }
                        processing_id = fba_shipment_processing_obj.create(cr,uid,data_shipment)
                        for each_item in each_results['Items']:
                            amazon_listing_ids = amazon_product_listing_obj.search(cr,uid,[('name','=',each_item['SellerSKU']),('shop_id','=',data.shop_id.id)])
                            print 'amazon_listing_ids',amazon_listing_ids
                            
                            if amazon_listing_ids:
                                amazon_listing_data = amazon_product_listing_obj.browse(cr,uid,amazon_listing_ids[0])

                                line_data = {
                                    'amazon_sku': amazon_listing_data.id,
                                    'qty':each_item['Quantity'],
                                    'product_id':amazon_listing_data.product_id.id,
                                    'amazon_inbound_shipping_id': processing_id
                                }
                                print "********",fba_shipment_line_obj.create(cr,uid,line_data)
                    data.write({'state':'cancel'})
                else:
                    each_results = results[0]
                    dest_address_id = self.create_dest_address(cr,uid,each_results)
                    print "======dest_address_id=====>",dest_address_id
                    update_vals = {
                                'plan_shipment_id': each_results['ShipmentId'],
                                'partner_id': dest_address_id,
                                'state': 'processing'
                                }
                    self.write(cr,uid,ids[0],update_vals)
#        for each_results in results:
#            if len(results) == 1:
#                dest_address_id = self.create_dest_address(cr,uid,each_results)
#                print "======dest_address_id=====>",dest_address_id
#                update_vals = {
#                            'plan_shipment_id':each_results['ShipmentId'],
#                            'partner_id':dest_address_id,
#                            'state': 'processing'
#                            }
#                self.write(cr,uid,ids[0],update_vals)
        return True
    
    def CreateInboundShipmentPlan_Api(self, cr, uid, ids, context=None):
        url_params = {}
        url_header = {}
        amazon_api_obj = self.pool.get('amazonerp.osv')
        
        # CreateInboundShipmentPlan------------
        for amazon_shipping_data in self.browse(cr, uid, ids, context=context):
            shopdata = amazon_shipping_data.shop_id
            if not amazon_shipping_data.shop_id.shop_address:
                raise osv.except_osv(_('Error !'),_('You can not confirm purchase order without selecting partner'))
            if not len(amazon_shipping_data.shipping_product_ids):
                raise osv.except_osv(_('Error !'),_('atleast one product should be shipped'))
            url_header['ShipFromAddress.Name'] = amazon_shipping_data.shop_id.shop_address.name.strip()
            
            if not amazon_shipping_data.shop_id.shop_address.street:
                raise osv.except_osv(_('Error !'),_('AddressLine1 is mandatory for Supplier.'))
            elif not amazon_shipping_data.shop_id.shop_address.country_id.code:
                raise osv.except_osv(_('Error !'),_('Country is mandatory for Supplier.'))
            elif not amazon_shipping_data.shop_id.shop_address.city:
                raise osv.except_osv(_('Error !'),_('City is mandatory for Supplier.'))
            elif not amazon_shipping_data.shop_id.shop_address.state_id.code:
                raise osv.except_osv(_('Error !'),_('State is mandatory for Supplier.'))
            elif not amazon_shipping_data.shop_id.shop_address.zip:
                raise osv.except_osv(_('Error !'),_('Zip is mandatory for Supplier.'))

            url_header['LabelPrepPreference'] = 'SELLER_LABEL'
            url_header['ShipFromAddress.AddressLine1'] = (amazon_shipping_data.shop_id.shop_address.street).strip()
            url_header['ShipFromAddress.City'] = (amazon_shipping_data.shop_id.shop_address.city).strip()
            url_header['ShipFromAddress.StateOrProvinceCode'] = (amazon_shipping_data.shop_id.shop_address.state_id.code).strip()
            url_header['ShipFromAddress.PostalCode'] = (amazon_shipping_data.shop_id.shop_address.zip).strip()
            url_header['ShipFromAddress.CountryCode'] = (amazon_shipping_data.shop_id.shop_address.country_id.code).strip()
            url_header['SellerId'] = shopdata.instance_id.aws_merchant_id
            if not amazon_shipping_data.shop_id.shop_address.street2:
                url_header['ShipFromAddress.AddressLine2'] = ''
            else:
                url_header['ShipFromAddress.AddressLine2'] = (amazon_shipping_data.shop_id.shop_address.street2).strip()
            url_params.update(url_header)
            count = 1
            for shipping_product_data in amazon_shipping_data.shipping_product_ids:
                if shipping_product_data.product_id.type != 'service':
                    if not shipping_product_data.amazon_sku.name:
                        raise osv.except_osv(_('Error !'),_('Internal Reference Not Found for. %s'%shipping_product_data.amazon_sku.name))
                    url_params['InboundShipmentPlanRequestItems.member.'+str(int(count))+'.SellerSKU'] = str(shipping_product_data.amazon_sku.name.strip())
                    url_params['InboundShipmentPlanRequestItems.member.'+str(int(count))+'.Quantity'] = int(shipping_product_data.qty)
                    count += 1
            print'url_params',url_params
            results = amazon_api_obj.call(shopdata.instance_id, 'CreateInboundShipmentPlan',url_params)
            print'results----',results
            return results
    
    def action_put_transport_content(self, cr, uid, ids, context=None):
        amazon_api_obj = self.pool.get('amazonerp.osv')
        (fba_data,) = self.browse(cr,uid,ids)
        url_params = {}
        if fba_data.shop_id and fba_data.inbound_shipment_id:
            instance_data = fba_data.shop_id.instance_id
            url_params['ShipmentId'] = fba_data.inbound_shipment_id

            if not fba_data.shipment_type:
                raise osv.except_osv(_('Error !'), _('Please Select Shipping Type From Carrier Details Tab.'))

            if not fba_data.spd_ltl_carrier:
                raise osv.except_osv(_('Error !'), _('Please Select Carrier From Carrier Details Tab.'))

#            if not fba_data.sp_ltl_carrier_name and fba_data.spd_ltl_carrier == 'Other':
#                raise osv.except_osv(_('Error !'), _('Please Select Carrier From Carrier Details Tab.'))


            if fba_data.shipment_type == 'SPD':
                url_params['ShipmentType'] = 'SP'
                if fba_data.spd_ltl_carrier == 'Amazon':
                    url_params['IsPartnered'] = 'true'

                    if not len(fba_data.packaging_ids):
                        raise osv.except_osv(_('Error !'), _('Please add Package For SPD.'))

                    count = 1
                    for packaging in fba_data.packaging_ids:
                        # TransportDetails.PartneredSmallParcelData.PackageList
                        url_params['TransportDetails.PartneredSmallParcelData.PackageList.member.'+str(count)+'.PackageNumber'] = int(packaging.package_no)
                        url_params['TransportDetails.PartneredSmallParcelData.PackageList.member.'+str(count)+'.Weight.Value'] = float(packaging.weight)
                        url_params['TransportDetails.PartneredSmallParcelData.PackageList.member.'+str(count)+'.Weight.Unit'] = 'pounds'
                        url_params['TransportDetails.PartneredSmallParcelData.PackageList.member.'+str(count)+'.Dimensions.Length'] = float(packaging.length)
                        url_params['TransportDetails.PartneredSmallParcelData.PackageList.member.'+str(count)+'.Dimensions.Width'] = float(packaging.width)
                        url_params['TransportDetails.PartneredSmallParcelData.PackageList.member.'+str(count)+'.Dimensions.Height'] = float(packaging.height)
                        url_params['TransportDetails.PartneredSmallParcelData.PackageList.member.'+str(count)+'.Dimensions.Unit'] = 'inches'
                        count += 1
                else:
                    url_params['IsPartnered'] = 'false'
                    # TransportDetails.NonPartneredSmallParcelData
#                    url_params['TransportDetails.NonPartneredSmallParcelData.CarrierName']= fba_data.sp_ltl_carrier_name

                    if not len(fba_data.nonpartnered_packaging_ids):
                        raise osv.except_osv(_('Error !'), _('Please add Package For NonPartnered SPD.'))

                    for nonpackaging in fba_data.nonpartnered_packaging_ids:
                        count = 1
                        # TransportDetails.NonPartneredSmallParcelData.PackageList
                        url_params['TransportDetails.NonPartneredSmallParcelData.PackageList.member.'+str(count)+'.PackageNumber'] = nonpackaging.package_no
                        url_params['TransportDetails.NonPartneredSmallParcelData.PackageList.member.'+str(count)+'.TrackingId'] = nonpackaging.tracking_no
                        count += 1

            else:
                url_params['ShipmentType'] = fba_data.shipment_type
                if fba_data.spd_ltl_carrier == 'Amazon':
                    url_params['IsPartnered'] = 'true'
                    if not len(fba_data.packaging_ids):
                        raise osv.except_osv(_('Error !'), _('Please add Package For LTL.'))

                    count = 1
                    for packaging in fba_data.packaging_ids:
                        # TransportDetails.PartneredLtlData.PalletList
                        url_params['TransportDetails.PartneredLtlData.PalletList.member.'+str(count)+'.PalletNumber'] = int(packaging.package_no)
                        url_params['TransportDetails.PartneredLtlData.PalletList.member.'+str(count)+'.Dimensions.Length'] = float(packaging.length)
                        url_params['TransportDetails.PartneredLtlData.PalletList.member.'+str(count)+'.Dimensions.Width'] = float(packaging.width)
                        url_params['TransportDetails.PartneredLtlData.PalletList.member.'+str(count)+'.Dimensions.Height'] = float(packaging.height)
                        url_params['TransportDetails.PartneredLtlData.PalletList.member.'+str(count)+'.Dimensions.Unit'] = 'inches'
                        url_params['TransportDetails.PartneredLtlData.PalletList.member.'+str(count)+'.Weight.Value'] = float(packaging.weight)
                        url_params['TransportDetails.PartneredLtlData.PalletList.member.'+str(count)+'.Weight.Unit'] = 'pounds'
                        url_params['TransportDetails.PartneredLtlData.PalletList.member.'+str(count)+'.IsStacked'] = 'true' if packaging.is_stacked else 'false'
                        count += 1

                    if not fba_data.ltl_total_weight:
                        raise osv.except_osv(_('Error !'), _('Please Select Total Weight-LTL Partnered From Carrier Details Tab.'))
                    if not fba_data.seller_declared_value:
                        raise osv.except_osv(_('Error !'), _('Please Select Seller Declared Value-LTL Partnered From Carrier Details Tab.'))
                    if not fba_data.transport_name:
                        raise osv.except_osv(_('Error !'), _('Please Select Transport Name-LTL Partnered From Carrier Details Tab.'))

                    url_params['TransportDetails.PartneredLtlData.TotalWeight.Value']= float(fba_data.ltl_total_weight)
                    url_params['TransportDetails.PartneredLtlData.TotalWeight.Unit']= 'pounds'
                    url_params['TransportDetails.PartneredLtlData.SellerDeclaredValue.Value']= float(fba_data.seller_declared_value) or 0.00
                    url_params['TransportDetails.PartneredLtlData.SellerDeclaredValue.CurrencyCode']= 'USD'
                    # TransportDetails.PartneredLtlData
                    url_params['TransportDetails.PartneredLtlData.Contact.Name']= fba_data.transport_name
                    url_params['TransportDetails.PartneredLtlData.Contact.Phone']= fba_data.transport_phone
                    url_params['TransportDetails.PartneredLtlData.Contact.Email']= fba_data.transport_email
                    url_params['TransportDetails.PartneredLtlData.Contact.Fax']= fba_data.transport_fax
                    url_params['TransportDetails.PartneredLtlData.Contact.BoxCount']= fba_data.transport_box
                    url_params['TransportDetails.PartneredLtlData.Contact.SellerFreightClass']= fba_data.transport_class
                    url_params['TransportDetails.PartneredLtlData.FreightReadyDate']= str(fba_data.transport_date).replace(' ','T')+'Z'
                else:
                    if not fba_data.ltl_pro_no:
                        raise osv.except_osv(_('Error !'), _('Please Enter Tracking Number-LTL Other Carrier Details.'))

                    url_params['IsPartnered'] = 'false'
                    # TransportDetails.NonPartneredLtlData
#                    url_params['TransportDetails.NonPartneredLtlData.CarrierName']= fba_data.sp_ltl_carrier_name
                    url_params['TransportDetails.NonPartneredLtlData.ProNumber']= fba_data.ltl_pro_no

        print'url_params',url_params
        result = amazon_api_obj.call(instance_data, 'PutTransportContent',url_params)
        print "=========result=====>",result
        if result == 'WORKING':
            shipment = {'ShipmentId':fba_data.inbound_shipment_id}
            if fba_data.shipment_type == 'SPD':
                result = amazon_api_obj.call(instance_data, 'EstimateTransportRequest',shipment)
                print "======result====>",result
                if result == 'ESTIMATING':
                    result = amazon_api_obj.call(instance_data, 'GetTransportContent',shipment)
                    print "====result====>",result
                    try:
                        result = float(result)
                    except:
                        result = 0.0
                        pass
                if result != 'Failed':
                    fba_data.write({'shipment_charges':result, 'state' : 'transfer'})
            else:
                result = amazon_api_obj.call(instance_data, 'GetTransportContent',shipment)
                try:
                    result = float(result)
                except:
                    result = 0.0
                    pass
                if result != 'Failed':
                    fba_data.write({'shipment_charges':result, 'state' : 'transfer'})
        return True
    
    def action_confirm_transport_content(self, cr, uid, ids, context=None):
        print "innnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnn"
        amazon_api_obj = self.pool.get('amazonerp.osv')
        (fba_data,) = self.browse(cr,uid,ids)
        if fba_data.inbound_shipment_id:
            instance_data = fba_data.shop_id.instance_id
            shipment = {'ShipmentId': fba_data.inbound_shipment_id}
            result = amazon_api_obj.call(instance_data, 'ConfirmTransportRequest',shipment)
            if result == 'CONFIRMING':
                fba_data.write({'state':'in_transit'})
        return True
    
    def action_in_transit_shipment_status(self, cr, uid, ids, context=None):
        amazon_api_obj = self.pool.get('amazonerp.osv')
        fba_shipment_processing_obj = self.pool.get('amazon.inbound.shipment')
        fba_shipment_processing_line_obj = self.pool.get('amazon.shipping.product1')
#        amazon_listing = self.pool.get('amazon.product.listing')


        for each_shipment in fba_shipment_processing_obj.browse(cr,uid,ids):
            if not each_shipment.inbound_shipment_id:
                continue

            if not each_shipment.shop_id.shop_address:
                raise osv.except_osv(_('Error !'), _('Please Select FBA Location in Shop.'))

            instance_data = each_shipment.shop_id.instance_id
            request_data = {
                'ShipmentId': each_shipment.inbound_shipment_id,
            }
            results = amazon_api_obj.call(instance_data, 'ListInboundShipmentItems',request_data)
            print 'results',results, results != 'None'
            if results != None:
                for each_result in results:
                    shipment_lines = fba_shipment_processing_line_obj.search(cr,uid,[('amazon_inbound_shipping_id','=',each_shipment.id),('amazon_sku.name','=',each_result['SellerSKU'])])
                    if not shipment_lines:
                        continue
                    
                    shipment_line_data = fba_shipment_processing_line_obj.browse(cr,uid,shipment_lines[0])
                    #If received Qy = 0 ,write all Qty in transit
                    if int(each_result['QuantityShipped']) == 0:
                        shipment_line_data.write({'intransit_qty':int(shipment_line_data.qty)})
                        continue

                    if shipment_line_data.moved_qty != int(each_result['QuantityReceived']):
                        stock_to_be_moved = int(each_result['QuantityReceived']) - shipment_line_data.moved_qty
                        print 'stock_to_be_moved',stock_to_be_moved

                        data_write = {
                            'intransit_qty':shipment_line_data.qty - int(each_result['QuantityReceived']),
                            'moved_qty': int(each_result['QuantityReceived']),
                        }
                        print "(((((((data_write((((((",data_write
                        shipment_line_data.write(cr, uid, shipment_line_data[0],data_write)

        #Mark the Shipment as Done if Qty In Transit <= 0
        count = 0
        for each_shipment in fba_shipment_processing_obj.browse(cr,uid,ids):
            for each_line in each_shipment.shipping_product_ids:
                if int(each_line.intransit_qty) <= 0:
                    count += 1
            print "========count == len(each_shipment.shipping_product_ids)=======>",count,len(each_shipment.shipping_product_ids)
            if count == len(each_shipment.shipping_product_ids):
                each_shipment.write({'state':'done'})
                
        return True
    
    
    def action_download_shipment_label(self, cr, uid, ids, context=None):
        amazon_api_obj = self.pool.get('amazonerp.osv')
        attach_object=self.pool.get('ir.attachment')
        (data,) = self.browse(cr,uid,ids)
        if data.shop_id and data.inbound_shipment_id:
            instance_data = data.shop_id.instance_id
            package_label_count = len(data.packaging_ids)
            if instance_data.site == 'United Kingdom':
                lbl = 'PackageLabel_A4_4'
            else:
                lbl = 'PackageLabel_Letter_2'
            request_data = {
                'ShipmentId': data.inbound_shipment_id,
                'PageType': lbl,
                'NumberOfPackages':package_label_count,
            }
            results = amazon_api_obj.call(instance_data, 'GetPackageLabels',request_data)
            if results.get('PdfDocument',False):
#                file_pdf = open('/var/www/'+data.shipment_id+'.zip','wb')
#                file_pdf.write(b64decode(results.get('PdfDocument')))
#                file_pdf.close()
#                os.system('unzip '+'/var/www/'+data.shipment_id+'.zip -d /var/www')
                attachment_pool = self.pool.get('ir.attachment')
                
                datas = binascii.b2a_base64(str(b64decode(results.get('PdfDocument'))))
                data_attach = {
                    'name': 'PackingSlip.zip',
                    'datas': datas,
                    'res_name': data.name,
                    'res_model': 'amazon.inbound.shipment',
                    'res_id': data.id,
                }
                attach_id = attach_object.search(cr,uid,[('name','=','PackingSlip.zip'),('res_id','=',data.id),('res_model','=','amazon.inbound.shipment')])
                if not attach_id:
                    attach_id = attach_object.create(cr, uid, data_attach)
                    print "===attach_id=ifffffff=>",attach_id
                else:
                    attach_id = attach_id[0]
                    print "===attach_id=ifffffff=>",attach_id, data_attach
                    attach_object.write(cr, uid, [attach_id], data_attach)
            
        return True
    
    def action_download_box_label(self, cr, uid, ids, context=None):
        amazon_api_obj = self.pool.get('amazonerp.osv')
        (data,) = self.browse(cr,uid,ids)
        if data.shop_id and data.inbound_shipment_id:
            instance_data = data.shop_id.instance_id
            package_label_count = len(data.packaging_ids)
            if instance_data.site == 'United Kingdom':
                lbl = 'PackageLabel_A4_2'
            else:
                lbl = 'PackageLabel_Letter_6'
            
            request_data = {
                'ShipmentId': data.inbound_shipment_id,
                'PageType': lbl,
                'NumberOfPackages':package_label_count,
            }
            results = amazon_api_obj.call(instance_data, 'GetPackageLabels',request_data)
            if results.get('PdfDocument',False):
#                file_pdf = open('/var/www/'+data.shipment_id+'.zip','wb')
#                file_pdf.write(b64decode(results.get('PdfDocument')))
#                file_pdf.close()
#                os.system('unzip '+'/var/www/'+data.shipment_id+'.zip -d /var/www')
                attachment_pool = self.pool.get('ir.attachment')

                datas = binascii.b2a_base64(str(b64decode(results.get('PdfDocument'))))
                data_attach = {
                    'name': 'BoxLabel.zip',
                    'datas': datas,
                    'description': data.name,
                    'res_name': data.name,
                    'res_model': data._name,
                    'res_id': data.id,
                }
                attach_id = attachment_pool.search(cr,uid,[('name','=','BoxLabel.zip'),('res_id','=',data.id),('res_model','=','amazon.inbound.shipment')])
                if not attach_id: 
                    attach_id = attachment_pool.create(cr, uid, data_attach)
                else:
                    attach_id = attach_id[0]
                    attachment_pool.write(cr, uid, [attach_id], data_attach)

        return True
    
    def create(self, cr, uid, vals, context=None):
        print "::::::::::::::::::::",vals, self.pool.get('ir.sequence').get(cr, uid, 'amazon.inbound.shipment')
        if not vals.get('name'):
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'amazon.inbound.shipment')
        return super(amazon_inbound_shipment, self).create(cr, uid, vals, context=context)
    
    def get_confirm(self, cr, uid, ids, context={}):
        self.write(cr, uid, ids[0], {'state': 'confirm'})
        return True
    
    def get_transfer(self, cr, uid, ids, context={}):
        self.write(cr, uid, ids[0], {'state': 'transfer'})
        return True
    
    def get_transit(self, cr, uid, ids, context={}):
        self.write(cr, uid, ids[0], {'state': 'in_transit'})
        return True
    
    def get_confirm_charges(self, cr, uid, ids, context={}):
        self.write(cr, uid, ids[0], {'state': 'confirm_charges'})
        return True
    
    def get_done(self, cr, uid, ids, context={}):
        self.write(cr, uid, ids[0], {'state': 'done'})
        return True
    
    def get_cancel(self, cr, uid, ids, context={}):
        self.write(cr, uid, ids[0], {'state': 'cancel'})
        return True
    
amazon_inbound_shipment()

