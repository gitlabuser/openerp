# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Business Applications
#    Copyright (C) 2004-2012 OpenERP S.A. (<http://openerp.com>).
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

from openerp.osv import fields, osv

class ecommerce_config_settings(osv.osv_memory):
    """ 
    This class for the basic configaration for Ecommerce Module.
    Like Which module is need to install and how many instance of this module are require.
    how many user can access it.
    """
    _name = 'ecommerce.module.config.settings'
    _inherit = 'res.config.settings'
    _columns = {
        'module_magento_teckzilla': fields.boolean('Magento'),
        'no_of_magento_instance': fields.char('No of Magento Instance', size=3),
        'module_ebay_teckzilla': fields.boolean('Ebay'),
        'no_of_ebay_instance': fields.char('No of Ebay Instance',size=3),
        'module_oeoo_amazon' : fields.boolean('Amazon'),
        'no_of_amazon_instance': fields.char('No of Amazon Instance',size=3),
        'module_royalmail_teckzilla': fields.boolean('RoyalMail'),
        'module_dpd_teckzilla': fields.boolean('DPD'),
        'module_fedex_teckzilla': fields.boolean('Fedex'),
        'module_interlink_teckzilla': fields.boolean('Interlink'),
        'no_of_users': fields.char('No of Users',size=3),
        'user_id': fields.many2one('res.users','User')
    }
    _defaults = {
          'user_id': 1
    }
    def execute(self, cr, uid, ids, context=None):
        wiz_obj = self.browse(cr, uid, ids[0])
        m_obj = self.pool.get('module.selection')
        m_ids = m_obj.search(cr, uid, [('module','=','magento_teckzilla')])
        print "========module_magento_teckzilla======>",wiz_obj.module_magento_teckzilla
        if m_ids:
            m_obj.write(cr, uid, m_ids[0], {'is_installed': wiz_obj.module_magento_teckzilla, 'no_instance':wiz_obj.no_of_magento_instance}) 
        else:
            m_obj.create(cr, uid,{'name': 'Magento','module':'magento_teckzilla','is_installed': wiz_obj.module_magento_teckzilla, 'no_instance':wiz_obj.no_of_magento_instance, 'code': 1}) 
        me_ids = m_obj.search(cr, uid, [('module','=','ebay_teckzilla')])
        if me_ids:
            m_obj.write(cr, uid, me_ids[0], {'is_installed': wiz_obj.module_ebay_teckzilla, 'no_instance':wiz_obj.no_of_ebay_instance}) 
        else:
            m_obj.create(cr, uid,{'name': 'Ebay','module':'ebay_teckzilla','is_installed': wiz_obj.module_ebay_teckzilla, 'no_instance':wiz_obj.no_of_ebay_instance, 'code': 2}) 
        ma_ids = m_obj.search(cr, uid, [('module','=','oeoo_amazon')])
        if ma_ids:
            m_obj.write(cr, uid, ma_ids[0], {'is_installed': wiz_obj.module_oeoo_amazon, 'no_instance':wiz_obj.no_of_amazon_instance}) 
        else:
            m_obj.create(cr, uid,{'name': 'Amazon','module':'oeoo_amazon','is_installed': wiz_obj.module_oeoo_amazon, 'no_instance':wiz_obj.no_of_amazon_instance, 'code': 3}) 
        return super(ecommerce_config_settings,self).execute(cr, uid, ids, context=context)
  # set and get method for fields  
    def get_default_module_magento_teckzilla(self, cr, uid, ids, context=None):
        module_magento_teckzilla = self.pool.get("ir.config_parameter").get_param(cr, uid, "ecommerce.module_magento_teckzilla", context=context)
        return {'module_magento_teckzilla': module_magento_teckzilla}

    def set_module_magento_teckzilla(self, cr, uid, ids, context=None):
        config_parameters = self.pool.get("ir.config_parameter")
        record = self.browse(cr, uid, ids[0], context=context)
        config_parameters.set_param(cr, uid, "ecommerce.module_magento_teckzilla", record.module_magento_teckzilla or '', context=context)
        
    def get_default_no_of_magento_instance(self, cr, uid, ids, context=None):
        no_of_magento_instance = self.pool.get("ir.config_parameter").get_param(cr, uid, "ecommerce.no_of_magento_instance", context=context)
        return {'no_of_magento_instance': no_of_magento_instance}

    def set_no_of_magento_instance(self, cr, uid, ids, context=None):
        config_parameters = self.pool.get("ir.config_parameter")
        record = self.browse(cr, uid, ids[0], context=context)
        config_parameters.set_param(cr, uid, "ecommerce.no_of_magento_instance", record.no_of_magento_instance or '0', context=context)
        
    def get_default_module_ebay_teckzilla(self, cr, uid, ids, context=None):
        module_ebay_teckzilla = self.pool.get("ir.config_parameter").get_param(cr, uid, "ecommerce.module_ebay_teckzilla", context=context)
        return {'module_ebay_teckzilla': module_ebay_teckzilla}

    def set_module_ebay_teckzilla(self, cr, uid, ids, context=None):
        config_parameters = self.pool.get("ir.config_parameter")
        record = self.browse(cr, uid, ids[0], context=context)
        config_parameters.set_param(cr, uid, "ecommerce.module_ebay_teckzilla", record.module_ebay_teckzilla or '', context=context)
        
    def get_default_no_of_ebay_instance(self, cr, uid, ids, context=None):
        no_of_ebay_instance = self.pool.get("ir.config_parameter").get_param(cr, uid, "ecommerce.no_of_ebay_instance", context=context)
        return {'no_of_ebay_instance': no_of_ebay_instance}

    def set_no_of_ebay_instance(self, cr, uid, ids, context=None):
        config_parameters = self.pool.get("ir.config_parameter")
        record = self.browse(cr, uid, ids[0], context=context)
        config_parameters.set_param(cr, uid, "ecommerce.no_of_ebay_instance", record.no_of_ebay_instance or '0', context=context)
        
    def get_default_module_oeoo_amazon(self, cr, uid, ids, context=None):
        module_oeoo_amazon = self.pool.get("ir.config_parameter").get_param(cr, uid, "ecommerce.module_oeoo_amazon", context=context)
        return {'module_oeoo_amazon': module_oeoo_amazon}

    def set_default_module_oeoo_amazon(self, cr, uid, ids, context=None):
        config_parameters = self.pool.get("ir.config_parameter")
        record = self.browse(cr, uid, ids[0], context=context)
        config_parameters.set_param(cr, uid, "ecommerce.module_oeoo_amazon", record.module_oeoo_amazon or '', context=context)    
    
    def get_default_no_of_amazon_instance(self, cr, uid, ids, context=None):
        no_of_amazon_instance = self.pool.get("ir.config_parameter").get_param(cr, uid, "ecommerce.no_of_amazon_instance", context=context)
        return {'no_of_amazon_instance': no_of_amazon_instance}

    def set_no_of_amazon_instance(self, cr, uid, ids, context=None):
        config_parameters = self.pool.get("ir.config_parameter")
        record = self.browse(cr, uid, ids[0], context=context)
        config_parameters.set_param(cr, uid, "ecommerce.no_of_amazon_instance", record.no_of_amazon_instance or '0', context=context)
        
    def get_default_module_royalmail_teckzilla(self, cr, uid, ids, context=None):
        module_royalmail_teckzilla = self.pool.get("ir.config_parameter").get_param(cr, uid, "ecommerce.module_royalmail_teckzilla", context=context)
        return {'module_royalmail_teckzilla': module_royalmail_teckzilla}

    def set_module_royalmail_teckzilla(self, cr, uid, ids, context=None):
        config_parameters = self.pool.get("ir.config_parameter")
        record = self.browse(cr, uid, ids[0], context=context)
        config_parameters.set_param(cr, uid, "ecommerce.module_royalmail_teckzilla", record.module_royalmail_teckzilla or '', context=context)
    
    def get_default_module_dpd_teckzilla(self, cr, uid, ids, context=None):
        module_dpd_teckzilla = self.pool.get("ir.config_parameter").get_param(cr, uid, "ecommerce.module_dpd_teckzilla", context=context)
        return {'module_dpd_teckzilla': module_dpd_teckzilla}

    def set_module_dpd_teckzilla(self, cr, uid, ids, context=None):
        config_parameters = self.pool.get("ir.config_parameter")
        record = self.browse(cr, uid, ids[0], context=context)
        config_parameters.set_param(cr, uid, "ecommerce.module_dpd_teckzilla", record.module_dpd_teckzilla or '', context=context)
        
    def get_default_module_fedex_teckzilla(self, cr, uid, ids, context=None):
        module_fedex_teckzilla = self.pool.get("ir.config_parameter").get_param(cr, uid, "ecommerce.module_fedex_teckzilla", context=context)
        return {'module_fedex_teckzilla': module_fedex_teckzilla}

    def set_module_fedex_teckzilla(self, cr, uid, ids, context=None):
        config_parameters = self.pool.get("ir.config_parameter")
        record = self.browse(cr, uid, ids[0], context=context)
        config_parameters.set_param(cr, uid, "ecommerce.module_fedex_teckzilla", record.module_fedex_teckzilla or '', context=context)
        
    def get_default_module_interlink_teckzilla(self, cr, uid, ids, context=None):
        module_interlink_teckzilla = self.pool.get("ir.config_parameter").get_param(cr, uid, "ecommerce.module_interlink_teckzilla", context=context)
        return {'module_interlink_teckzilla': module_interlink_teckzilla}

    def set_module_interlink_teckzilla(self, cr, uid, ids, context=None):
        config_parameters = self.pool.get("ir.config_parameter")
        record = self.browse(cr, uid, ids[0], context=context)
        config_parameters.set_param(cr, uid, "ecommerce.module_interlink_teckzilla", record.module_interlink_teckzilla or '', context=context)
        
    def get_default_no_of_users(self, cr, uid, ids, context=None):
        no_of_users = self.pool.get("ir.config_parameter").get_param(cr, uid, "ecommerce.no_of_users", context=context)
        return {'no_of_users': no_of_users}

    def set_no_of_users(self, cr, uid, ids, context=None):
        config_parameters = self.pool.get("ir.config_parameter")
        record = self.browse(cr, uid, ids[0], context=context)
        config_parameters.set_param(cr, uid, "ecommerce.no_of_users", record.no_of_users or '0', context=context)
        
ecommerce_config_settings()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
