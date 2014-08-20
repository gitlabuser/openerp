from osv import fields, osv
from tools.translate import _
import logging
import socket
import time
from datetime import timedelta,datetime
import datetime
import mx.DateTime as dt
import netsvc
#logger = netsvc.Logger()
import cStringIO
import StringIO
from urllib import urlencode
import Image
import os
from base64 import b64decode
from tools.translate import _
import urllib
import base64
from operator import itemgetter
from itertools import groupby
import logging
import cgi
from PIL import Image, ImageDraw ,ImageFont
logger = logging.getLogger('manage_amazon_listing')


class  upload_amazon_products(osv.osv):
    _name = "upload.amazon.products"

    def upload_amazon_products(self, cr, uid, ids, context=None):
        print"*****************************8s"
        amazon_api_obj = self.pool.get('amazonerp.osv')
        sale_shop_obj=self.pool.get('sale.shop')
        release_date = datetime.datetime.now()
        release_date = release_date.strftime("%Y-%m-%dT%H:%M:%S")
        date_string = """<LaunchDate>%s</LaunchDate>
                         <ReleaseDate>%s</ReleaseDate>"""%(release_date,release_date)
            
        for product in self.browse(cr,uid,ids):
            merchant_string = ''
            standard_product_string = ''
            desc = ''
            log_id = 0
            instance_obj = product.shop_id.instance_id
            warehouse_id = product.shop_id.warehouse_id.id
            location_id = self.pool.get('stock.warehouse').browse(cr,uid,warehouse_id).lot_stock_id.id
            merchant_string ="<MerchantIdentifier>%s</MerchantIdentifier>"%(instance_obj.aws_merchant_id)
            message_information = ''
            message_id = 1
            print"_______",product.id
            use_id=product.id
            print"++++++++++++",product.prod_listing_ids
            print"___", product.prod_listing_ids
            for each_product in product.prod_listing_ids:
                print"*********",each_product
                product_id=each_product.product_id
                print"============", product_id
                print each_product.product_id.amazon_cat
                print each_product.product_asin.asin
                item_type=each_product.product_id.amazon_cat
                product_nm = each_product.product_id.name_template
                product_sku = each_product.product_asin.name.strip(" ")
#                function_call = sale_shop_obj._my_value(cr, uid,location_id,each_product.id,context={})
#                quantity = str(function_call).split('.')

                if each_product.product_asin.title:
                    title=each_product.product_asin.title
                else:
                    title = each_product.product_id.name_template
                if each_product.product_asin.prod_dep:
                    sale_description = each_product.product_asin.prod_dep
                else:
                    sale_description = each_product.product_id.amazon_description
                if sale_description:
                    desc = "<Description><![CDATA[%s]]></Description>"%(sale_description)

                product_asin = each_product.product_asin.asin

                if each_product.is_new_listing:
                    if not each_product.product_asin.code_type:
                        raise osv.except_osv(_('Error'), _('UPC Required!!'))

                    standard_product_string = """
                    <StandardProductID>
                    <Type>UPC</Type>
                    <Value>%s</Value>
                    </StandardProductID>
                    """%(each_product.product_asin.code_type)
                else:
                    if not product_asin:
                        raise osv.except_osv(_('Error'), _('ASIN Required!!'))

                    standard_product_string = """
                    <StandardProductID>
                    <Type>ASIN</Type>
                    <Value>%s</Value>
                    </StandardProductID>
                    """%(product_asin)

                platinum_keywords = ''
                if each_product.product_id.platinum_keywords:
                    platinum_keyword_list = each_product.product_id.platinum_keywords.split('|')
                    for keyword in platinum_keyword_list:
                        platinum_keywords += '<PlatinumKeywords><![CDATA[%s]]></PlatinumKeywords>'%(keyword)
                if platinum_keywords == '':
                    platinum_keywords = '<PlatinumKeywords>No Keywords</PlatinumKeywords>'

                search_term = ''
                if each_product.product_id.search_keywords:
                    search_term_list = each_product.product_id.search_keywords.split('|')
                    for keyword_search in search_term_list:
                      search_term += '<SearchTerms><![CDATA[%s]]></SearchTerms>'%(keyword_search)


                style_keywords = ''
                if each_product.product_id.style_keywords:
                    style_keyword_list = each_product.product_id.style_keywords.split('|')
                    for keyword_style in style_keyword_list:
                            style_keywords += '<StyleKeywords><![CDATA[%s]]></StyleKeywords>'%(keyword_style)
                if style_keywords == '':
                    style_keywords = '<StyleKeywords>No Keywords</StyleKeywords>'

                message_information += """<Message><MessageID>%s</MessageID>
                                            <OperationType>Update</OperationType>
                                            <Product>
                                            <SKU>%s</SKU>%s
                                            <ProductTaxCode>A_GEN_NOTAX</ProductTaxCode>
                                            %s<DescriptionData>
                                            <Title><![CDATA[%s]]></Title>"""%(message_id,product_sku,standard_product_string,date_string,title)

                if not each_product.product_id.bullet_point:
                    raise osv.except_osv(_('Error'), _('Plz Enter Bullet Points!!'))

                bullet_points = ''
                bullets=each_product.product_id.bullet_point.split('|')
                for bullet in bullets:
                    bullet_points +="""<BulletPoint><![CDATA[%s]]></BulletPoint>"""%(bullet)


                if not each_product.product_id.amazon_brand:
                    raise osv.except_osv(_('Error'), _('Plz Enter Brand!!'))
                message_information += """<Brand><![CDATA[%s]]></Brand>"""%(each_product.product_id.amazon_brand)
                message_information += desc
                message_information += bullet_points
#                    message_information +="""<MSRP currency="USD">%s</MSRP>"""%(each_product.product_asin.price)
                message_information +="""<Manufacturer><![CDATA[%s]]></Manufacturer>"""%(each_product.product_id.amazon_manufacturer)
                message_information +="""<MfrPartNumber>LE</MfrPartNumber>"""
                message_information += search_term
                message_information += platinum_keywords


                if not each_product.product_id.amazon_manufacturer:
                    raise osv.except_osv(_('Error'), _('Plz Enter manufacturer!!'))

                xml_product_type =''
                c = ''
                val = ''
                if product.amazon_category.name:
                  if product.amazon_attribute_ids1:
                    c_len = len(product.amazon_attribute_ids1)
                    for rec in product.amazon_attribute_ids1:
                        cnt = 0
                        attrs = rec.name
                        val += c
                        print "-----------------val-->",val
                        c = ''
                        while attrs:
                            cnt = cnt + 1
                            if cnt == 1:
                                if attrs.parent_id.attribute_code is None:
                                    if rec.name.complete_name=='ProductType' or rec.name.complete_name=='ClothingType':
                                        print'hhhhhhhhhhhhhhhhhhhh',rec.value.name
                                        c=self.getmycategory(cr,uid,ids,rec.name.pattern,rec.value.name,context)
                                        print'c' ,c
                                        val += c
                                else:
                                    p = val.find(attrs.parent_id.attribute_code)
                                    l_tag = p + len(attrs.parent_id.attribute_code) + 1
                                    if p > 0:                                     
                                        val = val[:l_tag] +'''<%s>%s</%s>'''%(attrs.attribute_code,rec.value and rec.value.value or rec.value_text,attrs.attribute_code)+ val[l_tag:]
                                        attrs = False 
                                    else:
                                        print "=in else-----------vals-------------",val
                                        c = '''<%s>%s</%s>'''%(attrs.attribute_code,rec.value and rec.value.value or rec.value_text,attrs.attribute_code)
                            else:
                                c = '''<%s>%s</%s>'''%(attrs.attribute_code,c,attrs.attribute_code)
                            if not attrs:
                                continue
                            if attrs.parent_id:
                                attrs = attrs.parent_id
                            else:
                                attrs = False
#                                if c_len == 1:
#                                    val += c
                xml_product_type = val
                print 'style_keywords',style_keywords

                if product.amazon_category.name=='Clothing':
                    message_information +=""" <ItemType><![CDATA[%s]]></ItemType>
                                                <RecommendedBrowseNode>%s</RecommendedBrowseNode>
                                                </DescriptionData>
                                                <ProductData>
                                                <%s>
                                               <ClassificationData><ClothingType>%s</ClothingType></ClassificationData>
                                              </%s></ProductData>"""%(product.item_type.code_type,product.item_type.node,product.amazon_category.name,xml_product_type,product.amazon_category.name)
                else:
                    message_information +=""" <ItemType><![CDATA[%s]]></ItemType>
                                                <RecommendedBrowseNode>%s</RecommendedBrowseNode>
                                                </DescriptionData>
                                                <ProductData>
                                                <%s>
                                               <ProductType>%s</ProductType>
                                              </%s></ProductData>"""%(product.item_type.code_type,product.item_type.node,product.amazon_category.name,xml_product_type,product.amazon_category.name)                    
                message_information += """</Product>
                                            </Message>"""
                print product_sku
                print title
                print message_id
                message_id = message_id + 1
                print"___________",message_information
                product_str = """<MessageType>Product</MessageType>
                                <PurgeAndReplace>false</PurgeAndReplace>"""
                product_data = sale_shop_obj.xml_format(product_str,merchant_string,message_information)
                logger.error('product_data ---------%s', product_data)

            product_data = sale_shop_obj.xml_format(product_str,merchant_string,message_information)
            if product_data:
                product_submission_id = amazon_api_obj.call(instance_obj, 'POST_PRODUCT_DATA',product_data)
                logger.error('product_submission_id---------%s', product_submission_id)
                if product_submission_id.get('FeedSubmissionId',False):
                    time.sleep(100)
                    submission_results = amazon_api_obj.call(instance_obj, 'GetFeedSubmissionResult',product_submission_id.get('FeedSubmissionId',False))
                    print"+++++++++++++=", submission_results.get('getsubmitfeedresult')
                    print product.id,use_id
                    logger.error('submission_results---------%s', submission_results)
                    update=self.write(cr,uid,product.id,{'feed_result':product_submission_id.get('FeedSubmissionId'),'feed_data': submission_results})
                    if submission_results.get('MessagesWithError',False) == '0':
                            product_long_message = ('%s: Updated Successfully on Amazon') % (product_nm)
                            sale_shop_obj.log(cr, uid,log_id, product_long_message)
                            log_id += 1
        return True

    def upload_pricing(self,cr,uid,ids,context):
        amazon_api_obj = self.pool.get('amazonerp.osv')
       
        for product in self.browse(cr,uid,ids):
            price_upload_str=''
            sub_id=''
            parent_xml_data = ''
            amazon_inst_data = product.shop_id.instance_id
            message_count = 1
            merchant_string ="<MerchantIdentifier>%s</MerchantIdentifier>"%(amazon_inst_data.aws_merchant_id)
            message_type = '<MessageType>Price</MessageType>'
            
            for each_product in product.prod_listing_ids:
                print each_product.product_id.id
                product_data = self.pool.get('product.product').browse(cr,uid,each_product.product_id.id)
                if not each_product.product_id.name:
                     raise osv.except_osv(_('Error'), _('Please enter Product SKU for Image Feed "%s"'% (product_data.name)))
                parent_sku = each_product.product_asin.name.strip(" ")
                cost_final=each_product.product_asin.last_sync_price
                print 'cost_final',cost_final
                parent_xml_data += '''<Message><MessageID>%s</MessageID>
                                    <Price>
                                    <SKU>%s</SKU>
                                    <StandardPrice currency="GBP">%s</StandardPrice>
                                    </Price></Message>
                                '''% (message_count,parent_sku,cost_final)


                message_count = message_count + 1

            price_upload_str += """
                    <?xml version="1.0" encoding="utf-8"?>
                    <AmazonEnvelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="amzn-envelope.xsd">
                    <Header>
                        <DocumentVersion>1.01</DocumentVersion>
                        """+merchant_string+"""
                    </Header>
                    """+message_type+parent_xml_data+"""
                    """
            price_upload_str +="""</AmazonEnvelope>"""
            print str
            logger.error('str+++++++=%s',price_upload_str)
            product_submission_id = amazon_api_obj.call(amazon_inst_data, 'POST_PRODUCT_PRICING_DATA',price_upload_str)
            if product_submission_id.get('FeedSubmissionId',False):
#                time.sleep(80)
                submission_results = amazon_api_obj.call(amazon_inst_data, 'GetFeedSubmissionResult',product_submission_id.get('FeedSubmissionId',False))
                sub_id+=product_submission_id.get('FeedSubmissionId')
                print self.write(cr,uid,self.browse(cr,uid,ids)[0].id,{'feed_result':sub_id,'feed_data': submission_results})
        return True


    def getmycategory(self,cr,uid,ids,pattern,value,context):
        mycategory_val=''
        if pattern=='restricted':
            mycategory_val=value
        elif pattern=='choice':
            mycategory_val="""<%s></%s>"""%(value,value)
        else:
            mycategory_val=value

            print 'oye its other'
         
        
        return mycategory_val
    
    def upload_inventory(self,cr,uid,ids,context):
        amazon_api_obj = self.pool.get('amazonerp.osv')
        for product in self.browse(cr,uid,ids):
            sub_id=''
            str=""
            body=""
            xml_data=""
            message_count = 1
            amazon_inst_data = product.shop_id.instance_id
            merchant_string ="<MerchantIdentifier>%s</MerchantIdentifier>"%(amazon_inst_data.aws_merchant_id)
            message_type = '<MessageType>Inventory</MessageType>'
            print"++++++++++++",product.prod_listing_ids
            for each_product in product.prod_listing_ids:
                print each_product.product_id.id
                product_data = self.pool.get('product.product').browse(cr,uid,each_product.product_id.id)
                if not each_product.product_id.name:
                     raise osv.except_osv(_('Error'), _('Please enter Product SKU for Image Feed "%s"'% (product_data.name)))

                parent_sku = each_product.product_asin.name.strip(" ")
                inventory = each_product.product_id.qty_available
                update_xml_data = '''<SKU>%s</SKU>
                                     <Quantity>%s</Quantity>
                                     <FulfillmentLatency>1</FulfillmentLatency>
                                  '''%(parent_sku,int(inventory))
                xml_data += '''<Message>
                            <MessageID>%s</MessageID><OperationType>Update</OperationType>
                            <Inventory>%s</Inventory></Message>
                        '''% (message_count,update_xml_data)

                message_count+=1


            str = """
                    <?xml version="1.0" encoding="utf-8"?>
                    <AmazonEnvelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="amzn-envelope.xsd">
                    <Header>
                    <DocumentVersion>1.01</DocumentVersion>
                    """+merchant_string+"""
                    </Header>
                    """+message_type+xml_data+"""
                    """
            str +="""</AmazonEnvelope>"""
            print"__", str
            logger.error('str+++++++=%s',str)
            product_submission_id = amazon_api_obj.call(amazon_inst_data, 'POST_INVENTORY_AVAILABILITY_DATA',str)
            if product_submission_id.get('FeedSubmissionId',False):
                print"Iddddddddddddd",product_submission_id.get('FeedSubmissionId')
#                time.sleep(80)
                submission_results = amazon_api_obj.call(amazon_inst_data, 'GetFeedSubmissionResult',product_submission_id.get('FeedSubmissionId',False))
                sub_id+=product_submission_id.get('FeedSubmissionId')
                update=self.write(cr,uid,self.browse(cr,uid,ids)[0].id,{'feed_result':sub_id, 'feed_data': submission_results})

        return True

    def import_image(self, cr, uid, ids, context=None):
        amazon_api_obj = self.pool.get('amazonerp.osv')

        for product in self.browse(cr,uid,ids):
            sub_id=''
            xml_information = ''
            message_count=1
            instance_obj = product.shop_id.instance_id
            xml_information +="""<?xml version="1.0" encoding="utf-8"?>
                                <AmazonEnvelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="amzn-envelope.xsd">
                                <Header>
                                    <DocumentVersion>1.01</DocumentVersion>
                                    <MerchantIdentifier>%s</MerchantIdentifier>
                                </Header>
                                <MessageType>ProductImage</MessageType>
                            """%(instance_obj.aws_merchant_id)
            
            print"++++++++++++",product.prod_listing_ids
            for each_product in product.prod_listing_ids:
                product_data = self.pool.get('product.product').browse(cr,uid,each_product.product_id.id)
                if not each_product.product_id.name:
                    raise osv.except_osv(_('Error'), _('Please enter Product SKU for Image Feed "%s"'% (product_data.name)))
                cnt=0
                pref='PT'
                prefrence=''
                for imagedata in product_data.image_ids:
                    print 'imagedata--------------------------------------------------------------------',imagedata.name
                    image_data = self.pool.get('product.images').browse(cr,uid,imagedata.id)
#                    if image_data.is_amazon!=True:
#                        continue
                    if imagedata.url:
                       loc = imagedata.url
                    else:
                
                        img_nm=imagedata.name.replace(' ','_')
                        file = img_nm + imagedata.extention
                        local_media_repository = self.pool.get('res.company').get_local_media_repository(cr, uid, context=context)
                        f = open(local_media_repository + file, 'w')
                        f.write(base64.b64decode(imagedata.file_db_store))
                        f.close()
                        para = self.pool.get("ir.config_parameter")
                        url = para.get_param(cr, uid, "web.base.url", context=context)[:-5]
                        loc = url + '/'+ file #"http://77.68.41.12/index1.jpeg"
#                            url + '/'+ file
                    if cnt==0:
                            prefrence='Main'
                    else:
                            prefrence=pref+str(cnt)
                    xml_information += """<Message>
                                            <MessageID>%s</MessageID>
                                            <OperationType>Update</OperationType>
                                            <ProductImage>
                                                <SKU>%s</SKU>
                                                <ImageType>%s</ImageType>
                                                <ImageLocation>%s</ImageLocation>
                                            </ProductImage>
                                         </Message>""" % (message_count,each_product.product_asin.name,prefrence,loc)
                    message_count+=1
                    cnt=cnt+1
            xml_information +="""</AmazonEnvelope>"""
            print xml_information
            logger.error('xml_information++++++++=%s',xml_information)
            product_submission_id = amazon_api_obj.call(instance_obj, 'POST_PRODUCT_IMAGE_DATA',xml_information)
            if product_submission_id.get('FeedSubmissionId',False):
#                time.sleep(80)
                submission_results = amazon_api_obj.call(instance_obj, 'GetFeedSubmissionResult',product_submission_id.get('FeedSubmissionId',False))
                sub_id+=product_submission_id.get('FeedSubmissionId')
                print self.write(cr,uid,self.browse(cr,uid,ids)[0].id,{'feed_result':sub_id,'feed_data': submission_results})
        return True

    def upload_price_inventory_image(self, cr, uid, ids, context={}):
        self.upload_pricing(cr,uid,ids,context)
        self.upload_inventory(cr,uid,ids,context)
        self.import_image(cr, uid, ids, context=None)
        return True
    
    def get_feed_result(self,cr,uid,ids,context):
        amazon_api_obj = self.pool.get('amazonerp.osv')
        obj = self.browse(cr, uid, ids[0])
        amazon_inst_data = obj.shop_id.instance_id
        if obj.feed_result != False:
            submission_results = amazon_api_obj.call(amazon_inst_data, 'GetFeedSubmissionResultall',obj.feed_result.strip())
            print'submission_results',submission_results
            self.write(cr,uid,ids[0],{'feed_data':submission_results})
        return True

    def import_asin(self,cr,uid,ids,context):
        sku_list=[]
        self_data=self.browse(cr,uid,ids[0])
        amazon_api_obj = self.pool.get('amazonerp.osv')
        amazon_list_obj=self.pool.get('amazon.product.listing')
        instance_obj = self_data.shop_id.instance_id
        all_listings=self_data.prod_listing_ids
        for amazon_list in all_listings:
            logger.error('asin++++++++=%s',amazon_list.product_asin.name)
            if amazon_list.product_asin.name != False:
                sku_list.append(amazon_list.product_asin.name.strip())
            if len(sku_list)>19:
                 raise osv.except_osv(_('Error'), _('Amazon Products Listing must be contain only 19 records!!'))

        if len(sku_list):
                logger.error('sku++++++++=%s',sku_list)       
                node_list = amazon_api_obj.call(instance_obj, 'GetCompetitivePricingForSKU',sku_list)
                logger.error('node_list++++++++=%s',node_list)
                if not len(node_list):
                    time.sleep(15)
                    node_list = amazon_api_obj.call(instance_obj, 'GetCompetitivePricingForSKU',sku_list)
                if len(node_list):
                    for dic in node_list:
                        if dic.has_key('SellerSKU'):
                            find_sku=amazon_list_obj.search(cr,uid,[('name','=', dic['SellerSKU'])])
                            print 'find_sku===',find_sku
                        if len(find_sku):
                            if dic.has_key('ASIN'):
                                amazon_list_obj.write(cr,uid,find_sku[0],{'asin':dic['ASIN']}) 
                                logger.error('I found ASIN with help of sku') 
        return True
    
    _columns = {
        'name':fields.char('Name',size=64,required=True),
        'product_data': fields.selection([('ClothingAccessories', 'ClothingAccessories'),
        ('ProductClothing', 'ProductClothing'),('Miscellaneous', 'Miscellaneous'),('CameraPhoto', 'CameraPhoto'),('Home', 'Home'),
        ('Sports', 'Sports'),('SportsMemorabilia', 'SportsMemorabilia'),('EntertainmentCollectibles', 'EntertainmentCollectibles'),
        ('HomeImprovement', 'HomeImprovement'),('Tools', 'Tools'),('FoodAndBeverages', 'FoodAndBeverages'),('Gourmet', 'Gourmet'),
        ('Jewelry', 'Jewelry'),('Health', 'Health'),('CE','CE'),('Computers', 'Computers'),('SWVG', 'SWVG'),('Wireless', 'Wireless'),
        ('Beauty', 'Beauty'),('Office', 'Office'),('MusicalInstruments', 'MusicalInstruments'),('AutoAccessory', 'AutoAccessory'),
        ('PetSupplies', 'PetSupplies'),('ToysBaby', 'ToysBaby'),('TiresAndWheels', 'TiresAndWheels'),
        ('Music', 'Music'),('Video', 'Video'),('Lighting', 'Lighting'),('LargeAppliances', 'LargeAppliances'),('FBA', 'FBA'),
        ('Toys', 'Toys'),('GiftCards', 'GiftCards'),('LabSupplies', 'LabSupplies'),('RawMaterials', 'RawMaterials'),('PowerTransmission', 'PowerTransmission'),
        ('Industrial', 'Industrial'),('Shoes', 'Shoes'),('Motorcycles', 'Motorcycles'),('MaterialHandling', 'MaterialHandling'),('MechanicalFasteners', 'MechanicalFasteners'),
        ('FoodServiceAndJanSan', 'FoodServiceAndJanSan'),('WineAndAlcohol', 'WineAndAlcohol'),('EUCompliance', 'EUCompliance'),('Books', 'Books')],
        'Product Type',Required=True),
        'product_type_clothingaccessories': fields.selection([('ClothingAccessories', 'ClothingAccessories')],'ClothingAccessories'),
        'product_type_ce': fields.selection([('Antenna', 'Antenna'),('AudioVideoAccessory', 'AudioVideoAccessory'),('AVFurniture', 'AVFurniture'),
        ('BarCodeReader', 'BarCodeReader'),('CEBinocular', 'CEBinocular'),('CECamcorder', 'CECamcorder'),('CameraBagsAndCases', 'CameraBagsAndCases'),
        ('CEBattery','CEBattery'),('CEBlankMedia','CEBlankMedia'),('CableOrAdapter','CableOrAdapter'),('CECameraFlash', 'CECameraFlash'),
        ('CameraLenses', 'CameraLenses'),('CameraOtherAccessories', 'CameraOtherAccessories'),('CameraPowerSupply', 'CameraPowerSupply'),('CarAlarm', 'CarAlarm'),
        ('CarAudioOrTheater', 'CarAudioOrTheater'),('CarElectronics', 'CarElectronics'),('ConsumerElectronics', 'ConsumerElectronics'),('CEDigitalCamera', 'CEDigitalCamera'),
        ('DigitalPictureFrame', 'DigitalPictureFrame'),('DigitalVideoRecorder', 'DigitalVideoRecorder'),('DVDPlayerOrRecorder', 'DVDPlayerOrRecorder'),('CEFilmCamera', 'CEFilmCamera'),
        ('GPSOrNavigationAccessory', 'GPSOrNavigationAccessory'),('GPSOrNavigationSystem', 'GPSOrNavigationSystem'),('HandheldOrPDA', 'HandheldOrPDA'),('Headphones', 'Headphones'),
        ('HomeTheaterSystemOrHTIB', 'HomeTheaterSystemOrHTIB'),('KindleAccessories', 'KindleAccessories'),('KindleEReaderAccessories', 'KindleEReaderAccessories'),('KindleFireAccessories', 'KindleFireAccessories'),
        ('MediaPlayer', 'MediaPlayer'),('MediaPlayerOrEReaderAccessory', 'MediaPlayerOrEReaderAccessory'),('MediaStorage', 'MediaStorage'),('MiscAudioComponents', 'MiscAudioComponents'),('PC', 'PC'),('PDA', 'PDA'),
        ('Phone', 'Phone'),('PhoneAccessory', 'PhoneAccessory'),('PhotographicStudioItems', 'PhotographicStudioItems'),('PortableAudio', 'PortableAudio'),('PortableAvDevice', 'PortableAvDevice'),('PowerSuppliesOrProtection', 'PowerSuppliesOrProtection'),
        ('RadarDetector', 'RadarDetector'),('RadioOrClockRadio', 'RadioOrClockRadio'),('ReceiverOrAmplifier', 'ReceiverOrAmplifier'),('RemoteControl', 'RemoteControl'),('Speakers', 'Speakers'),('StereoShelfSystem', 'StereoShelfSystem'),
        ('CETelescope', 'CETelescope'),('Television', 'Television'),('Tuner', 'Tuner'),('TVCombos', 'TVCombos'),('TwoWayRadio', 'TwoWayRadio'),('VCR', 'VCR'),('CEVideoProjector', 'CEVideoProjector'),('VideoProjectorsAndAccessories', 'VideoProjectorsAndAccessories'),
        ], 'CE Types'),
        'feed_result':fields.text('Feed ID',readonly=True),
        'product_type_com': fields.selection([('CarryingCaseOrBag', 'CarryingCaseOrBag'),('ComputerAddOn', 'ComputerAddOn'),('ComputerComponent', 'ComputerComponent'),
        ('ComputerCoolingDevice', 'ComputerCoolingDevice'),('ComputerDriveOrStorage', 'ComputerDriveOrStorage'),('ComputerInputDevice', 'ComputerInputDevice'),('ComputerProcessor', 'ComputerProcessor'),
        ('ComputerSpeaker', 'ComputerSpeaker'),('Computer', 'Computer'),('FlashMemory', 'FlashMemory'),('InkOrToner', 'InkOrToner'),
        ('Keyboards', 'Keyboards'),('MemoryReader', 'MemoryReader'),('Monitor', 'Monitor'),('Motherboard', 'Motherboard'),
        ('NetworkingDevice', 'NetworkingDevice'),('NotebookComputer', 'NotebookComputer'),('PersonalComputer', 'PersonalComputer'),('Printer', 'Printer'),
        ('RamMemory', 'RamMemory'),('Scanner', 'Scanner'),('SoundCard', 'SoundCard'),('SystemCabinet', 'SystemCabinet'),
        ('SystemPowerDevice', 'SystemPowerDevice'),('TabletComputer', 'TabletComputer'),('VideoCard', 'VideoCard'),('VideoProjector', 'VideoProjector'),
        ('Webcam', 'Webcam')], 'Computer Types'),

        'product_type_auto_accessory': fields.selection([('AutoAccessoryMisc', 'AutoAccessoryMisc'),('AutoPart', 'AutoPart'),('PowersportsPart', 'PowersportsPart'),
        ('PowersportsVehicle', 'PowersportsVehicle'),('ProtectiveGear', 'ProtectiveGear'),('Helmet', 'Helmet'),('RidingApparel', 'RidingApparel'),
        ], 'Auto Accessory Types'),

        'product_type_sports': fields.selection([('SportingGoods', 'SportingGoods'),('GolfClubHybrid', 'GolfClubHybrid'),('GolfClubIron', 'GolfClubIron'),
        ('GolfClubPutter', 'GolfClubPutter'),('GolfClubWedge', 'GolfClubWedge'),('GolfClubWood', 'GolfClubWood'),('GolfClubs', 'GolfClubs'),
        ], 'sports Types'),

        'product_type_foodandbeverages': fields.selection([('Food', 'Food'),('HouseholdSupplies', 'HouseholdSupplies'),('Beverages', 'Beverages'),
        ('HardLiquor', 'HardLiquor'),('AlcoholicBeverages', 'AlcoholicBeverages'),('Wine', 'Wine')], 'Food And Beverages Types'),

        'product_type_softwarevideoGames': fields.selection([('Software', 'Software'),('HandheldSoftwareDownloads', 'HandheldSoftwareDownloads'),('SoftwareGames', 'SoftwareGames'),
        ('VideoGames', 'VideoGames'),('VideoGamesAccessories', 'VideoGamesAccessories'),('VideoGamesHardware', 'VideoGamesHardware')], 'Software Video Games Types'),

        'product_type_tools': fields.selection([('GritRating', 'GritRating'),('Horsepower', 'Horsepower'),('Diameter', 'Diameter'),
        ('Length', 'Length'),('Width', 'Width'),('Height', 'Height'),('Weight','Weight')], 'Tools Types'),

        'product_type_toys': fields.selection([('ToysAndGames', 'ToysAndGames'),('Hobbies', 'Hobbies'),('CollectibleCard', 'CollectibleCard'),
        ('Costume', 'Costume')], 'Toys Types'),

        'product_type_jewelry': fields.selection([('Watch', 'Watch'),('FashionNecklaceBraceletAnklet', 'FashionNecklaceBraceletAnklet'),('FashionRing', 'FashionRing'),
        ('FashionEarring', 'FashionEarring'),('FashionOther', 'FashionOther'),('FineNecklaceBraceletAnklet', 'FineNecklaceBraceletAnklet'),('FineRing', 'FineRing'),('FineEarring', 'FineEarring'),('FineOther', 'FineOther')], 'Food And Beverages Types'),

        'product_type_home': fields.selection([('BedAndBath', 'BedAndBath'),('FurnitureAndDecor', 'FurnitureAndDecor'),('Kitchen', 'Kitchen'),
        ('OutdoorLiving', 'OutdoorLiving'),('SeedsAndPlants', 'SeedsAndPlants'),('Art', 'Art'),('Home', 'Home')], 'Home Types'),

        'product_type_miscellaneous': fields.selection([('MiscType', 'MiscType')], 'Misc Types'),

        'product_type_Video': fields.selection([('VideoDVD', 'VideoDVD'),('VideoVHS','VideoVHS')], 'Video Types'),
        'product_type_petsupplies': fields.selection([('PetSuppliesMisc', 'PetSuppliesMisc')], 'Petsupplies Types'),
        'product_type_toys_baby': fields.selection([('ToysAndGames', 'ToysAndGames'),('BabyProducts', 'BabyProducts')], 'Toys n Baby Types'),
        'product_type_beauty': fields.selection([('BeautyMisc', 'BeautyMisc')], 'Beauty Types'),
        'product_type_shoes': fields.selection([('ClothingType', 'ClothingType')], 'Shoes Types'),

        'product_type_wirelessaccessories': fields.selection([('WirelessAccessories', 'WirelessAccessories'),('WirelessDownloads', 'WirelessDownloads'),
        ], 'Wireless Types'),

        'product_type_cameraphoto': fields.selection([('FilmCamera', 'FilmCamera'),('Camcorder', 'Camcorder'),('DigitalCamera', 'DigitalCamera'),
        ('DigitalFrame', 'DigitalFrame'),('Binocular', 'Binocular'),('SurveillanceSystem', 'SurveillanceSystem'),('Telescope', 'Telescope'),
        ('Microscope', 'Microscope'),('Darkroom', 'Darkroom'),('Lens', 'Lens'),('LensAccessory', 'LensAccessory'),
        ('Filter', 'Filter'),('Film', 'Film'),('BagCase', 'BagCase'),('BlankMedia', 'BlankMedia'),('PhotoPaper', 'PhotoPaper'),('Cleaner', 'Cleaner'),('Flash', 'Flash'),
        ('TripodStand', 'TripodStand'),('Lighting', 'Lighting'),('Projection', 'Projection'),('PhotoStudio', 'PhotoStudio'),
        ('LightMeter', 'LightMeter'),('PowerSupply', 'PowerSupply'),('OtherAccessory', 'OtherAccessory'),
        ], 'Camera n Photo'),

        'product_sub_type_ce': fields.selection([('Antenna', 'Antenna'),('AVFurniture', 'AVFurniture'),('BarCodeReader', 'BarCodeReader'),
        ('CEBinocular', 'CEBinocular'),('CECamcorder', 'CECamcorder'),('CameraBagsAndCases', 'CameraBagsAndCases'),('Battery', 'Battery'),
        ('BlankMedia', 'BlankMedia'),('CableOrAdapter', 'CableOrAdapter'),('CECameraFlash', 'CECameraFlash'),('CameraLenses', 'CameraLenses'),
        ('CameraOtherAccessories', 'CameraOtherAccessories'),('CameraPowerSupply', 'CameraPowerSupply'),('CarAudioOrTheater', 'CarAudioOrTheater'),('CarElectronics', 'CarElectronics'),
        ('CEDigitalCamera', 'CEDigitalCamera'),('DigitalPictureFrame', 'DigitalPictureFrame'),('CECarryingCaseOrBag', 'CECarryingCaseOrBag'),('CombinedAvDevice', 'CombinedAvDevice'),
        ('Computer', 'Computer'),('ComputerDriveOrStorage', 'ComputerDriveOrStorage'),('ComputerProcessor', 'ComputerProcessor'),('ComputerVideoGameController', 'ComputerVideoGameController'),
        ('DigitalVideoRecorder', 'DigitalVideoRecorder'),('DVDPlayerOrRecorder', 'DVDPlayerOrRecorder'),('CEFilmCamera', 'CEFilmCamera'),('FlashMemory', 'FlashMemory'),
        ('GPSOrNavigationAccessory', 'GPSOrNavigationAccessory'),('GPSOrNavigationSystem', 'GPSOrNavigationSystem'),('HandheldOrPDA', 'HandheldOrPDA'),('HomeTheaterSystemOrHTIB', 'HomeTheaterSystemOrHTIB'),('Keyboards', 'Keyboards'),
        ('MemoryReader', 'MemoryReader'),('Microphone', 'Microphone'),('Monitor', 'Monitor'),('MP3Player', 'MP3Player'),
        ('MultifunctionOfficeMachine', 'MultifunctionOfficeMachine'),('NetworkAdapter', 'NetworkAdapter'),('NetworkMediaPlayer', 'NetworkMediaPlayer'),('NetworkStorage', 'NetworkStorage'),
        ('NetworkTransceiver', 'NetworkTransceiver'),('NetworkingDevice', 'NetworkingDevice'),('NetworkingHub', 'NetworkingHub'),('Phone', 'Phone'),
        ('PhoneAccessory', 'PhoneAccessory'),('PhotographicStudioItems', 'PhotographicStudioItems'),('PointingDevice', 'PointingDevice'),('PortableAudio', 'PortableAudio'),
        ('PortableAvDevice', 'PortableAvDevice'),('PortableElectronics', 'PortableElectronics'),('Printer', 'Printer'),('PrinterConsumable', 'PrinterConsumable'),
        ('ReceiverOrAmplifier', 'ReceiverOrAmplifier'),('RemoteControl', 'RemoteControl'),('SatelliteOrDSS', 'SatelliteOrDSS'),('Scanner', 'Scanner'),
        ('SoundCard', 'SoundCard'),('Speakers', 'Speakers'),('CETelescope', 'CETelescope'),('SystemCabinet', 'SystemCabinet'),
        ('SystemPowerDevice', 'SystemPowerDevice'),('Television', 'Television'),('TwoWayRadio', 'TwoWayRadio'),('VCR', 'VCR'),
        ('VideoCard', 'VideoCard'),('VideoProjector', 'VideoProjector'),('VideoProjectorsAndAccessories', 'VideoProjectorsAndAccessories'),('Webcam', 'Webcam')], 'Product Sub Type'),
        'product_type_sportsmemorabilia':fields.selection([('SportsMemorabilia','SportsMemorabilia')],'Sports Memorabilia'),
        'product_type_health':fields.selection([('HealthMisc','HealthMisc'),('PersonalCareAppliances','PersonalCareAppliances')],'Health'),
        'battery_chargecycles':fields.integer('Battery Charge Cycles'),
        'battery_celltype':fields.selection([('NiCAD','NiCAD'),('NiMh','NiMh'),('alkaline','alkaline'),('aluminum_oxygen','aluminum_oxygen'),('lead_acid','lead_acid'),('lead_calcium','lead_calcium'),('lithium','lithium'),('lithium_ion','lithium_ion'),('lithium_manganese_dioxide','lithium_manganese_dioxide'),('lithium_metal','lithium_metal'),('lithium_polymer','lithium_polymer'),('manganese','manganese'),('polymer','polymer'),
        ('silver_oxide','silver_oxide'),('zinc','zinc')],'Battery Cell Type'),
        'power_plugtype':fields.selection([('type_a_2pin_jp','type_a_2pin_jp'),('type_e_2pin_fr','type_e_2pin_fr'),('type_j_3pin_ch','type_j_3pin_ch'),('type_a_2pin_na','type_a_2pin_na'),('type_ef_2pin_eu','type_ef_2pin_eu'),('type_k_3pin_dk','type_k_3pin_dk'),('type_b_3pin_jp','type_b_3pin_jp'),('type_f_2pin_de','type_f_2pin_de'),('type_l_3pin_it','type_l_3pin_it'),('type_b_3pin_na','type_b_3pin_na'),('type_g_3pin_uk','type_g_3pin_uk'),('type_m_3pin_za','type_m_3pin_za'),('type_c_2pin_eu','type_c_2pin_eu'),
        ('type_h_3pin_il','type_h_3pin_il'),('type_n_3pin_br','type_n_3pin_br'),('type_d_3pin_in','type_d_3pin_in'),('type_i_3pin_au','type_i_3pin_au')],'Power Plug Type'),
        'power_source':fields.selection([('AC','AC'),('DC','DC'),('Battery','Battery'),
        ('AC & Battery','AC & Battery'),('Solar','Solar'),('fuel_cell','Fuel Cell'),('Kinetic','Kinetic')],'Power Source'),
        'wattage':fields.integer('Wattage'),

        'product_type_music':fields.selection([('MusicPopular','MusicPopular'),('MusicClassical','MusicClassical')],'Music'),
        'product_type_office':fields.selection([('ArtSupplies','ArtSupplies'),('EducationalSupplies','EducationalSupplies'),('OfficeProducts','OfficeProducts'),('PaperProducts','PaperProducts'),('WritingInstruments','WritingInstruments')],'Office'),
        'variation_data':fields.selection([('Solar','Solar'),('Solar','Solar')],'VariationData'),
        'hand_orientation':fields.selection([('Solar','Solar'),('Solar','Solar')],'HandOrientation'),
        'input_device_design_style':fields.selection([('Solar','Solar'),('Solar','Solar')],'InputDeviceDesignStyle'),
        'keyboard_description':fields.char('Keyboard Description',size=64),
        'product_type_tiresandwheels':fields.selection([('Tires','Tires'),('Wheels','Wheels')],'Tires And Wheels'),
        'product_type_giftcard':fields.selection([('ItemDisplayHeight','ItemDisplayHeight'),('ItemDisplayLength','ItemDisplayLength'),
        ('ItemDisplayWidth','ItemDisplayWidth'),('ItemDisplayWeight','ItemDisplayWeight')],'Gift Card'),

        'product_type_musicalinstruments':fields.selection([('BrassAndWoodwindInstruments','BrassAndWoodwindInstruments'),('Guitars','Guitars'),
        ('InstrumentPartsAndAccessories','InstrumentPartsAndAccessories'),('KeyboardInstruments','KeyboardInstruments'),('MiscWorldInstruments','MiscWorldInstruments'),('PercussionInstruments','PercussionInstruments'),
        ('SoundAndRecordingEquipment','SoundAndRecordingEquipment'),('StringedInstruments','StringedInstruments')],'MusicalInstruments Type'),

        'model_number':fields.integer('Model Number'),
        'voltage':fields.integer('Voltage'),
        'wattage_com':fields.integer('Wattage'),
        'wireless_input_device_protocol':fields.selection([('Solar','Solar'),('Solar','Solar')],'Wireless InputDevice Protocol'),
        'wireless_input_device_technology':fields.selection([('Solar','Solar'),('Solar','Solar')],'Wireless InputDevice Technology'),
        'prod_listing_ids': fields.one2many('products.amazon.listing.upload', 'listing_id','Product Listing'),

        'cablelength':fields.char('Cabel Length',size=64),
        'operating_system':fields.char('Operating System',size=64),
        'power_source_gp':fields.char('Power Source',size=64),
        'screen_size':fields.char('Screen Size',size=64),
        'total_ethernet_ports':fields.char('Total Ethernet Ports',size=64),
        'wireless_type':fields.char('Wireless Type',size=64),

        'battery_cell_type_gp':fields.char('Battery Cell Type',size=64),
        'battery_charge_cycles_gp':fields.integer('Battery Charge Cycles'),
        'battery_power_gpnav':fields.char('Battery Power',size=64),
        'box_contents_gp':fields.char('Box Contents',size=64),
        'cable_length_gp':fields.char('Cable Length',size=64),
        'color_screen_gp':fields.boolean('Wireless Type'),
        'duration_ofmap_service_gp':fields.char('Duration Of Map Service',size=64),
        'operatingsystem_gp':fields.char('Operating System',size=64),
        'video_processor_gp':fields.char('Video Processor',size=64),
        'efficiencys_gp':fields.char('Efficiency',size=64),
        'finish_typeh_gp':fields.char('Finish Type',size=64),
        'internet_applications_gp':fields.char('Internet Applications',size=64),
        'memory_slots_available_gp':fields.char('Memory Slots Available',size=64),
        'power_plug_type_gp':fields.char('Battery Charge Cycles',size=64),
        'powersource_gpnav':fields.char('Power Source',size=64),
        'processorbrand_gp':fields.char('Processor Brand',size=64),
        'screensize_gp':fields.char('Screen_Size',size=64),
        'remotecontroldescription_gp':fields.char('Remote Control Descriptionpe',size=64),
        'removablememory_gp':fields.char('Removable Memory',size=64),
        'screenresolution_gp':fields.char('Screen Resolution',size=64),
        'subscriptiontermnamer_gp':fields.char('Subscription TermName',size=64),
        'trafficfeatures_gp':fields.char('Traffic Features',size=64),
        'softwareincluded_gp':fields.char('Software Included',size=64),
        'totalethernetports_gp':fields.char('Total Ethernet Ports',size=64),
        'totalfirewireports_gp':fields.char('Total Fire wire Ports',size=64),
        'totalhdmiports_gp':fields.char('Total Hdmi Ports',size=64),
        'totalsvideooutports_gp':fields.integer('Total SVideo OutPorts'),
        'wirelesstechnology_gp':fields.char('Wireless Technology',size=64),
        'total_usb_ports_gp':fields.char('Total USB Ports',size=64),
        'waypointstype_gp':fields.char('Waypoints Type',size=64),

        'colorscreen_hpda':fields.boolean('ColorScreen'),
        'hardrivesize_hpda':fields.integer('Hard Drive Size'),
        'memory_slots_available_hpda':fields.char('Memory Slots Available',size=64),
        'operating_system_hpda':fields.char('Operating System',size=64),
        'power_source_hpda':fields.char('Power Source',size=64),
        'processor_type_hpda':fields.char('Processor Type',size=64),
        'processor_speed_hpda':fields.char('Processor Speed',size=64),
        'RAMsize_hpda':fields.char('RAMSize',size=64),
        'screen_size_hpda':fields.char('Screen Size',size=64),
        'screen_resolution_hpda':fields.char('Screen Resolution',size=64),
        'softwareincluded_hpda':fields.char('Software Included',size=64),
        'wirelesstechnology_hpda':fields.char('Wireless Technology',size=64),

        'amplifiertype_headphone':fields.char('Amplifiertype',size=64),
        'battery_celltype_headphone':fields.char('Battery Celltype',size=64),
        'batterychargecycles_headphone':fields.char('Battery Chargecycles',size=64),
        'batterypower_headphone':fields.char('Battery Power',size=64),
        'cable_length_headphone':fields.char('Cable Length',size=64),
        'controltype_headphone':fields.char('Control Type',size=64),
        'fittype_headphone':fields.char('Fit Type',size=64),
        'headphoneearcupmotion_headphone':fields.char('Headphone Earcup Motion',size=64),
        'noisereductionlevel_headphone':fields.char('Noise Reduction Level',size=64),
        'power_plug_type_headphone':fields.char('Power Plug Type',size=64),
        'shape_headphone':fields.char('Shape',size=64),
        'powersource_headphone':fields.char('Power Source',size=64),
        'totalcomponentinports_headphone':fields.char('Total Component In Ports',size=64),
        'wirelesstechnology_headphone':fields.char('Wireless Technology',size=64),

        'variationdata_net':fields.char('Variation Data',size=64),
        'additional_features_net':fields.char('Additional Features',size=64),
        'additional_functionality_net':fields.char('Additional Functionality',size=64),
        'ipprotocol_standards_net':fields.char('IP ProtocolStandards',size=64),
        'lanportbandwidth_net':fields.char('LAN Port Bandwidth',size=64),
        'lan_port_number_net':fields.char('LAN Port Number',size=64),
        'maxdownstreamtransmissionrate_net':fields.char('Max Downstream Transmission Rate',size=64),
        'maxupstreamtransmissionRate_net':fields.char('Max Upstream Transmission Rate',size=64),
        'model_number_net':fields.char('Model Number',size=64),
        'modem_type_net':fields.char('Modem Type',size=64),
        'network_adapter_type_type_net':fields.char('Network Adapter Type',size=64),
        'operating_system_compatability_net':fields.char('Operating System Compatability',size=64),
        'securityprotocol_net':fields.char('Security Protocol',size=64),
        'simultaneous_sessions_net':fields.char('Simultaneous Sessions',size=64),
        'voltage_net':fields.char('Voltage',size=64),
        'wattage_net':fields.char('Wattage',size=64),
        'wirelessdatatransferrate_net':fields.char('Wireless Data Transfer Rate',size=64),
        'wirelessroutertransmissionband_net':fields.char('Wireless Router Transmission Band',size=64),
        'wirelesstechnology_net':fields.char('Wireless Technology',size=64),

        'variationdata_scanner':fields.char('Variation Data',size=64),
        'hasgreyscale_scanner':fields.char('Has Grey Scale',size=64),
        'lightsourcetype_scanner':fields.char('Battery Chargecycles',size=64),
        'maxinputsheetcapacity_scanner':fields.integer('Max Input Sheet Capacity'),
        'maxprintresolutionblackwhite_scanner':fields.char('Max Print Resolution BlackWhite',size=64),
        'maxprintresolutioncolor_scanner':fields.char('Max Print Resolution Color',size=64),
        'maxprintspeedblackwhite_scanner':fields.char('Max Print Speed BlackWhite',size=64),
        'maxprintspeedcolor_scanner':fields.char('Max Print Speed Color',size=64),
        'maxscanningsize_scanner':fields.char('Max scanning size',size=64),
        'minscanningsize_scanner':fields.char('Min Scanning Size',size=64),
        'printermediasizemaximum_scanner':fields.char('Printer Media Size Maximum',size=64),
        'printeroutputtype_scanner':fields.char('Printer Output Type',size=64),
        'printerwirelesstype_scanner':fields.char('Printer Wireless Type',size=64),
        'printing_media_type_scanner':fields.char('Printing Media Type',size=64),
        'printingtechnology_scanner':fields.char('Printing Technology',size=64),
        'scanrate_scanner_scanner':fields.char('Scan Rate',size=64),
        'scannerresolution_scanner':fields.char('Scanner Resolution',size=64),

        'variationdata_printer':fields.char('Variation Data',size=64),
        'hasgreyscale_printer':fields.char('Has Grey Scale',size=64),
        'lightsourcetype_printer':fields.char('Battery Chargecycles',size=64),
        'maxinputsheetcapacity_printer':fields.integer('Max Input Sheet Capacity'),
        'maxprintresolutionblackwhite_printer':fields.char('Max Print Resolution BlackWhite',size=64),
        'maxprintresolutioncolor_printer':fields.char('Max Print Resolution Color',size=64),
        'maxprintspeedblackwhite_printer':fields.char('Max Print Speed BlackWhite',size=64),
        'maxprintspeedcolor_printer':fields.char('Max Print Speed Color',size=64),
        'maxscanningsize_printer':fields.char('Max scanning size',size=64),
        'minscanningsize_printer':fields.char('Min Scanning Size',size=64),
        'printermediasizemaximum_printer':fields.char('Printer Media Size Maximum',size=64),
        'printeroutputtype_printer':fields.char('Printer Output Type',size=64),
        'printerwirelesstype_printer':fields.char('Printer Wireless Type',size=64),
        'printing_media_type_printer':fields.char('Printing Media Type',size=64),
        'printingtechnology_printer':fields.char('Printing Technology',size=64),
        'scanrate_scanner_printer':fields.char('Scan Rate',size=64),
        'scannerresolution_printer':fields.char('Scanner Resolution',size=64),

        'amazon_category': fields.many2one('product.attribute.set','Category'),
        'amazon_attribute_ids1': fields.one2many('product.attribute.info', 'manage_amazon_product_id', 'Attributes'),
#        'res_feed_result':fields.char('Feed result',size=64),
        'feed_data':fields.text('Feed Data',readonly=True),
        'shop_id': fields.many2one('sale.shop', 'Shop', domain=[('amazon_shop','=', True)]),
        'item_type': fields.many2one('product.category.type', 'Item Type')
        
    }

    _defaults = {
#        'company_id': lambda s, cr, uid, c: s.pool.get('res.company')._company_default_get(cr, uid, 'sale.shop', context=c),
        }


upload_amazon_products()

class products_amazon_listing_upload(osv.osv):
    _name = "products.amazon.listing.upload"

    _columns = {
        'is_new_listing':fields.boolean('New'),
        'listing_id':fields.many2one('upload.amazon.products', string='Listing Name'),
        'product_id':fields.many2one('product.product', string='Product Name'),
        'product_asin':fields.many2one('amazon.product.listing', string='Listing'),
        'quantity_db': fields.integer('Quantity Available'),
    }
products_amazon_listing_upload()
