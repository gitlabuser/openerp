# -*- coding: utf-8 -*-
##############################################################################
#
#    TeckZilla Software Solutions and Services
#    Copyright (C) 2012-2013 TeckZilla-OpenERP Experts(<http://www.teckzilla.net>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import osv, fields
from tools.translate import _
import netsvc
import re
import time
import datetime
import logging
logger = logging.getLogger('sale')

class sale_shop(osv.osv):
    _inherit = "sale.shop"
    _columns = {
        'instance_id' : fields.many2one('sales.channel.instance','Instance',readonly=True),
        'last_update_order_date' : fields.date('Last Update order Date'),
        'prefix': fields.char('Prefix', size=64),
        'suffix': fields.char('suffix', size=64),
        'last_update_order_status_date' : fields.datetime('Start Update Status Date'),
        'last_export_stock_date' :fields.datetime('Last Exported Stock Date'),
        'last_export_price_date' :fields.datetime('Last Exported Price Date'),
        'last_import_order_date' :fields.datetime('Last Imported Order Date'),
        'sale_channel_shop': fields.boolean('Sales channel shop'),
        'tax_include' : fields.boolean('Cost Price Include Taxes'),
        'picking_policy': fields.selection([('direct', 'Deliver each product when available'), ('one', 'Deliver all products at once')],
            'Shipping Policy',
            help="""Pick 'Deliver each product when available' if you allow partial delivery."""),
        'order_policy': fields.selection([
                ('manual', 'On Demand'),
                ('picking', 'On Delivery Order'),
                ('prepaid', 'Before Delivery'),
            ], 'Create Invoice'),
        'shop_address': fields.many2one('res.partner', 'Shop Address'),
        'alloc_type': fields.selection([('fixed','Fixed'),
                                        ('per','Percentage')],'Type'),
        'alloc_value': fields.float('Value')
    }
    
  
    #***************Update Order Status********************
    def update_order_status(self, cr, uid, ids, context={}):
        log_obj = self.pool.get('ecommerce.logs')
        log_vals = {}
        try:
            shop_obj = self.browse(cr, uid, ids[0])
            if shop_obj.instance_id.module_id == 'oeoo_amazon':
                self.update_amazon_order_status(cr, uid, ids, context = context)

            if shop_obj.instance_id.module_id == 'ebay_teckzilla':
                self.update_ebay_order_status(cr, uid, ids, context=context)
                
            if shop_obj.instance_id.module_id == 'magento_teckzilla':
                self.update_magento_order_status(cr, uid, ids, context=context)

            self.write(cr, uid, shop_obj.id, {'last_update_order_status_date': datetime.datetime.now()})
            log_vals = {
                            'activity': 'update_order_status',
                            'start_datetime': context.get('from_date',False),
                            'end_datetime': datetime.datetime.now(),
                            'shop_id': ids[0],
                            'message':'SucessFull'
                            }
        except Exception as e:
            log_vals = {
                            'activity': 'update_order_status',
                            'start_datetime': context.get('from_date',False),
                            'end_datetime': datetime.datetime.now(),
                            'shop_id': ids[0],
                            'message':'Failed '+str(e)
                            }
        log_obj.create(cr, uid, log_vals)
        return True
    
    #***************Export price********************
    def export_price(self, cr, uid, ids, context={}):
        print "======innnnnn export price========>"
        log_obj = self.pool.get('ecommerce.logs')
        log_vals = {}
        try:
            shop_obj = self.browse(cr, uid, ids[0])
            if shop_obj.amazon_shop:
                self.export_amazon_price(cr,uid,ids,context)
            if shop_obj.ebay_shop:
                self.export_stock_and_price(cr, uid, ids, context=context)
            if shop_obj.magento_shop:
                self.export_stock_and_price(cr, uid, ids, context=context)
            self.write(cr, uid, shop_obj.id, {'last_export_price_date': datetime.datetime.now()})
            log_vals = {   
                            'activity': 'export_price',
                            'start_datetime': context.get('from_date',False),
                            'end_datetime': datetime.datetime.now(),
                            'shop_id': ids[0],
                            'message':'Successful'
                            }
        except Exception as e:
            log_vals = {   
                            'activity': 'import_orders',
                            'start_datetime': context.get('from_date',False),
                            'end_datetime': datetime.datetime.now(),
                            'shop_id': ids[0],
                            'message':'Failed ' + str(e)
                            }
        log_obj.create(cr, uid, log_vals)
        return True
    
    #**************Stock Function***********************
    #***************Export Stock********************
    def export_stock(self, cr, uid, ids, context={}):
        print "======innnnnn export stock========>"
        log_obj = self.pool.get('ecommerce.logs')
        log_vals = {}
        try:
            shop_obj = self.browse(cr, uid, ids[0])
            print "=======shop_obj.instance_id.module_id==========",shop_obj.instance_id.module_id
            
            if shop_obj.instance_id.module_id == 'oeoo_amazon':
                self.export_amazon_stock(cr,uid,ids,context)
            if shop_obj.instance_id.module_id == 'ebay_teckzilla':
                self.export_stock_and_price(cr, uid, ids, context=context) 
            if shop_obj.instance_id.module_id == 'magento_teckzilla':
                self.export_magento_stock(cr, uid, ids, context=context) 
            self.write(cr, uid, shop_obj.id, {'last_export_stock_date': datetime.datetime.now()})
            log_vals = {   
                            'activity': 'export_stock',
                            'start_datetime': context.get('from_date',False),
                            'end_datetime': datetime.datetime.now(),
                            'shop_id': ids[0],
                            'message':'Successful'
                            }
        except Exception as e:
            log_vals = {   
                            'activity': 'import_orders',
                            'start_datetime': context.get('from_date',False),
                            'end_datetime': datetime.datetime.now(),
                            'shop_id': ids[0],
                            'message':'Failed ' + str(e)
                            }
        log_obj.create(cr, uid, log_vals)
        return True
      
    
     #**************Orders Function***********************
    #***************Import Orders********************
    def import_orders(self, cr, uid, ids, context={}):
        print "======innnnnn main import Orders========>"
        log_obj = self.pool.get('ecommerce.logs')
        log_vals = {}
#        try:
        shop_obj = self.browse(cr, uid, ids[0])
        if shop_obj.instance_id.module_id == 'oeoo_amazon':
            self.import_amazon_orders(cr, uid, ids, context = context)
        print "============shop_obj.instance_id.module_id==========>",shop_obj.instance_id.module_id
        if shop_obj.instance_id.module_id == 'ebay_teckzilla':
            self.import_ebay_orders(cr, uid, ids, context=context)
        if shop_obj.instance_id.module_id == 'magento_teckzilla':
            self.import_magento_orders(cr, uid, ids, context=context)
        self.write(cr, uid, shop_obj.id, {'last_import_order_date': time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())})
        log_vals = {   
                        'activity': 'import_orders',
                        'start_datetime': context.get('from_date',False),
                        'end_datetime': datetime.datetime.now(),
                        'shop_id': ids[0],
                        'message':'Successful'
                        }
#        except Exception as e:
#            log_vals = {   
#                            'activity': 'import_orders',
#                            'start_datetime': context.get('from_date',False),
#                            'end_datetime': datetime.datetime.now(),
#                            'shop_id': ids[0],
#                            'message':'Failed ' + str(e)
#                            }
        log_obj.create(cr, uid, log_vals)
        return True
    
    def manageCountryCode(self, cr, uid, id, country_code, context):
        cr.execute("SELECT id from res_country WHERE lower(name) = %s or lower(code) in %s", (country_code.lower(), (country_code.lower(),country_code[:2].lower())))
        res = cr.fetchall()
        print "country res: ",res
        if not res:
            country_id = self.pool.get('res.country').create(cr,uid,{'code':country_code[:2].upper(), 'name': country_code.title()},context)
        else:
            country_id = res[0][0]
        return country_id
    
    def manageStateCode(self, cr, uid, id, state_code, country_id, context):
        state_name = re.sub('[^a-zA-Z ]*', '', state_code.upper())
        print "state_name: ",state_name
        cr.execute("SELECT id from res_country_state WHERE lower(name) = %s or lower(code) in %s AND country_id=%s", (state_name.lower(), (state_name.lower(),state_name[:3].lower()),country_id))
        res = cr.fetchall()
        print "state res: ",res
        if not res:
            state_id = self.pool.get('res.country.state').create(cr,uid,{'country_id':country_id, 'name':state_name.title(), 'code':state_name[:3].upper()},context)
        else:
            state_id = res[0][0]
        return state_id
    
    def updatePartnerInvoiceAddress(self, cr, uid, id, resultvals, context={}):
        partneradd_obj = self.pool.get('res.partner')
        if resultvals.get('BillingCountryCode',False):
            country_id = self.manageCountryCode(cr,uid,id,resultvals['BillingCountryCode'],context)
        else:
            return False

        if resultvals.get('BillingStateOrRegion',False):
            state_id = self.manageStateCode(cr,uid,id,resultvals['BillingStateOrRegion'],country_id,context)
        else:
            state_id = False

        addressvals = {
            'name' : resultvals['BillingName'],
            'street' : resultvals.get('BillingAddressLine1', False),
            'street2' : resultvals.get('BillingAddressLine2',False),
            'city' : resultvals.get('BillingCity',False),
            'country_id' : country_id,
            'state_id' : state_id,
            'phone' : resultvals.get('BillingPhone',False),
            'zip' : resultvals.get('BillingPostalCode',False),
            'email' : resultvals.get('BillingEmail',False),
            'type' : 'invoice',
        }
        if context.get('shoppartnerinvoiceaddrvals',False):
            addressvals.update(context['shoppartnerinvoiceaddrvals'])
        print "addressvals: ",addressvals
        partnerinvoice_ids = partneradd_obj.search(cr, uid, [('name','=',resultvals['BillingName']),('street','=',resultvals.get('BillingAddressLine1') and resultvals['BillingAddressLine1'] or ''),('zip','=',resultvals.get('BillingPostalCode') and resultvals['BillingPostalCode'] or '')])
        if partnerinvoice_ids:
           partnerinvoice_id = partnerinvoice_ids[0]
           partneradd_obj.write(cr, uid, partnerinvoice_id, addressvals) 
        else: 
            partnerinvoice_id = partneradd_obj.create(cr, uid,addressvals) 
            
        return partnerinvoice_id
  
    def updatePartnerShippingAddress(self, cr, uid, id, resultvals, context={}):
        partneradd_obj = self.pool.get('res.partner')
        if resultvals.get('ShippingCountryCode',False):
            country_id = self.manageCountryCode(cr,uid,id,resultvals['ShippingCountryCode'],context)
        else:
            return False

        if resultvals.get('ShippingStateOrRegion',False):
            state_id = self.manageStateCode(cr,uid,id,resultvals['ShippingStateOrRegion'],country_id,context)
        else:
            state_id = 0

        addressvals = {
            'name' : resultvals['ShippingName'],
            'street' : resultvals.get('ShippingAddressLine1',False),
            'street2' : resultvals.get('ShippingAddressLine2',False),
            'city' : resultvals.get('ShippingCity',False),
            'country_id' : country_id,
            'state_id' : state_id,
            'phone' : resultvals.get('ShippingPhone',False),
            'zip' : resultvals.get('ShippingPostalCode',False),
            'email' : resultvals.get('ShippingEmail',False),
            'type' : 'delivery',
        }
        if context.get('shoppartnershippingaddrvals',False):
            addressvals.update(context['shoppartnershippingaddrvals'])
        print "addressvals: ",addressvals
        partnershippingadd_ids = partneradd_obj.search(cr, uid, [('name','=',resultvals['ShippingName']),('street','=',resultvals.get('ShippingAddressLine1') and resultvals['ShippingAddressLine1'] or ''),('zip','=',resultvals.get('ShippingPostalCode') and resultvals['ShippingPostalCode'] or '')])
        if partnershippingadd_ids:
            partnershippingadd_id = partnershippingadd_ids[0]
            partneradd_obj.write(cr, uid, partnershippingadd_id, addressvals) 
        else: 
            partnershippingadd_id = partneradd_obj.create(cr, uid,addressvals)
        return partnershippingadd_id
  
    
    def import_listing(self, cr, uid, ids, shop_id, product_id,resultvals, context={}):
        return True  
   
    def createAccountTax(self, cr, uid, ids, value, context={}):
        accounttax_obj = self.pool.get('account.tax')
        accounttax_id = accounttax_obj.create(cr,uid,{'name':'Sales Tax(' + str(value) + '%)','amount':float(value)/100,'type_tax_use':'sale'})
        print 'createAccountTax id: ',accounttax_id
        return accounttax_id
    
    def computeTax(self, cr, uid, id, resultval, context):
        tax_id = []
        if float(resultval.get('ItemTax',0.0)) > 0.0:
            if resultval.get('ItemTaxPercentage',False):
                ship_tax_vat = float(resultval['ItemTaxPercentage']) / 100.00
                ship_tax_percent = float(resultval['ItemTaxPercentage'])
            else:
                ship_tax_vat = float(resultval['ItemTax'])/float(resultval['ItemPrice'])
                ship_tax_percent = float(resultval['ItemTax'])/float(resultval['ItemPrice']) * 100.00
            acctax_id = self.pool.get('account.tax').search(cr,uid,[('type_tax_use', '=', 'sale'), ('amount', '>=', ship_tax_vat - 0.001), ('amount', '<=', ship_tax_vat + 0.001)])
            print "acctax_id: ",acctax_id
            if not acctax_id:
                acctax_id = self.createAccountTax(cr,uid,id,ship_tax_percent, context)
                tax_id = [(6, 0, [acctax_id])]
            else:
                tax_id = [(6, 0, [acctax_id[0]])]
        return tax_id
  
    def createProduct(self, cr, uid, id, shop_id, product_details, context={}):
        ## Logic for creating products in OpenERP
        ###Getting Product Category

        prodtemp_obj = self.pool.get('product.template')
        prod_obj = self.pool.get('product.product')

        template_vals = {
            'list_price' : product_details.get('ItemPrice',0.00),
            'purchase_ok' : 'TRUE',
            'sale_ok' : 'TRUE',
            'name' : product_details['Title'],
            'type' : 'consu',
            'procure_method' : 'make_to_stock',
            'cost_method' : 'average',
            'standard_price': 0.00,
            'categ_id' : context['default_product_category'],
            'weight_net' : product_details.get('ItemWeight',0.00),
        }
        print "template_vals: ",template_vals
        template_id = prodtemp_obj.create(cr,uid,template_vals,context)
        product_vals = {
            'product_tmpl_id' : template_id,
            'default_code': product_details.get('SellerSKU','').strip()
        }
        print "=======product_vals===========>",product_vals
        if context.get('shopproductsvals',False):
            ordervals.update(context['shopproductsvals'])
        print "product_vals: ",product_vals
        prod_id = prod_obj.create(cr,uid,product_vals,context)

        return prod_id
  
   
    
    def oe_status(self, cr, uid, ids,resultval):
        saleorder_obj = self.pool.get('sale.order')
        order = saleorder_obj.browse(cr, uid, ids)
        wf_service = netsvc.LocalService('workflow')
        print ")))))))))))))))))))))))))))",resultval.get('confirm'),resultval.get('paid', False)
        if resultval.get('confirm', False):
            print wf_service.trg_validate(uid, 'sale.order', ids, 'order_confirm', cr)
            invoice_ids = self.pool.get('account.invoice').search(cr,uid,[('origin','=',order.name)])
            print "==========invoice_ids==========>",invoice_ids
            if len(invoice_ids):
                print wf_service.trg_validate(uid, 'account.invoice', invoice_ids[0], 'invoice_open', cr)
                if resultval.get('paid', False):
                    print self.pool.get('account.invoice').invoice_pay_customer(cr, uid, [invoice_ids[0]], context={})
                
        return True
    
    def manageSaleOrderLine(self, cr, uid, id, shop_id, saleorderid, resultval, context):
        saleorder_obj = self.pool.get('sale.order')
        saleorderline_obj = self.pool.get('sale.order.line')
        product_obj = self.pool.get('product.product')

        saleorderlineid = False
        
#        cr.execute("SELECT * FROM product_product WHERE substring(trim(product_sku),1,9) = %s and active=True",(resultval['SellerSKU'][:9],))
#        product_ids = filter(None, map(lambda x: x[0], cr.fetchall()))
#        print "base_ecommerce/sale.py > manageSaleOrderLine() product_ids: ",product_ids
        product_ids = product_obj.search(cr, uid, [('default_code','=',resultval['SellerSKU'])])
        if not product_ids:
            product_id = self.createProduct(cr,uid,id,shop_id,resultval,context)
        else:
            product_id = product_ids[0]
            
        
        ### Account Tax - Needs to be tested
        if not context.get('create_tax_product_line',False):
            tax_id = self.computeTax(cr, uid, id, resultval, context) if float(resultval['ItemTax']) > 0.00 else False
        else:
            tax_id = False

        product = product_obj.browse(cr,uid,product_id)

        orderlinevals = {
            'order_id' : saleorderid,
            'product_uom_qty' : resultval['QuantityOrdered'],
            'product_uom' : product.product_tmpl_id.uom_id.id,
            'name' : product.product_tmpl_id.name,
            'price_unit' : float(resultval['ItemPrice']),
#            'delay' : product.product_tmpl_id.sale_delay,
            'invoiced' : False,
            'state' : 'confirmed',
            'product_id' : product_id,
            'tax_id' : tax_id,
            'type': 'make_to_stock',
            'unique_sales_line_rec_no': resultval['unique_sales_line_rec_no']
        }
        if context.get('shoporderlinevals',False):
            orderlinevals.update(context['shoporderlinevals'])
        print "orderlinevals: ",orderlinevals

        if resultval.get('listing_id',False):
            self.import_listing(cr, uid, id, shop_id, product_id ,resultval, context={})

        '''### Check if there is no line
        is_line_order = len(saleorder_obj.browse(cr,uid,saleorderid).order_line)

        ### Check if order_id was created in same import only if order has >= 1 lines
        if is_line_order:
            cr.execute("SELECT id from sale_order WHERE id=%s AND import_unique_id =%s",(saleorderid, context.get('import_unique_id','')),)
            saleorderids = filter(None, map(lambda x: x[0], cr.fetchall()))
            if not len(saleorderids):
                print"manageSaleOrderLine import_unique_id different"
                return True

            ### Check if line with same unique_sales_line_rec_no/product_id already exist
            if context.get('orderline_search_clause',False):
                context['orderline_search_clause'].append(('order_id','=',saleorderid),)
                saleorderlineids = saleorderline_obj.search(cr,uid,context['orderline_search_clause']) or []
    #            cr.execute("SELECT l.id from sale_order s, sale_order_line l WHERE l.order_id=s.id AND s.id=%s AND l.unique_sales_line_rec_no=%s", (saleorderid,context['orderline_search_clause'],))
            else:
                cr.execute("SELECT l.id from sale_order s, sale_order_line l WHERE l.order_id=s.id AND s.id=%s AND l.product_id=%s", (saleorderid,product_id,))
                saleorderlineids = filter(None, map(lambda x: x[0], cr.fetchall()))
            if len(saleorderlineids):
                print"manageSaleOrderLine line already exist"
                return saleorderlineids[0]
        else:
            ### If no line, then update import_unique_id to current one
             saleorder_obj.write(cr,uid,saleorderid,{'import_unique_id':resultval['import_unique_id']})'''

        saleorderlineid = saleorderline_obj.create(cr,uid,orderlinevals,context)
        cr.commit()
        return saleorderlineid

    def createShippingProduct(self, cr, uid, id, context={}):
        prod_obj = self.pool.get('product.product')
        prodcateg_obj = self.pool.get('product.category')
        categ_id = prodcateg_obj.search(cr,uid,[('name','=','Service')])
        if not categ_id:
            categ_id = prodcateg_obj.create(cr,uid,{'name':'Service', 'type':'normal'},context)
        else:
            categ_id = categ_id[0]
        prod_id = prod_obj.create(cr,uid,{'type':'service','name':'Shipping and Handling', 'default_code':context['shipping_product_default_code'],'categ_id':categ_id},context)
#        print "createEbayShippingProduct id: ",prod_id
        return prod_id

    def manageSaleOrderLineShipping(self, cr, uid, id, shop_id, saleorderid, resultval, context):
        saleorderline_obj = self.pool.get('sale.order.line')
        product_obj = self.pool.get('product.product')

        ## Shipping Service
        prod_shipping_id = product_obj.search(cr,uid,[('default_code','=',context['shipping_product_default_code'])])
        if not prod_shipping_id:
            prod_shipping_id = self.createShippingProduct(cr,uid,id,context)
        else:
            prod_shipping_id = prod_shipping_id[0]
        print "prod_shipping_id: ",prod_shipping_id

        shipping_price = resultval.get('ShippingPrice',0.00)
        shiplineids = saleorderline_obj.search(cr,uid,[('order_id','=',saleorderid),('product_id','=',prod_shipping_id)])
        print 'shipping_price Before',shipping_price
        if shiplineids:
            shipping_price = float(shipping_price) + float(saleorderline_obj.browse(cr,uid,shiplineids[0]).price_unit)
            print 'shipping_price After',shipping_price
            saleorderline_obj.write(cr,uid,shiplineids[0],{'price_unit':shipping_price})
            return shiplineids[0]

        product = product_obj.browse(cr,uid,prod_shipping_id)

        shiporderlinevals = {
            'order_id' : saleorderid,
            'product_uom_qty' : 1,
            'product_uom' : product.product_tmpl_id.uom_id.id,
            'name' : product.product_tmpl_id.name,
            'price_unit' : shipping_price,
#            'delay' : product.product_tmpl_id.sale_delay,
            'invoiced' : False,
            'state' : 'confirmed',
            'product_id' : prod_shipping_id,
            'type': 'make_to_stock',
        }
        print "shiporderlinevals: ",shiporderlinevals
        shiplineid = saleorderline_obj.create(cr,uid,shiporderlinevals,context)
        cr.commit()
        return shiplineid
    
    def manageSaleOrder(self, cr, uid, id, shop_id, resultval, context):
        saleorder_obj = self.pool.get('sale.order')
        shop_obj = self.pool.get('sale.shop')
        partner_obj = self.pool.get('res.partner')
        payment_method_obj = self.pool.get('payment.method')

        payment_id = False
        if isinstance(shop_id, (int, long)):
            shop = shop_obj.browse(cr,uid,shop_id)
        else:
            shop = shop_id
        print "=====shop_id==$$$$$$$$=====>",shop
        print "**********resultval**************",resultval
        print "(((((((((((((",resultval['OrderId'],shop.prefix,shop.suffix,shop.name
        if context.get('order_search_clause',False):
            saleorderids = saleorder_obj.search(cr,uid,context['order_search_clause'])
        else:
            saleorderids = saleorder_obj.search(cr,uid,[('name','=',shop.prefix + resultval['OrderId'] + shop.suffix),('shop_id','=',shop.id)])

        print "base_ecommerce/sale => manageSaleOrder() saleorderids: ",saleorderids
        if saleorderids:
            saleorder = saleorder_obj.browse(cr,uid,saleorderids[0])
            if saleorder.invoiced:
                return False
            else:
                return saleorderids[0]
        partnerinvoiceaddress_id = self.updatePartnerInvoiceAddress(cr,uid,id,resultval) or False
        partner_id = partnerinvoiceaddress_id
        partnershippingaddress_id = self.updatePartnerShippingAddress(cr,uid,id,resultval) or False

        if not partner_id or not (partnershippingaddress_id or partnerinvoiceaddress_id):
            print "Invalid Partner Information!!!!!!!!!"
            ## Skip it since the address info is wrong
            return False

        pricelist_id = partner_obj.browse(cr,uid,partner_id)['property_product_pricelist'].id

#        carrier_ids = resultval.get('Carrier') and self.pool.get('delivery.carrier').search(cr,uid,[(context['shipping_code_key'],'=',resultval['Carrier'])])
#        if not carrier_ids:
#            carrier_ids = resultval.get('Carrier') and self.pool.get('delivery.carrier').search(cr,uid,[('name','=',resultval['Carrier'])])
#        carrier_id = carrier_ids[0] if carrier_ids else False
        carrier_id = False
        if context.get('date_format',False):
            date_order = time.strptime(resultval['PurchaseDate'], context['date_format'])
            date_order = time.strftime("%Y-%m-%dT%H:%M:%S.000Z",date_order)
        else:
            date_order = resultval['PurchaseDate']
        if resultval.get('PaymentMethod',False) and resultval['PaymentMethod'] != 'None':
            payment_ids = payment_method_obj.search(cr,uid,[('name','=',resultval['PaymentMethod'])])
            if payment_ids:
                payment_id = payment_ids[0]
            else:
                payment_id = payment_method_obj.create(cr, uid, {'name': resultval['PaymentMethod'], 'code': resultval['PaymentMethod']})
            
#        print "resultval['PaymentMethod']: ",resultval['PaymentMethod']
        ordervals = {
            'name' : resultval['OrderId'],
            'picking_policy' : shop.picking_policy or 'direct',
            'order_policy' : shop.order_policy or 'picking',
            'partner_order_id' : partnerinvoiceaddress_id,
            'partner_invoice_id' : partnerinvoiceaddress_id,
            'date_order' : date_order,
            'shop_id' : shop.id,
            'partner_id' : partner_id,
            'user_id' : uid,
            'partner_shipping_id' : partnershippingaddress_id,
            'shipped' : False,
            'state' : 'draft',
#            'invoice_quantity' : shop.invoice_quantity,
            'pricelist_id' : pricelist_id,
            'payment_method_id' : payment_id,
            'carrier_id': carrier_id or False,
            'unique_sales_rec_no': resultval.get('unique_sales_rec_no',False),
            'is_waiting_for_shipment': context.get('waiting_for_shipment',False),
        }
        if context.get('shopordervals',False):
            ordervals.update(context['shopordervals'])

        saleorderid = saleorder_obj.create(cr,uid,ordervals,context)
        message = _('SaleOrder %s created successfully' % ((shop.prefix or '') + resultval['OrderId'] + (shop.suffix or '')))
        self.log(cr, uid, shop_id, message)
        cr.commit()
        return saleorderid
    
    
    
    def createOrderIndividual(self, cr, uid, id, shop_id, resultval, context={}):
        print "========shop_id=====>",shop_id
        saleorder_obj = self.pool.get('sale.order')
        saleorderid = self.manageSaleOrder(cr, uid, id, shop_id, resultval, context)
        print "createOrderIndividual saleorderid: ",saleorderid

        if not saleorderid:
            return False
        
        if saleorder_obj.browse(cr,uid,saleorderid).state == 'draft':
            ### Order has been reversed bcoz in Sales order it comes in right order
            if resultval.get('ShippingPrice',False) and float(resultval['ShippingPrice']) > 0.00 :
                self.manageSaleOrderLineShipping(cr, uid, id, shop_id, saleorderid, resultval, context)

            if resultval.get('ItemTax',False) and float(resultval['ItemTax']) > 0.00 and context.get('create_tax_product_line',False):
                self.manageSaleOrderLineTax(cr, uid, id, shop_id, saleorderid, resultval, context)

            saleorderlineid = self.manageSaleOrderLine(cr, uid, id, shop_id, saleorderid, resultval, context)
            print "createOrderIndividual saleorderlineid: ",saleorderlineid

        cr.commit()
        return saleorderid
    
    def handleMissingOrders(self, cr, uid, shop_id, missed_resultvals, context={}):
        shop_obj = self.pool.get('sale.shop')
        company_id = self.pool.get('res.users').browse(cr,uid,uid).company_id.id
        defaults = {'company_id':company_id}
        count = 0
        while (missed_resultvals):
            count = count + 1 ### count is to make sure loop doesn't go into endless iteraiton
            if count > 3:
                break

            resultvals = missed_resultvals[:]

            prev_order_id = False
            prev_order_paid = False

            for resultval in resultvals:
                resultval = self.get_payment_method(cr, uid, shop_id, resultval)
                if not resultval.get('SellerSKU',False):
                    continue

#                try:
                saleorderid = self.createOrderIndividual(cr,uid,id,shop_id,resultval,context)
                print "saleorderid: ",saleorderid

                if not saleorderid:
                    continue
                prev_order_id = saleorderid
                prev_order_paid = resultval['paid']
                missed_resultvals.remove(resultval)
               #                except Exception, e:
#                print "handleMissingOrders Exception: ",e
#                if str(e).find('concurrent update') != -1:
#                    cr.rollback()
#                message = _("ImportLog Exception handleMissingOrders '%s': %s") % (str(e),resultval['OrderId'],)
#                shop_obj.log(cr, uid, shop_id, message)
#                cr.commit()
#                continue

                self.oe_status(cr, uid, saleorderid,resultval)
                cr.commit()

        return True
    
    def get_payment_method(self, cr, uid, shop, resultval):
        print "=====resultval============>",resultval
        pay_obj = self.pool.get('ecommerce.payment.method')
        pay_ids = pay_obj.search(cr, uid, [('shop_id', '=' , shop.id)])
        resultval.update({'confirm': False})
        resultval.update({'order_policy': shop.order_policy})
        print "=====resultval============>",resultval
        for pay in pay_obj.browse(cr, uid, pay_ids):
            methods = (pay.name).split(',')
            payment_method = resultval.get('PaymentMethod',False) and resultval['PaymentMethod'] or ''
            if payment_method in methods:
                resultval.update({'paid': pay.pay_invoice})
                resultval.update({'confirm':pay.val_order})
                resultval.update({'order_policy':pay.order_policy})
                break
            print "*****************************************************************"
            print "======payment_method============>",payment_method
            print "=======resultval['paid']========>",resultval['paid']
            print "======= resultval['confirm']========>", resultval['confirm']
            print "======= resultval['order_policy']=======>", resultval['order_policy']
            print "*****************************************************************"
        return resultval
    
#    def createOrder(self, cr, uid, shop, resultvals, context={}):
#        sale_order_obj = self.pool.get('sale.order')
#        saleorderid = False
#        company_id = self.pool.get('res.users').browse(cr,uid,uid).company_id.id
#        defaults = {'company_id':company_id}
#        
##        self.create_order_info(cr,uid,shop_id,context)
#        prev_order_id = False
#        prev_order_paid = False
#        missed_resultvals = []
#        missed_order_ids = []
#
#        for resultval in resultvals:
#            resultval = self.get_payment_method(cr, uid, shop, resultval)
#            context['import_type'] = 'api'
#            print "=====resultval=^^^^^^^^^^^^^^^^^^^**********************======>",resultval
#            if not resultval.get('SellerSKU',False):
#                continue
#            context['waiting_for_shipment'] = False
##            try:
#            saleorderid = self.createOrderIndividual(cr,uid,id,shop.id,resultval,context)
#
#            if not saleorderid:
#                continue
#            self.oe_status(cr, uid, saleorderid, resultval)
#            cr.commit()
#
#
##            except Exception, e:
##                print "base_ecommerce/sale.py createOrderDirect Exception: ",e
##                if str(e).find('concurrent update') != -1:
##                    missed_resultvals.append(resultval)
##                    missed_order_ids.append(resultval['OrderId'])
##                    cr.rollback()
##                    continue
##                cr.rollback()
##                message = _("ImportLog Exception createOrderDirect for '%s': %s") % (str(e),resultval['OrderId'],)
###                shop_obj.log(cr, uid, shop_id, message)
##                cr.commit()
#
# 
#        print "createOrderDirect missed_resultvals: ",missed_resultvals
#
#        self.handleMissingOrders(cr,uid,shop.id,missed_resultvals,context)
#
#        return True
    def createOrder(self, cr, uid, id, shop_id, resultvals, context={}):
        print "inside shoperp_instance createOrder"
        saleorderid = False
        order_data = []
        context['import_type'] = 'api'
        
        missed_resultvals = []
        missed_order_ids = []
        for resultval in resultvals:
            if isinstance(shop_id, (int, long)):
               shop_id =  self.browse(cr,uid,shop_id)
            resultval = self.get_payment_method(cr, uid, shop_id, resultval)
            if not resultval.get('SellerSKU',False):
                continue

            saleorderid = self.createOrderIndividual(cr,uid,id,shop_id,resultval,context)
            print "saleorderid: ",saleorderid

            if not saleorderid:
                continue
            order_data.append({'id':saleorderid, 'resultval':resultval})
            cr.commit()

#            except Exception, e:
#                print "base_ecommerce_connector/shoperp_instance.py createOrder Exception: ",e
#                if str(e).find('concurrent update') != -1:
#                    missed_resultvals.append(resultval)
#                    missed_order_ids.append(resultval['OrderId'])
#                    cr.rollback()
#                    continue
#            message = _("ImportLog Exception createOrder for '%s': %s") % (str(e),resultval['OrderId'],)
#                shop_obj.log(cr, uid, shop_id, message)
        order_ids = []
        for saleorderid in order_data:
            try:
                self.oe_status(cr, uid, saleorderid['id'], saleorderid['resultval'])
                order_ids.append( saleorderid['id'])
                cr.commit()
            except Exception, e:
                print "base_ecomerce_connector/shooperp_instance.py createOrder oe_status Exception: ",e
                cr.rollback()
                message = _("ImportLog Exception createOrder oe_status for '%s': %s") % (str(e),resultval['OrderId'],)
#                shop_obj.log(cr, uid, shop_id, message)
                cr.commit()
                continue

        print "createOrderDirect missed_resultvals: ",missed_resultvals

        self.handleMissingOrders(cr,uid,shop_id,missed_resultvals,context)

        return order_ids

sale_shop()

class sale_order(osv.osv):
    _inherit = 'sale.order'
    _columns = {
        'unique_sales_rec_no' : fields.char('Order Unique ID',size=100),
        'import_unique_id' : fields.char('Import ID',size=100),
        'payment_method_id': fields.many2one('payment.method','Payment Method'),
        'track_exported': fields.boolean('Track Exported')
    }
    _defaults = {
        'track_exported': False
    }
  
    def _get_sale_order_name(self,cr,uid,shop_id,name,context=None):
        shop_obj = self.pool.get('sale.shop')
        shop = shop_obj.browse(cr,uid,shop_id)
        if shop_id and not name.startswith(shop.prefix or '') and not name.endswith(shop.suffix or ''):
            return str(shop.prefix or '') + name + str(shop.suffix or '')
        print "_get_sale_order_name name: ",name
        return name

    def create(self, cr, uid, vals, context=None):
        if vals.get('shop_id',False) and vals.get('name'):
            vals.update({'name': self._get_sale_order_name(cr,uid,vals['shop_id'],vals['name'],context)})

        return super(sale_order, self).create(cr, uid, vals, context=context)
  
    def generate_payment_with_journal(self, cr, uid, journal_id, partner_id, amount, payment_ref, entry_name, date, should_validate, context, defaults=None):
      #  print "base_ecommerce inside generate_payment_with_journal"
        voucher_obj = self.pool.get('account.voucher')
        voucher_line_obj = self.pool.get('account.voucher.line')
        data = voucher_obj.onchange_partner_id(cr, uid, [], partner_id, journal_id, int(amount), False, 'receipt', date, context)['value']
     #   print "voucher data: ",data
        account_id = data['account_id']
        currency_id = context.get('currency_id',False)
        statement_vals = {
            'reference': 'ST_' + entry_name,
            'journal_id': journal_id,
            'amount': amount,
            'date' : date,
            'partner_id': partner_id,
            'account_id': account_id,
            'type': 'receipt',
            'currency_id': currency_id,
            'number': '/'
        }
        statement_id = voucher_obj.create(cr, uid, statement_vals, context)
        context.update({'type': 'receipt', 'partner_id': partner_id, 'journal_id': journal_id, 'default_type': 'cr'})
        line_account_id = voucher_line_obj.default_get(cr, uid, ['account_id'], context)['account_id']
        statement_line_vals = {
                                'voucher_id': statement_id,
                                'amount': amount,
                                'account_id': line_account_id,
                                'type': 'cr',
                               }
        statement_line_id = voucher_line_obj.create(cr, uid, statement_line_vals, context)

        return statement_id
  
sale_order()

class sale_order_line(osv.osv):
    _inherit = "sale.order.line"
    _columns = {
        'unique_sales_line_rec_no' : fields.char('Sales Line Record Number', size=256)
    }
sale_order_line()