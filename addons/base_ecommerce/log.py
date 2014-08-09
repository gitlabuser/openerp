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

class ecommerce_logs(osv.osv):
    _name = "ecommerce.logs"
    _columns = {
       'start_datetime':fields.datetime('Start time', readonly="1"),
       'end_datetime': fields.datetime('End Date', readonly="1"),
       'shop_id': fields.many2one('sale.shop', 'Shop',readonly="1"),
       'message': fields.text('Message', readonly="1"),
       'activity': fields.selection([
                                    ('import_orders','Import Orders'),
                                    ('update_order_status','Update Order Status'),
                                    ('import_price','Import Price'),
                                    ('export_price','Export Price'),
                                    ('import_stock','Import Stock'),
                                    ('export_stock','Export Stock'),
                                    ], 'Activity')
    }
ecommerce_logs()
    