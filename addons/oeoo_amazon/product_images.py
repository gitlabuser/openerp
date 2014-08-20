from osv import fields, osv


class product_images(osv.osv):
    _inherit = "product.images"
    
    _columns = {
#        'url_location':fields.char('Full URL', size=256),
        'is_amazon': fields.boolean('Amazon Exported')
    }

product_images()