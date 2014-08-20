# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

from osv import fields, osv
import datetime
import time
import math
class product_product(osv.osv):
    _inherit = 'product.product'

    def is_amazon_listing_availabe(self, cr, uid, id, context=None):
        if not self.browse(cr,uid,id).amazon_listing_ids:
            return True

        active_ids = self.pool.get('amazon.product.listing').search(cr,uid,[('product_id','=',id),('active_amazon','=',True)])
        if active_ids:
            return True
        else:
            return False

    def get_allocation(self, cr, uid, ids, context={}):
        print "jjjjjjjjjjjjjjjjjjjj in amazon"
        shop_obj = self.pool.get('sale.shop')
        history_obj = self.pool.get('product.allocation.history')
        prod_obj = self.browse(cr, uid, ids[0])
        if prod_obj.qty_available > 0:
            s = {}
            for rec in prod_obj.amazon_listing_ids:
                if not s.has_key(rec.shop_id.id):
                    s.update({rec.shop_id.id: 1})
                else:
                    s.update({rec.shop_id.id: s[rec.shop_id.id] + 1})
            shop_ids = s.keys()
            for record in shop_obj.browse(cr, uid, shop_ids):
                if record.alloc_type == 'fixed':
                    value = math.floor(record.alloc_value/s[record.id])
                else:
                    value = math.floor(math.floor((prod_obj.qty_available * record.alloc_value) / 100) / s[record.id])
                cr.execute('UPDATE amazon_product_listing set last_sync_stock = %s where product_id = %s and shop_id = %s',(value, ids[0], record.id, ))
                vals = {
                    'name': record.id,
                    'qty_allocate': value,
                    'date': datetime.datetime.now(),
                    'alloc_history_id': ids[0]
                }
                print history_obj.create(cr, uid, vals)
        res = super(product_product, self).get_allocation(cr, uid, ids, context)
        return True

    _columns = {
        'amazon_listing_ids': fields.one2many('amazon.product.listing','product_id','Amazon Listings'),
        'amazon_category': fields.many2one('product.attribute.set','Category'),
        'amazon_cat':fields.char('Item Type',size=64),
        'amazon_attribute_ids1': fields.one2many('product.attribute.info', 'amazon_product_id', 'Attributes'),
        'amazon_exported': fields.boolean('Amazon Exported'),
        'code_type':fields.char('UPC/ISBN',size=20),
        
        'amazon_description':fields.text('Amazon Description'),
        'platinum_keywords': fields.text('Platinum Keywords'),
        'search_keywords': fields.text('Search Keywords'),
        'style_keywords': fields.text('Style Keywords'),
        'bullet_point':fields.text('Bullet Point'),
        
        'orderitemid': fields.char('Orderitemid', size=16),
        'product_order_item_id': fields.char('Order_item_id', size=256),
        'amazon_brand':fields.char('Brand',size=64),
        'bullet_point':fields.text('Bullet Point'),
        'amazon_manufacturer':fields.char('Manufacturer',size=64),
        'amzn_condtn': fields.selection([('New','New'),('UsedLikeNew','Used Like New'),('UsedVeryGood','Used Very Good'),('UsedGood','UsedGood')
        ,('UsedAcceptable','Used Acceptable'),('CollectibleLikeNew','Collectible Like New'),('CollectibleVeryGood','Collectible Very Good'),('CollectibleGood','Collectible Good')
        ,('CollectibleAcceptable','Collectible Acceptable'),('Refurbished','Refurbished'),('Club','Club')],'Amazon Condition'),
        'amazon_updated_price':fields.float('Amazon Updated Price',digits=(16,2)),
        'amazon_prodlisting_ids': fields.one2many('amazon.product.listing', 'product_id','Product Listing'),
        
        'item_type': fields.many2one('product.category.type', 'Item Type')
    }
product_product()

class amazon_product_listing(osv.osv):
    _name = 'amazon.product.listing'
    _order = 'id desc'

    def get_product_available(self, cr, uid, asin , ids, context=None):
        if context == None:
            context = {}

        res = {}
        res = {}.fromkeys(ids, 0.0)
        # all moves from a location out of the set to a location in the set
        location_ids = self.pool.get('stock.location').search(cr,uid,[('usage','=','internal')])
        states= ['done']
        print 'asin',asin
        print 'ids',ids
        where = [tuple(location_ids),tuple(location_ids),tuple([asin]),tuple(ids),tuple(states)]
        date_str = False
        
        cr.execute(
            'select sum(product_qty), product_id, product_uom '\
            'from stock_move '\
            'where location_id NOT IN %s'\
            'and location_dest_id IN %s'\
            'and listing_id IN %s'\
            'and product_id IN %s'\
            'and state IN %s' + (date_str and 'and '+date_str+' ' or '') +''\
            'group by product_id,product_uom',tuple(where))
            
        results = cr.fetchall()
        print "results: ",results

        # all moves from a location in the set to a location out of the set
        cr.execute(
            'select sum(product_qty), product_id, product_uom '\
            'from stock_move '\
            'where location_id IN %s'\
            'and location_dest_id NOT IN %s '\
            'and listing_id IN %s'\
            'and product_id  IN %s'\
            'and state in %s' + (date_str and 'and '+date_str+' ' or '') + ''\
            'group by product_id,product_uom',tuple(where))
        results2 = cr.fetchall()
        print "results2: ",results2
        
        #TOCHECK: before change uom of product, stock move line are in old uom.

        total_quantity = 0.00
        for amount, prod_id, prod_uom in results:
            total_quantity += amount

        for amount, prod_id, prod_uom in results2:
            total_quantity -= amount

        return total_quantity
    
    def _get_asin_stock(self, cr, uid, ids, field_names=None, arg=False, context=None):
        print 'In Amazon stock',ids
        if context is None:
            context = {}
        res = {}

        for id in ids:
            res[id] = 0.0

        for id in ids:
            data = self.browse(cr,uid,id)
            if data.name:
                res[id] = self.get_product_available(cr, uid,data.name,[data.product_id.id],context=None)

        return res

#    def _get_current_stock(self, cr, uid, ids, field_names=None, arg=False, context=None):
#        print 'In Current Stock',ids
#        if context is None:
#            context = {}
#        res = {}
#        for id in ids:
#            res[id] = 0
#
#        for id in ids:
#            listing_id = self.search(cr,uid,[('id','=',id)])
#            if listing_id:
#                data = self.browse(cr,uid,id)
##                last_sync_stock = data.stock_sync_id.last_sync_stock or 0
#                total_sales = data.total_sales or 0
#                if data.name:
##                    print 'last_sync_stock',last_sync_stock
#                    print 'total_sales',total_sales
#                    res[id] = last_sync_stock - total_sales
#        return res

    def _get_total_sales_mfn(self, cr, uid, ids, field_names=None, arg=False, context=None):
        print 'In Total Sales Fba',ids
        product_obj = self.pool.get('product.product')

        if context is None:
            context = {}
        res = {}
        for id in ids:
            res[id] = 0

        for id in ids:
            listing_ids = self.search(cr,uid,[('id','=',id)])
            if listing_ids:
                data = self.browse(cr,uid,id)
                if data.last_sync_date and data.product_id:
                    result = product_obj._get_shop_sales_value(cr,uid,data.product_id.id,data.last_sync_date,False,'amazon_shop',context,data.name or False)
                    res[id] = result and int(result[0][0]) or 0

        return res

    def _get_percentage_sales(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for id in ids:
            res[id] = 0.0

        product_obj = self.pool.get('product.product')

        for listing in self.browse(cr,uid,ids):
            if not listing.product_id:
                continue

            currentTimeFrom = listing.product_id.date_from_fix
            print "_get_percentage_sales currentTimeFrom: ",currentTimeFrom
            currentTimeTo = listing.product_id.date_to_fix
            print "_get_percentage_sales currentTimeTo: ",currentTimeTo

            result = product_obj._get_shop_sales_value(cr,uid,listing.product_id.id,currentTimeFrom,currentTimeTo,'amazon_shop',context,listing.name)
            listing_sales = result and result[0][0] or 0.0

            result = product_obj._get_shop_sales_value_with_listing(cr,uid,listing.product_id.id,currentTimeFrom,currentTimeTo,'amazon_shop',context)
            amazon_sales = result and result[0][0] or 0.0

            if amazon_sales > 0.0:
                percentage_sales = (listing_sales / amazon_sales) * 100.0
            else:
                percentage_sales = 0.0
            
            res[listing.id] = percentage_sales
            
        return res

    def _get_average_rank(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for id in ids:
            res[id] = 0.0

        for listing in self.browse(cr,uid,ids):
            get_last_seven_ranks = '''SELECT name from amazon_product_listing_rank
                WHERE listing_id = %s
                limit 7''' % (listing.id)

            print 'get_last_seven_ranks',get_last_seven_ranks
            cr.execute(get_last_seven_ranks)
            amazon_ranks = filter(None, map(lambda x: x[0], cr.fetchall()))
            if len(amazon_ranks) > 0:
                total_rank = 0
                
                for amazon_rank in amazon_ranks:
                    total_rank += amazon_rank

                res[listing.id] = total_rank / len(amazon_ranks)

        return res
    
    _columns = {
        'name': fields.char('SKU', size=100, required=True),
        
        'asin':fields.char('ASIN',size=64),
        'title':fields.char('Title',size=50,required=True),
        'prod_dep':fields.text('Product Description'),
#        'price': fields.float('Price',required=True),
        'code_type':fields.char('UPC/ISBN',size=20),
        
        'listing_name': fields.char('Name', size=100),
        'fulfillment_channel': fields.selection([('AMAZON_NA', 'FBA'), ('DEFAULT', 'Default')], 'Fufillment Channel'),
        'product_id': fields.many2one('product.product','Product'),
        'shop_id': fields.many2one('sale.shop','Shop', required=True, domain=[('amazon_shop','=',True)]),
        'created_date': fields.datetime('Created Date'),
        
        'last_sync_price': fields.float('Price'),
        'stock_to_be_updated': fields.boolean('Stock To Be Updated',readonly=True),
        'price_to_be_updated': fields.boolean('Price To Be Updated',readonly=True),
        'listing_flag': fields.boolean('Listing Flag',readonly=True),
        'last_sync_date': fields.datetime('Last Sync Date'),
        'last_sync_stock': fields.integer('Last Sync Stock'),

        'last_rank_updated': fields.datetime('Last Rank Updated'),

        'added_stock': fields.integer('Stock Added',readonly=True),
        'percentage_sales': fields.function(_get_percentage_sales, method=True, type='float', string='Daily Sales (%)'),
        'last_mgr_update': fields.datetime('Last Manager Update'),
        'active_amazon':fields.boolean('Active'),
        'rank':fields.integer('Rank'),
        'fnsku':fields.char('FNSKU',size=30),
        'avg_seven_rank': fields.function(_get_average_rank, method=True, type='float', string='Average 7 days Rank'),
        'amazon_rank_ids': fields.one2many('amazon.product.listing.rank','listing_id','Amazon Rank'),
        'amazon_lowest_competitors': fields.one2many('lowest.product.competitors','listing_id','Amazon Rank'),

    }
  
    
amazon_product_listing()

class amazon_product_listing_rank(osv.osv):
    _name = 'amazon.product.listing.rank'
    _order = 'id desc'

    _columns = {
        'name': fields.integer('Rank',required=True),
        'rank_created_date': fields.datetime('Rank Updated On'),
        'listing_id': fields.many2one('amazon.product.listing','Amazon Listings'),
        'buybox_owner': fields.boolean('BuyBox Owner'),
        'buybox_price': fields.float('BuyBox Price'),
#        'item_condition': fields.selection([('New', 'New'), ('Used', 'Used'),('Collectible','Collectible'),('Refurbished','Refurbished')], 'Item Condition'),
        'category': fields.char('Category', size=256),
    }

amazon_product_listing_rank()

class lowest_product_competitors(osv.osv):
    _name = 'lowest.product.competitors'
    _description = "Amazon Product Competitors"

    _columns = {
        'listing_id': fields.many2one('amazon.product.listing','Amazon Listings'),
        'shipping_time': fields.selection([('14 or more days', '14 or more days'), ('8-13 days', '8-13 days'),('0-2 days','0-2 days'),('3-7 days','3-7 days')], 'Shipping Time'),
        'seller_feedback_count':fields.char('Seller Feedback Count',size=50),
        'sellerpositivefeedbackrating':fields.many2one('seller.positive.feedback.rating','Seller Positive Feedback Rating'),
        'no_offer_listingsconsidered':fields.integer('Number Of Offer Listings Considered'),
        'price': fields.float('Price'),
        'item_condition': fields.selection([('New', 'New'), ('Used', 'Used'),('Collectible','Collectible'),('Refurbished','Refurbished')], 'Item Condition'),
        'item_subcondition': fields.selection([('New','New'),('Good', 'Good'), ('Refurbished', 'Refurbished'),('Acceptable','Acceptable'),('Refurbished','Refurbished'),('Mint','Mint'),('VeryGood','VeryGood')], 'Item Sub Condition'),
        'fulfillment_channel': fields.selection([('Amazon','Amazon'),('Merchant', 'Merchant')], 'Fulfillment Channel'),
        'feedback_count':fields.char('Feedback Count',size=50),
        'ships_domestically':fields.boolean('Ships Domestically'),
        'last_sync_date': fields.datetime('Last Sync Date'),
    }

    _rec_name = 'price'

lowest_product_competitors()

class sellerpositivefeedbackrating(osv.osv):
    _name = 'seller.positive.feedback.rating'
    _columns = {
        'name':fields.char('Seller Positive Feedback Rating',size=100)
    }
sellerpositivefeedbackrating()

