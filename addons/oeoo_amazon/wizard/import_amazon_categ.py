from osv import fields, osv
from tools.translate import _
import xml.etree.ElementTree as ET
from cStringIO import StringIO

class import_amazon_categ(osv.osv_memory):
    _name = "import.amazon.categ"
    _columns = {
        'name': fields.char('File', size=500)
    }
    def import_category(self, cr, uid, ids, context={}):
        attrs_set_obj = self.pool.get('product.attribute.set')
        attrs_obj = self.pool.get('product.attribute')
        attrs_option_obj = self.pool.get('product.attribute.option') 
        imp_obj = self.browse(cr, uid, ids[0])
        tree = ET.parse('/opt/UKxsd/'+ imp_obj.name)
        cat = (imp_obj.name).split('.')[0]
        root = tree.getroot()
        cnt = 0
        set_id = False
        flag = 0
        att_id = False
        for child in root:
            cnt = 0
            parent_id = False
            
            for neighbor_data in child.iter():
#                print "---------------start--------------------------------"
                neighbor = neighbor_data.attrib
#                print "==========neighbor========>",neighbor
                if neighbor.has_key('name') or neighbor.has_key('ref'):
                    cnt = cnt + 1
                    if cat == neighbor.get('name', False):
                        flag = 1
                        at_set_ids = attrs_set_obj.search(cr, uid, [('name','=',neighbor.get('name', False))])
                        if at_set_ids:
                            set_id = at_set_ids[0]
                        else:
                            set_id = attrs_set_obj.create(cr, uid, {'name': neighbor.get('name', False)})
                            print'wronggggggggggggggggggggg1'
                    if flag == 1 and cnt == 1:
                        if neighbor.has_key('type'):
#                            print "============neighbor.get('type', False)[:-6]======>",neighbor.get('type', False)[:-6]
#                            print "============neighbor.get('type', False)[:-10]======>",neighbor.get('type', False)[:-10]
                            att_ids = attrs_obj.search(cr, uid, [('attribute_code','in',[neighbor.get('type', False)[:-6], neighbor.get('type', False)[:-10], neighbor.get('type', False),neighbor.get('ref', False)]),('attr_set_id','=',set_id)])
                        else:
#                            print "============neighbor.get('name', False)[:-6]======>",neighbor.get('name', False)[:-6]
#                            print "============neighbor.get('name', False)[:-10]======>",neighbor.get('name', False)[:-10]
                            att_ids = attrs_obj.search(cr, uid, [('attribute_code','in',[neighbor.get('name', False)[:-6], neighbor.get('name', False)[:-10], neighbor.get('name', False), neighbor.get('ref', False)]),('attr_set_id','=',set_id)])
#                        print "==============att_ids=flag=*************========>",att_ids
#                        print "==============att_ids=flag=*************========>",set_id
                        if att_ids:
                            parent_id = att_ids[0]
                            att_id = att_ids[0]
                        else:
                            parent_id = False
                    else: 
                        if neighbor.has_key('type'):
                            att_ids = attrs_obj.search(cr, uid, [('attribute_code','in',[neighbor.get('type', False) and neighbor.get('type', False)[:-6], neighbor.get('type', False) and neighbor.get('type', False)[:-10], neighbor.get('type', False),neighbor.get('ref', False)]),('attr_set_id','=',set_id),('parent_id','=',parent_id)])
                            name = neighbor.get('type', False)
                        else:
                            att_ids = attrs_obj .search(cr, uid, [('attribute_code','in',[neighbor.get('name', False) and neighbor.get('name', False)[:-6], neighbor.get('type', False) and neighbor.get('type', False)[:-10], neighbor.get('name', False),neighbor.get('ref', False)]),('attr_set_id','=',set_id),('parent_id','=',parent_id)])
                            name = False
#                        print "==============att_ids==*************========>",att_ids
                        if not att_ids:
                            att_vals = {
                                'attribute_code': name or neighbor.get('name', False) or neighbor.get('ref', False),
                                'attr_set_id': set_id,
                                'parent_id': parent_id
                            }
                            att_id = attrs_obj.create(cr, uid, att_vals)
                            print'wronggggggggggggggggggggggggggggggggggg2'
#                            print "========att_vals======>",att_vals
                        else:
                            att_id = att_ids[0]
#                    print "=======att_id**************=========>",att_id
                if len(neighbor) == 1 and neighbor.has_key('value'):
                    op_ids = attrs_option_obj.search(cr, uid, [('name','=',neighbor.get('value', False)),('attribute_id','=',att_id)])
                    if not op_ids:
                        op_vals = {
                            'name': neighbor.get('value', False),
                            'attribute_id': att_id,
                            'value': neighbor.get('value', False)
                        }
                        op_id = attrs_option_obj.create(cr, uid, op_vals)
#                        print "=========op_vals========>",op_vals
                        print 'wronggggggggggggggggggggggggggggggggggggggggg3'
                
        attrs_Flag_ids = attrs_obj.search(cr, uid, [])
        attrs_obj.get_leaf(cr, uid, attrs_Flag_ids)
#        for child in root:
#            print'neighbor_datad===',child.getchildren()
#            for m in child.getchildren():
#                print'm',m.getchildren()
#                for v in m.getchildren():
#                    print'v',v.getchildren()
#                    for j in v.getchildren():
#                        print'j',j.getchildren()
#                        for f in j.getchildren():
#                             print'f==',f.getchildren()[1:]
#                             nn=f.getchildren()[1:]
#                             for d in f.getchildren():
#                                 print'd--',d.getchildren()
#                                 for k in d.ge

                        
            
#            for neighbor_data in child.iter():
#                    print'neighbor_datad===',neighbor_data
#
##                for neighbor_datad in neighbor_data.iter():
#                    print'neighbor_datad===',neighbor_data.attrib
##                if neighbor.has_key('name')=='ProductType':
##                     ij
        product_type_lst=[]
        for child in root:
            cnt = 0
            parent_id = False
            
            for neighbor_data in child.iter():
                
                neighbor = neighbor_data.attrib
                
#                print "==========neighbor========>",len(neighbor)
                if len(neighbor)==1:
                    if neighbor.has_key('ref'):
#                        print "==========neighbor========>",neighbor
                        product_type_lst.append(neighbor['ref'])
                    
        print product_type_lst
        print'lllll', context['active_ids']

        product_type_ids=attrs_obj.search(cr, uid, [('attribute_code','=','ProductType'),('attr_set_id','=',context['active_ids'][0])])
        print'product_type_ids',product_type_ids
        
        if len(product_type_ids):
            cnt=0
            for p_type in product_type_lst:
                att_option_search=attrs_option_obj.search(cr,uid,[('name','=',p_type),('value','=',p_type),('attribute_id','=',product_type_ids[0])])
                if not len(att_option_search):
                    print'i will createeeee'
                    new_att_id=attrs_option_obj.create(cr,uid,{'name':p_type,'value':p_type,'attribute_id':product_type_ids[0]})
                    print'ggujgfjgfj',new_att_id
                    cnt=cnt+1
                    print'-------',cnt
        return True
import_amazon_categ()
