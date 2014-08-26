from openerp.osv import osv, fields
from datetime import datetime, timedelta
import time
import logging
import utils

logger = logging.getLogger('sale')

class sale_shop(osv.osv):
    _name = "sale.shop"
    _inherit = "sale.shop"
    __logger = logging.getLogger(_name)

    _columns = {
        'instance_id' : fields.many2one('sales.channel.instance', 'Instance', readonly=True),
        'amazon_shop' : fields.boolean('Amazon Shop', readonly=True),
        'amazon_margin':fields.float('Amazon Margin', size=64),
        'requested_report_id': fields.char('Requested Report ID', size=100 , readonly=True),
        'report_id': fields.char('Report ID', size=100 , readonly=True),
        'report_update':fields.datetime('Last ASIN Import Date'),
        'report_requested_datetime': fields.datetime('Report Requested'),
        'fba_location':fields.many2one('stock.location', 'FBA Location'),
        'amazon_fba_shop':fields.boolean('FBA Shop', readonly=True),
    }
        
    def import_listing(self, cr, uid, ids, shop_id, product_id , resultvals, context={}):
        amazon_product_listing_obj = self.pool.get('amazon.product.listing')
        print "===import_listing in amazonnnnnnnnnnnnnnn======>", shop_id
        if isinstance(shop_id, int):
            shop_obj = self.pool.get('sale.shop').browse(cr, uid, shop_id)
        else:
            shop_obj = shop_id
        print "SHOPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP"
        if shop_obj.amazon_shop:
            product_sku = resultvals.get('SellerSKU', False)
            amazon_ids = amazon_product_listing_obj.search(cr, uid, [('product_id', '=', product_id), ('name', '=', product_sku)])
            if not amazon_ids:
                vals = {
                    'product_id': product_id,
                    'name': product_sku,
                    'title': resultvals.get('Title', False),
                    'asin': resultvals.get('listing_id', False),
                    'shop_id': shop_obj.id
                }
                print "*************", amazon_product_listing_obj.create(cr, uid, vals)
        return super(sale_shop, self).import_listing(cr, uid, ids, shop_id, product_id, resultvals, context)
        
    def import_amazon_orders(self, cr, uid, ids, context=None):
        amazon_api_obj = self.pool.get('amazonerp.osv')
        sale_order_obj = self.pool.get('sale.order')
        pick_obj = self.pool.get('stock.picking')
        final_resultvals = []
        instance_obj = self.browse(cr, uid, ids[0])
        context.update({'from_date': datetime.now()})
        
        createdAfter = utils.calcCreatedAfter(instance_obj.last_import_order_date)
        fulfillment = 'MFN'
        if instance_obj.amazon_fba_shop:
            fulfillment = 'AFN'
            
        results = amazon_api_obj.call(instance_obj.instance_id, 'ListOrders', createdAfter, False, fulfillment)
        print "=**********results********", results
        
#        logger.error('results %s',  results)
        time.sleep(30)
        result_next_token = False
        if results:
            last_dictionary = results[-1]
            while last_dictionary.get('NextToken', False):
                result_next_token = True
                next_token = last_dictionary.get('NextToken', False)
                del results[-1]
                
                result_vals = []
                context['shipping_product_default_code'] = 'SHIP AMAZON'
                context['default_product_category'] = 1
                for result in results:
                    print "=**********result********", result
                    saleorderids = sale_order_obj.search(cr, uid, [('name', '=', instance_obj.prefix + result['OrderId'] + instance_obj.suffix), ('shop_id', '=', instance_obj.id)])
                    if saleorderids:
                        if sale_order_obj.browse(cr, uid, saleorderids[0]).state != 'draft':
                            print 'Order Exist', result['OrderId']
                            continue
                    result_vals = amazon_api_obj.call(instance_obj.instance_id, 'ListOrderItems', result['OrderId'])

                    for result_val in result_vals:
                        print 'result_val', result_val
                        result_val.update(result)
                        final_resultvals.append(result_val)
                        print 'result_val : ',result_val

                if final_resultvals:
                    order_ids = self.createOrder(cr, uid, ids, instance_obj.id, final_resultvals, context)
                    for saleorderid in order_ids:
                        sobj = sale_order_obj.browse(cr, uid, saleorderid)
                        if instance_obj.amazon_fba_shop:
                            picking_ids = sobj.picking_ids
                            if picking_ids:
                                for each_picking in picking_ids:
                                    pick_obj.write(cr, uid, each_picking.id, {'carrier_tracking_ref':'FULFILLMENT'})
                                    pick_obj.force_assign(cr, uid, [each_picking.id])
                                    context.update({'location_id': instance_obj.fba_location.id})
                                    self.do_partial(cr, uid, [each_picking.id], context)
                
                time.sleep(25)
                result_next_token = amazon_api_obj.call(instance_obj.instance_id, 'ListOrdersByNextToken', next_token)
                results = result_next_token
                last_dictionary = results[-1]
                if last_dictionary.get('NextToken', False) == False:
                    break
            
            if not result_next_token:
                result_vals = []
                context['shipping_product_default_code'] = 'SHIP AMAZON'
                context['default_product_category'] = 1
                for result in results:
                    print "=**********result********", result
                    saleorderids = sale_order_obj.search(cr, uid, [('name', '=', instance_obj.prefix + result['OrderId'] + instance_obj.suffix), ('shop_id', '=', instance_obj.id)])
                    if saleorderids:
                        if sale_order_obj.browse(cr, uid, saleorderids[0]).state != 'draft':
                            print 'Order Exist', result['OrderId']
                            continue
                    result_vals = amazon_api_obj.call(instance_obj.instance_id, 'ListOrderItems', result['OrderId'])

                    for result_val in result_vals:
                        print 'result_val', result_val
                        result_val.update(result)
                        final_resultvals.append(result_val)
                        
                        print 'result_val : ',result_val

                if final_resultvals:
                    order_ids = self.createOrder(cr, uid, ids, instance_obj.id, final_resultvals, context)
                    for saleorderid in order_ids:
                        sobj = sale_order_obj.browse(cr, uid, saleorderid)
                        if instance_obj.amazon_fba_shop:
                            picking_ids = sobj.picking_ids
                            if picking_ids:
                                for each_picking in picking_ids:
                                    pick_obj.write(cr, uid, each_picking.id, {'carrier_tracking_ref':'FULFILLMENT'})
                                    pick_obj.force_assign(cr, uid, [each_picking.id])
                                    context.update({'location_id': instance_obj.fba_location.id})
                                    self.do_partial(cr, uid, [each_picking.id], context)
             
        return True
    
    def do_partial(self, cr, uid, ids, context=None):
        # no call to super!
        stock_pick_obj = self.pool.get('stock.picking')
        moveobj = self.pool.get('stock.move')
        assert len(ids) == 1, 'Partial move processing may only be done one form at a time.'
        print ids
        partial = stock_pick_obj.browse(cr, uid, ids[0], context=context)
        print partial
        partial_data = {
            'delivery_date' : partial.date
        }
        print partial.move_lines
        moves_ids = []
        for move in partial.move_lines:
            if context.get('location_id', False):
                moveobj.write(cr, uid, move.id, {'location_id': context.get('location_id')})
            move_id = move.id
            partial_data['move%s' % (move_id)] = {
                'product_id': move.product_id.id,
                'product_qty': move.product_qty,
                'product_uom': move.product_uom.id,
#                'prodlot_id': move.prodlot_id.id,
            }
            moves_ids.append(move_id)
            if (move.picking_id.type == 'in') and (move.product_id.cost_method == 'average'):
                partial_data['move%s' % (move_id)].update(product_price=move.cost,
                                                          product_currency=move.currency.id)
        self.pool.get('stock.move').do_partial(cr, uid, moves_ids, partial_data, context=context)
        return True
    
    
    def update_amazon_order_status(self, cr, uid, ids, context={}):
        logger.error('update_amazon_order_status %s', ids)
        if context == None:
            context = {}
        shop_obj = self.browse(cr, uid, ids[0])
        instance_obj = shop_obj.instance_id
        amazon_api_obj = self.pool.get('amazonerp.osv')
        sale_order_obj = self.pool.get('sale.order')

        sale_ids = [1]
        offset = 0
        while len(sale_ids):
            today_data = time.strftime("%Y-%m-%d")
            print 'today_data', today_data
            sale_ids = sale_order_obj.search(cr, uid, [('track_exported', '=', False), ('state', '=', 'done'), ('shop_id', '=', shop_obj.id)], offset, 100, 'id')
            logger.error('sale_ids %s', sale_ids)

            if not sale_ids:
                break
            offset += len(sale_ids)

            message_information = ''
            message_id = 1

            today = datetime.now()
            DD = timedelta(seconds=120)
            earlier = today - DD
            fulfillment_date = earlier.strftime("%Y-%m-%dT%H:%M:%S")
            fulfillment_date_concat = str(fulfillment_date) + '-00:00'

            for sale_data in sale_order_obj.browse(cr, uid, sale_ids):
                order_id = sale_data.unique_sales_rec_no  # for getting order_id
                logger.error('order_id %s', order_id)
                
                print "======sale_data.picking_ids=====>", sale_data.picking_ids
                if sale_data.picking_ids:
                    picking_data = sale_data.picking_ids[0]
                    tracking_id = picking_data.carrier_tracking_ref  # for getting tracking_id
                    carrier_id = picking_data.carrier_id
                    if not carrier_id:
                        continue

                    carrier_name = carrier_id.carrier_name
                    shipping_method = carrier_id.shipping_method

                    for each_line in sale_data.order_line:
                        product_qty = int(each_line.product_uom_qty)
                        product_order_item_id = each_line.unique_sales_line_rec_no
                        

                        fulfillment_date = picking_data.date_done.replace(' ', 'T')[:19]
                        fulfillment_date_concat = str(fulfillment_date) + '-00:00'
                        print 'fulfillment_date_concat', fulfillment_date_concat
                        logger.error('fulfillment_date_concat %s', fulfillment_date_concat)

                        item_string = '''<Item><AmazonOrderItemCode>%s</AmazonOrderItemCode>
                                        <Quantity>%s</Quantity></Item>''' % (product_order_item_id, product_qty)


                        message_information += """<Message>
                                            <MessageID>%s</MessageID>
                                            <OperationType>Update</OperationType>
                                            <OrderFulfillment><AmazonOrderID>%s</AmazonOrderID>
                                            <FulfillmentDate>%s</FulfillmentDate>
                                            <FulfillmentData>
                                            <CarrierName>%s</CarrierName>
                                            <ShippingMethod>%s</ShippingMethod>
                                            <ShipperTrackingNumber>%s</ShipperTrackingNumber>
                                            </FulfillmentData>%s</OrderFulfillment>
                                            </Message>""" % (message_id, order_id, fulfillment_date_concat, carrier_name, shipping_method, tracking_id, item_string.encode("utf-8"))
                        message_id = message_id + 1

            data = """<?xml version="1.0" encoding="utf-8"?><AmazonEnvelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="amzn-envelope.xsd"><Header><DocumentVersion>1.01</DocumentVersion><MerchantIdentifier>M_SELLERON_82825133</MerchantIdentifier></Header><MessageType>OrderFulfillment</MessageType>""" + message_information.encode("utf-8") + """</AmazonEnvelope>"""

            logger.error('data ---------> %s', data)
            results = amazon_api_obj.call(instance_obj, 'POST_ORDER_FULFILLMENT_DATA', data)
            logger.error('results ---------> %s', results)

            for sale_data in sale_order_obj.browse(cr, uid, sale_ids):
                sale_data.write({'track_exported':True})
                cr.commit()

            time.sleep(70)

        return True
    
    # Listing
    def request_products_report(self, cr, uid, ids, context=None):
#        try:
            if context == None:
                context = {}


            (data,) = self.browse(cr, uid, ids , context=context)
            instance_obj = data.instance_id
            amazon_api_obj = self.pool.get('amazonerp.osv')
            StartDate = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()) + '.000Z'
            reportData = amazon_api_obj.call(instance_obj, 'RequestReport', '_GET_MERCHANT_LISTINGS_DATA_', StartDate)
            print "======reportData======>", reportData
            if reportData.get('ReportProcessingStatus', False):
                if reportData['ReportProcessingStatus'] == '_SUBMITTED_':
                    self.write(cr, uid, ids, {'requested_report_id':reportData['ReportRequestId'], 'report_id':'', 'report_requested_datetime':time.strftime("%Y-%m-%d %H:%M:%S")}, context)
                    cr.commit()
                else:
                    if context.get('raise_exception', False):
                        raise osv.except_osv(_('Error Sending Request'), '%s' % _(reportData['ReportProcessingStatus']))
            else:
                if context.get('raise_exception', False):
                    raise osv.except_osv(_('Error Sending Request'), '%s' % _('Null Response'))
            return True
        
    def check_report_status(self, cr, uid, ids, context=None):
#        try:
            if context == None:
                context = {}

            (data,) = self.browse(cr, uid, ids , context=context)
            instance_obj = data.instance_id
            amazon_api_obj = self.pool.get('amazonerp.osv')
            if not data.requested_report_id:
                raise osv.except_osv(_('Error !'), '%s' % _('Please request Report'))

            reportList = amazon_api_obj.call(instance_obj, 'GetReportList', False, data.requested_report_id, False, False)
            print "======reportList=====>", reportList
            if reportList:
                self.write(cr, uid, ids, {'report_id':reportList[0]}, context)
                cr.commit()
            else:
                if not context.get('raise_exception', False):
                    raise osv.except_osv(_('Error !'), '%s' % _('Request Status Not Done'))

            return True
    
    def handleMissingAsins(self, cr, uid, ids, missed_resultvals, context=None):
        count = 0
        amazon_stock_synch_obj = self.pool.get('amazon.stock.sync')
        while (missed_resultvals):
            count = count + 1  # ## count is to make sure loop doesn't go into endless iteraiton
            if count > 3:
                break

            resultvals = missed_resultvals
            print 'missed_resultvals', missed_resultvals
            
            for results in resultvals:
                print 'results', results
                try:
                    amazon_stock_synch_obj.write(cr, uid, [results['stock_sync_id']], results)
                    cr.commit()
                    missed_resultvals.remove(results)
                
                except Exception, e:
                    print "Import Amazon Listing handleMissingItems: ", e
                    time.sleep(20)

        return True
    
    
    def import_amazon_products(self, cr, uid, ids, context=None):
        (data,) = self.browse(cr, uid, ids , context=context)
        amazon_api_obj = self.pool.get('amazonerp.osv')
        prod_obj = self.pool.get('product.product')
        amazon_product_listing_obj = self.pool.get('amazon.product.listing')
        if not data.report_id:
            raise osv.except_osv('Error', '%s' % ('Please request New Report'))

        instance_obj = data.instance_id
        missed_resultvals = []
        response = amazon_api_obj.call(instance_obj, 'GetReport', data.report_id)
        
        amazon_create_vals = {}

        if response:
            product_inv_data_lines = response.split("\n")
            count = 0
            for product_inv_data_line in product_inv_data_lines:
                count += 1

                if count == 1:
                    continue

                if product_inv_data_line == '' :
                    continue

                try:
                    product_inv_data_fields = product_inv_data_line.split('\t')
                    sku = product_inv_data_fields[3].strip(" ")
                    asin = product_inv_data_fields[16].strip(" ")
                    amazon_stock = product_inv_data_fields[5].strip(" ")
                    amazon_price = product_inv_data_fields[4].strip(" ")
                    name = (product_inv_data_fields[0].strip(" ")).encode('utf-8')
                    print "======name========>", name
                    if len(sku.split(" ")):
                        fulfillment_channel = 'DEFAULT'
                        print "================sku,", sku
                        product_ids = prod_obj.search(cr, uid, [('default_code', '=', sku)])
                        print "=======product_ids======>", product_ids
                        if not product_ids:
                            product_ids = [prod_obj.create(cr, uid, {'default_code': sku, 'name': name, 'list_price':float(amazon_price)})]
                        print 'product_ids ===', product_ids

                        if not len(product_ids):
                            continue

                        if asin == '':
                            continue

                        listing_ids = amazon_product_listing_obj.search(cr, uid, [('product_id', '=', product_ids[0]), ('name', '=', sku), ('asin', '=', asin), ('shop_id', '=', data.id)])
                        print 'listing_ids', listing_ids

                        fulfillment_channel = 'DEFAULT'

                        try:
                            price = float(amazon_price)
                        except:
                            price = 0.0
                            pass

                        print 'price', price
                        print 'amazon_stock', amazon_stock

                        if amazon_stock == '':
                            continue

                        amazon_create_vals = {
                            'listing_name':sku,
                            'name':sku,
                            'asin':asin,
                            'fulfillment_channel':fulfillment_channel,
                            'product_id':product_ids[0],
                            'shop_id':data.id,
                            'active_amazon':True,
                        
                            'last_sync_stock':amazon_stock,
                            'last_sync_price':price,
                            'last_sync_date':data.report_requested_datetime,
                            'title': name or ' '
                        }

                        print 'amazon_create_vals', amazon_create_vals
                        if not listing_ids:
                            listing_id = amazon_product_listing_obj.create(cr, uid, amazon_create_vals)
                        else:
                            amazon_product_listing_obj.write(cr, uid, listing_id[0], amazon_create_vals)

                        print 'listing_id', listing_id

                        cr.commit()

#                            if count % 7 == 0:
#                                raise Exception("concurrent update")

                except Exception, e:
                    print "handleUpdate ASIN Exception: ", e
                    if str(e).find('concurrent update') != -1:
                        cr.rollback()
                        time.sleep(20)
                        missed_resultvals.append(amazon_create_vals)
                    continue

        # Handle Misses ASIN ORders
        self.handleMissingAsins(cr, uid, ids, missed_resultvals)


        # Inactivate all the ASIN which are not synced
        cr.execute('select id from amazon_product_listing where (last_sync_date < %s or last_sync_date is null) and shop_id = %s ', (data.report_update, data.id))
        amazon_listing_ids = filter(None, map(lambda x: x[0], cr.fetchall()))
        print 'amazon_listing_ids', amazon_listing_ids
        for each_listing in amazon_listing_ids:
            try:
                amazon_product_listing_obj.write(cr, uid, [each_listing], {'last_sync_stock':0, 'last_sync_date':data.report_update})
#            except Exception, e:
#                print "--->",e
            except Exception, e:
                if str(e).find('concurrent update') != -1:
                    cr.rollback()
                    time.sleep(20)
        self.write(cr, uid, ids, {'report_update': datetime.now(), 'requested_report_id':False})
        return True
    
    # stock
    def xml_format(self, message_type, merchant_string, message_data):
        result = """
            <?xml version="1.0" encoding="utf-8"?>
            <AmazonEnvelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="amzn-envelope.xsd">
            <Header>
            <DocumentVersion>1.01</DocumentVersion>
            """ + merchant_string.encode("utf-8") + """
            </Header>
            """ + message_type.encode("utf-8") + """
            """ + message_data.encode("utf-8") + """
            </AmazonEnvelope>"""
        return result
    
    def _export_amazon_stock_generic(self, cr, uid, ids, instance_obj, xml_data, context=None):
        if context == None:
            context = {}
        amazon_api_obj = self.pool.get('amazonerp.osv')
        merchant_string = "<MerchantIdentifier>%s</MerchantIdentifier>" % (instance_obj.aws_merchant_id)
        message_type = '<MessageType>Inventory</MessageType>'
        stock_data = self.xml_format(message_type, merchant_string, xml_data)
        stock_submission_id = False
        print 'stock_data*****************************************', stock_data
        try:
            stock_submission_id = amazon_api_obj.call(instance_obj, 'POST_INVENTORY_AVAILABILITY_DATA', stock_data)
            print 'stock_submission_id', stock_submission_id
        except Exception, e:
            raise osv.except_osv(_('Error !'), _('%s') % (e))

        return True
    
    def export_amazon_stock(self, cr, uid, ids, context=None):
        print 'context in price', context
        amazon_prod_list_obj = self.pool.get('amazon.product.listing')
        if context == None:
            context = {}
        context.update({'from_date': datetime.now()}) 
        (data,) = self.browse(cr, uid, ids)
        amazon_inst_data = data.instance_id
        if context.has_key('listing_ids'):
            listing_ids = context.get('listing_ids')
        else:
            listing_ids = amazon_prod_list_obj.search(cr, uid, [('active_amazon', '=', True), ('shop_id', '=', data.id)])
        xml_data = ''
        message_id = 1
        for amazon_list_data in amazon_prod_list_obj.browse(cr, uid, listing_ids):
            if amazon_list_data.product_id.type == 'service':
                continue
            
            if not amazon_list_data.name:
                raise osv.except_osv(_('Please enter SKU for '), '%s' % _(amazon_list_data.name))

            qty = amazon_list_data.product_id.qty_available
            # If stock goes Negative , Update it to 0, because amazon doesnt accept it and API Fails
            if int(qty) < 0:
                qty = 0

            update_xml_data = '''<SKU><![CDATA[%s]]></SKU>
                                <Quantity>%s</Quantity>
                                ''' % (amazon_list_data.name, int(qty))

            xml_data += '''<Message>
                        <MessageID>%s</MessageID><OperationType>Update</OperationType>
                        <Inventory>%s</Inventory></Message>
                    ''' % (message_id, update_xml_data)

            message_id += 1
        if xml_data != '':
            self._export_amazon_stock_generic(cr, uid, ids, amazon_inst_data, xml_data)
        return True
        
    # price
    def _export_amazon_price_generic(self, cr, uid, ids, instance_obj, xml_data, context=None):
        amazon_api_obj = self.pool.get('amazonerp.osv')
        merchant_string = "<MerchantIdentifier>%s</MerchantIdentifier>" % (instance_obj.aws_merchant_id)
        message_type = """<MessageType>Price</MessageType>"""
        price_data = self.xml_format(message_type, merchant_string, xml_data)
        print 'price_data*************', price_data
        price_submission_id = False
        try:
            price_submission_id = amazon_api_obj.call(instance_obj, 'POST_PRODUCT_PRICING_DATA', price_data)
            print 'price_submission_id', price_submission_id
        except Exception, e:
            raise osv.except_osv(_('Error !'), _('%s') % (e))
        return True
    
    def export_amazon_price(self, cr, uid, ids, context=None):
        print 'context in price', context
        amazon_prod_list_obj = self.pool.get('amazon.product.listing')
        if context == None:
            context = {}
        context.update({'from_date': datetime.now()}) 
        (data,) = self.browse(cr, uid, ids)
        instance_obj = data.instance_id
        if context.has_key('listing_ids'):
            listing_ids = context.get('listing_ids')
        else:
            listing_ids = amazon_prod_list_obj.search(cr, uid, [('active_amazon', '=', True), ('shop_id', '=', data.id)])
        price_string = ''
        message_id = 1
        for amazon_list_data in amazon_prod_list_obj.browse(cr, uid, listing_ids):
            if amazon_list_data.product_id.type == 'service':
                continue
            
            if not amazon_list_data.name:
                raise osv.except_osv(_('Please enter SKU for '), '%s' % _(amazon_list_data.title))

            price = amazon_list_data.last_sync_price
            if float(price) > 0.00:
                price_string += """<Message>
                        <MessageID>%s</MessageID>
                        <Price>
                        <SKU><![CDATA[%s]]></SKU>
                        <StandardPrice currency='%s'>%.2f</StandardPrice>
                        </Price>
                        </Message>""" % (message_id, amazon_list_data.name, amazon_list_data.product_id.company_id.currency_id.name, float(price))
                message_id += 1
                print "=========amazon_list_data.product_id.company_id.currency_id.name============>", amazon_list_data.product_id.name, amazon_list_data.product_id.company_id.name, amazon_list_data.product_id.company_id.currency_id.name
        if price_string != '':
            self._export_amazon_price_generic(cr, uid, ids, instance_obj, price_string)
        return True

    # Upload Listing Methods
    def _my_value(self, cr, uid, location_id, product_id, context=None):
        cr.execute(
            'select sum(product_qty) '\
            'from stock_move '\
            'where location_id NOT IN  %s '\
            'and location_dest_id = %s '\
            'and product_id  = %s '\
            'and state = %s ', tuple([(location_id,), location_id, product_id, 'done']))
        wh_qty_recieved = cr.fetchone()[0] or 0.0
        # this gets the value which is sold and confirmed
        argumentsnw = [location_id, (location_id,), product_id, ('done',)]  # this will take reservations into account
        cr.execute(
            'select sum(product_qty) '\
            'from stock_move '\
            'where location_id = %s '\
            'and location_dest_id NOT IN %s '\
            'and product_id  = %s '\
            'and state in %s ', tuple(argumentsnw))
        qty_with_reserve = cr.fetchone()[0] or 0.0
        qty_available = wh_qty_recieved - qty_with_reserve
        return qty_available
    
    def import_amazon_stock(self, cr, uid, ids, context={}):
        listing_obj = self.pool.get('amazon.product.listing')
        amazon_api_obj = self.pool.get('amazonerp.osv')
        (obj,) = self.browse(cr, uid, ids)
        listing_ids = listing_obj.search(cr, uid, [('shop_id', '=', ids[0])])
        sku_list = []
        for record in listing_obj.browse(cr, uid, listing_ids):
            sku_list.append(record.name)
        print "========sku_list===>", sku_list
        result = amazon_api_obj.call(obj.instance_id, 'ListInventorySupply', sku_list)
        print "=====result======>", result
        if result:
            for rec in result:
                print "===>", rec.get('SellerSKU')
                l_ids = listing_obj.search(cr, uid, [('name', '=', rec['SellerSKU'])])
                if l_ids:
                    listing_obj.write(cr, uid, l_ids[0], {'last_sync_stock': float(rec['InStockSupplyQuantity'])}) 
        print "===========result====>", result
        return True
    
    
sale_shop()

class sale_order(osv.osv):
    _name = 'sale.order'
    _inherit = 'sale.order'
    def _default_journal(self, cr, uid, context={}):
        accountjournal_obj = self.pool.get('account.journal')
        accountjournal_ids = accountjournal_obj.search(cr, uid, [('name', '=', 'Sales Journal')])
        if accountjournal_ids:
            return accountjournal_ids[0]
        else:
#            raise wizard.except_wizard(_('Error !'), _('Sales journal not defined.'))
            return False
    _columns = {
        'amazon_order_id' : fields.char('Order ID', size=256),
        'journal_id': fields.many2one('account.journal', 'Journal', readonly=True),
        'faulty_order':fields.boolean('Faulty'),
        'confirmed':fields.boolean('Confirmed'),
        'shipservicelevel':fields.char('ShipServiceLevel', size=64),
    }
    _defaults = {
        'journal_id': _default_journal,
    }
sale_order()

class sale_order_line(osv.osv):
    _name = 'sale.order.line'
    _inherit = 'sale.order.line'

    _columns = {
        'order_item_id' : fields.char('Order Item ID', size=256),
        'asin' : fields.char('Asin', size=256),
    }

sale_order_line()
