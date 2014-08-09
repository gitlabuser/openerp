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
class product_attribute_option(osv.osv):
    _name = "product.attribute.option"
    _columns = {
            'name': fields.char('Label', size=255),
            'value':fields.char('Value', size=100),
            'attribute_id': fields.many2one('product.attribute', 'Attribute')
    }
product_attribute_option()

class product_attribute(osv.osv):
    _name = "product.attribute"
    
    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
        if not args:
            args = []
        if context is None:
            context = {}
        ids = []
        if name:
            ids = self.search(cr, user, [('attribute_code','=',name)] + args, limit=limit, context=context)
        if not ids:
            ids = self.search(cr, user, [('attribute_code',operator,name)] + args, limit=limit, context=context)
        return self.name_get(cr, user, ids, context)
  
    def name_get(self, cr, uid, ids, context=None):
        print "-------------->"
        if isinstance(ids, (list, tuple)) and not len(ids):
            return []
        if isinstance(ids, (long, int)):
            ids = [ids]
        reads = self.read(cr, uid, ids, ['attribute_code','parent_id'], context=context)
        res = []
        for record in reads:
            name = record['attribute_code']
            if record['parent_id']:
                if name:
                   name = record['parent_id'][1]+' / '+ name
            res.append((record['id'], name))
        return res
    
    def _name_get_fnc(self, cr, uid, ids, prop, unknow_none, context=None):
        res = self.name_get(cr, uid, ids, context=context)
        return dict(res)
#        return {}

    def get_leaf(self, cr, uid, ids, context={}):
        res = True
        for rec in self.browse(cr, uid, ids):
#            print "====rec.id==>",rec.id
            attrs_ids = self.search(cr, uid, [('parent_id','=',rec.id)])
            if not attrs_ids:
                self.write(cr, uid,rec.id,{'is_leaf': True})
        return res
    
    _columns = {
            'attribute_code': fields.char('Name', size=255),
            'complete_name': fields.function(_name_get_fnc, type="char", string='Complete Name'),
            'attr_set_id': fields.many2one('product.attribute.set', 'Attribute Set'),
            'option_ids': fields.one2many('product.attribute.option', 'attribute_id', 'Options'),
            'parent_id': fields.many2one('product.attribute', 'Parent'),
            'pattern': fields.selection([('choice', 'Choice'),
                        ('restricted', 'Ristricted'),
                        ('other', 'Other')], 'Product Type Pattern'),
      
           'is_leaf': fields.boolean("Leaf"),
           'import': fields.boolean("Imported")
            
    }
    
    
    _defaults = {
        'parent_id': False,
        'is_leaf': False
        
    }
product_attribute()

class product_attribute_set(osv.osv):
    _name = "product.attribute.set"
    _columns = {
            'name': fields.char('Name', size=255),
            'code': fields.char('Code', size=255),
            'shop_id': fields.many2one('sale.shop', 'Shop'),
            'attribute_ids': fields.one2many('product.attribute', 'attr_set_id', 'Attributes')
    }
product_attribute_set()


class product_attribute_info(osv.osv):
    _name="product.attribute.info"
    _columns={
        'name': fields.many2one('product.attribute', 'Attribute', required=True),
        'value': fields.many2one('product.attribute.option', 'Values'),
        'value_text': fields.text('Text')
    }
product_attribute_info()