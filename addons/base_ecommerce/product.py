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

class product_product(osv.osv):
    _inherit = 'product.product'
    def get_allocation(self, cr, uid, ids, context={}):
        print "jjjjjjjjjjjjjjjjjjjj"
        return True
    _columns = {
        'allocation_history_id': fields.one2many('product.allocation.history', 'alloc_history_id', 'Allocation History', readonly=True)
    }
product_product()

class product_allocation_history(osv.osv):
    _name = 'product.allocation.history'
    _columns = {
        'date': fields.datetime('Date of Allocation', readonly=True),
        'name': fields.many2one('sale.shop', 'Shop', readonly=True),
        'alloc_history_id': fields.many2one('product.product','Product'),
        'qty_allocate': fields.float('Allocated Quantity', readonly=True)
    }
product_product()