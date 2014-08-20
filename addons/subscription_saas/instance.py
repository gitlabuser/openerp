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

class sales_channel_instance(osv.osv):
    _inherit = 'sales.channel.instance' 
    
    def create(self, cr, uid, vals, context=None):
        print "========in create666666666666666666=====>"
        para = self.pool.get("ir.config_parameter")

        if vals.get('module_id') == 'ebay_teckzilla':
            ebay_inst = para.get_param(cr, uid, "ecommerce.no_of_ebay_instance", context=context)
            cr.execute("select count(id) from sales_channel_instance where module_id = 'ebay_teckzilla'")
            ebay_query = cr.fetchall()
            ebay_ins_count = ebay_query[0][0]
            if int(ebay_inst) != 0 and int(ebay_inst) <= ebay_ins_count:
                raise osv.except_osv(('Error!'), ('You have only access to create '+ebay_inst+' ebay instance'))
            
        if vals.get('module_id') == 'oeoo_amazon':
            amazon_inst = para.get_param(cr, uid, "ecommerce.no_of_amazon_instance", context=context)
            cr.execute("select count(id) from sales_channel_instance where module_id = 'oeoo_amazon'")
            amazon_query = cr.fetchall()
            amazon_ins_count = amazon_query[0][0]
            if int(amazon_inst) != 0 and int(amazon_inst) <= amazon_ins_count:
                raise osv.except_osv(('Error!'), ('You have only access to create '+amazon_inst+' amazon instance'))
            
        if vals.get('module_id') == 'magento_teckzilla':
            magento_inst = para.get_param(cr, uid, "ecommerce.no_of_magento_instance", context=context)
            cr.execute("select count(id) from sales_channel_instance where module_id = 'magento_teckzilla'")
            magento_query = cr.fetchall()
            magento_ins_count = magento_query[0][0]
            if int(magento_inst) != 0 and int(magento_inst) <= magento_ins_count:
                raise osv.except_osv(('Error!'), ('You have only access to create '+magento_inst+' magento instance'))
            
        return super(sales_channel_instance, self).create(cr, uid, vals, context)
sales_channel_instance()