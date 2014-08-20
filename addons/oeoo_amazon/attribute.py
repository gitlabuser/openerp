# -*- coding: utf-8 -*-

from osv import osv, fields
class product_attribute_info(osv.osv):
    _inherit="product.attribute.info"
    _columns={
        'manage_amazon_product_id': fields.many2one('upload.amazon.products', 'Product'),
        'amazon_product_id': fields.many2one('product.product', 'Product')
    }
product_attribute_info()

class product_attribute_set(osv.osv):
    _inherit = "product.attribute.set"
    _columns = {
            'categ_type_ids': fields.one2many('product.category.type', 'attr_type_id', 'Attributes')
    }
product_attribute_set()

class product_category_type(osv.osv):
    _name = "product.category.type"
    _columns = {
        'attr_type_id': fields.many2one('product.attribute.set','Attribute Type'),
        'name': fields.char('Name', size=1000),
        'code_type': fields.char('Type'),
        'node': fields.char('Node'),
    }
product_category_type()