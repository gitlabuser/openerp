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

{
    "name" : "Base Ecommerce TeckZilla",
    "version" : "1.1",
    "depends" : ['base','sale','product','stock','sale_stock','delivery'],
    "author" : "TeckZilla",
    "description": """
    Base Module for All MarketPlaces Management\n
    """,
    "website" : "www.teckzilla.net",
    'images': [],
    "category" : "ecommerce",
    'summary': 'Base Module For All E-Commerce Modules',
    "demo" : [],
    "data" : [  
            'instance_view.xml',
            'sale_view.xml',
            'payment_view.xml',
            'log_view.xml',
            'import_sequence.xml',
            'attribute_view.xml',
            'base_menu_view.xml',
            'attribute_view.xml',
            'security/ir.model.access.csv',
            'wizard/update_marketplace_price_view.xml',
            'product_view.xml'
#            'ecommerce.payment.method.csv'
    ],
    'auto_install': False,
    "installable": True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

