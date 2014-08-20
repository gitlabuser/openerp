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

from openerp.osv import osv, fields

class sales_channel_instance(osv.osv):
    """ For instance of Sales Channel"""
    _name = 'sales.channel.instance'
    
    def _get_installed_module(self, cr, uid, context={}):
        sel_obj = self.pool.get('module.selection')
        sele_ids = sel_obj.search(cr, uid, [('is_installed','=',True)])
        select = []
        for s in sel_obj.browse(cr, uid, sele_ids):
            select.append((str(s.module),s.name))
        print "+++++++++",select
        return select
    _columns = {
       'name' : fields.char('Name',size=64, required=True),
#       'module_id': fields.many2one('module.selection', 'Sales Channels', domain=[('is_installed','=',True)], required=True),
       'module_id': fields.selection(_get_installed_module,'Module', size=100)
    }
    
    
    def get_module_id(self, cr, uid, ids, module_id, context={}):
        return {'value': {'m_id': module_id}}
    
    def create_stores(self, cr, uid, ids, context):
        """ For create store of Sales Channel """
        (instances,) = self.browse(cr, uid, ids, context)  
        shop_obj = self.pool.get('sale.shop')
        shop_ids = shop_obj.search(cr,uid,[('instance_id','=',ids[0])])
        payment_ids = self.pool.get('account.payment.term').search(cr,uid,[])
        if not shop_ids:
            shop_data = {
                        'sale_channel_shop': True,
                        'name': instances.name + ' Shop',
                        'payment_default_id':payment_ids[0],
                        'warehouse_id':1,
                        'instance_id':ids[0],
                        'order_policy':'prepaid'
            }
            shop_id = shop_obj.create(cr,uid,shop_data)
        else:
            shop_id = shop_ids[0]
        return shop_id
sales_channel_instance()
 
class module_selection(osv.osv):
    """ Manage selection for Multi Sales Channel"""
    _name="module.selection"
    _columns = {
        'name': fields.char('Name',size=64),
        'module': fields.char('Module', size=255),
        'is_installed': fields.boolean('install'),
        'no_instance': fields.integer('Instance'),
        'code': fields.integer('Code')
    }
module_selection()