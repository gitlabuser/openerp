# -*- coding: utf-8 -*-

{
    "name" : "Amazon Connector",
    "version" : "1.1.1",
    "depends" : ["base",'base_ecommerce',"product","sale",'product_images_olbs'],
    "author" : "oeoo",
    "description": """
        Amazon Management\n
        Provide Integration with Amazon\n
        Import Orders\n
        Import products\n
        Export Products\n
        Update Order Status\n
        Import Price/Stock\n
        Export Price/Stock\n
    """,
    "website" : "www.oeoo.me",
    'images': [],
    "category" : "ecommerce",
    'summary': 'Amazon Integration of Oeoo',
    "demo" : [],
    "data" : [  
             'security/ir.model.access.csv',
             'attribute_view.xml',
             'sequence/inbound_sequence.xml',
             'wizard/add_amazon_asin_view.xml',
             'wizard/import_category_view.xml',
             'amazon_view.xml',
             'delivery_view.xml',
             'product_view.xml',
             'sale_view.xml',
             'manage_amazon_listing_view.xml',
             'product_images_view.xml',
#             'amazon_fba_view.xml',
             'amazon_inbound_shipment_view.xml',
            'wizard/update_marketplace_price_view.xml'
    ],
    'auto_install': False,
    "installable": True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:


