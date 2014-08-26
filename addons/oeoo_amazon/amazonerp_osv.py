# -*- coding: utf-8 -*-
import hashlib
import hmac
import urllib
from urllib import urlencode
from osv import osv
import time
import base64
from tools.translate import _
import httplib
from xml.dom.minidom import parseString
import md5
from datetime import timedelta,datetime
import datetime

#from elementtree.ElementTree import XML, fromstring, tostring
from lxml import etree as ET

class Session:
    def Initialize(self, access_key, secret_key, merchant_id, marketplace_id, site):
        self.access_key = access_key
        self.secret_key = secret_key
        self.merchant_id = merchant_id
        self.marketplace_id = marketplace_id
        self.domain = site
        self.version= '2011-01-01'



Session()


class Call:
    RequestData = ""  # just a stub
    command = ''
    url_string = ''
    url_params = []
    post_data = ''

    def getErrors(self, node):
        info = {}
        for node in node:
            for cNode in node.childNodes:
                if cNode.nodeName == 'Message':
                     info['Error'] = cNode.childNodes[0].data
        return info

    def MakeCallRepeat(self,responseDOM,url_params,post_data,command,method):
        getErrordetails = self.getErrors(responseDOM.getElementsByTagName('Error'))
        print 'getErrordetails',getErrordetails
        if getErrordetails.get('Error',False):
            count = 1
            while ( getErrordetails.get('Error').lower().find('request signature we calculated') != -1 or getErrordetails.get('Error').lower().find('throttled') != -1 or getErrordetails.get('Error').lower().find('connection timed') != -1 or getErrordetails.get('Error').lower().find('internal service') != -1):
                count = count + 1
                time.sleep(25)
                del url_params['Signature']
                url_string = self.calc_signature(url_params,post_data)
                self.url_string  = str(command) + url_string
                responseDOM = self.MakeCall(method)
                getErrordetails = self.getErrors(responseDOM.getElementsByTagName('Error'))
                print 'getErrordetails',getErrordetails
                if count >= 5 or len(getErrordetails) == 0:
                    break

        #Raise Error even after calling it five times, because it can be some other issue other than signature mismatch or throttled
#        if getErrordetails.get('Error',False):
#            print 'major Error',getErrordetails
#            raise osv.except_osv(_('Error!'), _((getErrordetails.get('Error',False))))

        return responseDOM

    def calc_signature(self, url_params,post_data):
        """Calculate MWS signature to interface with Amazon
        '/Orders/2011-01-01"""
        '''keys = url_params.keys()
        keys.sort()
        # Get the values in the same order of the sorted keys
        values = map(url_params.get, keys)
        # Reconstruct the URL paramters and encode them
        url_string = urlencode( zip(keys,values) )
        string_to_sign = 'POST\n%s\n%s\n%s' % (self.Session.domain,post_data,url_string)'''

        url_params['Timestamp'] = time.strftime("%Y-%m-%dT%H:%M:%S")+ 'Z'
        keys = url_params.keys()
        keys.sort()
        # Get the values in the same order of the sorted keys
        values = map(url_params.get, keys)
        # Reconstruct the URL paramters and encode them
        url_string = urlencode( zip(keys,values) )
        url_string = url_string.replace('+','%20')
        string_to_sign = 'POST\n%s\n%s\n%s' % (self.Session.domain,post_data,url_string)
        signature = hmac.new(self.Session.secret_key.encode('utf-8'),string_to_sign,hashlib.sha256).digest()
        url_params['Signature'] = base64.b64encode( signature )

        keys = url_params.keys()
        keys.sort()
        values = map(url_params.get, keys)
        
        # Reconstruct the URL paramters and encode them
        url_string = urlencode( zip(keys,values) ).replace('%0A','')
#        print "=======url_string========>",(url_string).encode('utf-8')
        return url_string

    def cal_content_md5(self,request_xml):
        m = md5.new()
        print "_________request_xml_____________>,",request_xml
        m.update(request_xml)
        value = m.digest()
        hash_string = base64.encodestring(value)
        hash_string = hash_string.replace('\n', '')
        return hash_string

    def MakeCall(self,callName):
        '''self.url_param['Timestamp'] = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime())+ 'Z'
        signature_info = self.calc_signature(self.url_param,self.post_data)
        self.url_param['Signature'] = signature_info[0]
        self.url_string  = str(self.command) + signature_info[1].replace('%0A','')+'&Signature='+urllib.quote(str(signature_info[0]))'''
        print"**********************url_string",self.url_string
        self.url_string = (self.url_string).replace('+','%20')
        conn = httplib.HTTPSConnection(self.Session.domain)
        if callName.startswith('POST_'):
            content_md5 = self.cal_content_md5(self.RequestData)
            conn.request("POST", self.url_string, self.RequestData, self.GenerateHeaders(len(self.RequestData),content_md5))
        else:
            conn.request("POST", self.url_string, self.RequestData, self.GenerateHeaders('',''))
            print "------------------------------------------------"
        response = conn.getresponse()
        data = response.read()
        conn.close()
        if callName == 'GetReport':
            return data
        else:
            responseDOM = parseString(data)
            tag = responseDOM.getElementsByTagName('Error')
            if (tag.count!=0):
                for error in tag:
                    print "\n",error.toprettyxml("  ")
            return responseDOM

    def GenerateHeaders(self, length_request, contentmd5):
        headers ={}
        headers = {
                   "Content-type": "text/xml; charset=UTF-8"
                   }
        if length_request and contentmd5:
            headers['Content-Length'] = length_request
            headers['Content-MD5']= contentmd5
        return headers

class ListMatchingProducts:
    Session = Session()
    def __init__(self, access_key, secret_key, merchant_id, marketplace_id, site):
        self.Session.Initialize(access_key, secret_key, merchant_id, marketplace_id, site)

    def Get(self,product_query,prod_query_contextid):
        api = Call()
        api.Session = self.Session
        command = '/Products/2011-10-01?'
        version = '2011-10-01'
        method = 'ListMatchingProducts'
        url_params ={'Action':method,'SellerId':self.Session.merchant_id,'MarketplaceId':self.Session.marketplace_id,'Query':product_query,'AWSAccessKeyId':self.Session.access_key,'SignatureVersion':'2','SignatureMethod':'HmacSHA256','Version':version}
        if prod_query_contextid:
            url_params['QueryContextId'] = prod_query_contextid
        url_params['Timestamp'] = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime())+ '.000Z'
        post_data = '/Products/2011-10-01'
        url_params['Signature'] = api.calc_signature(url_params,post_data)[0]
        url_string = api.calc_signature(url_params,post_data)[1].replace('%0A','')
        api.url_string  = str(command) + url_string
        api.RequestData =''
        responseDOM = api.MakeCall('ListMatchingProducts')
        element = ET.XML(responseDOM.toprettyxml())
        mydict = {}
        product_info = []
        flag = False
        for elt in element.getiterator():
                if (elt.tag[0] == "{") and (elt.text is not None):
                        uri, tag = elt.tag[1:].split("}")
                        if tag == 'Product':
                                flag = True      #set flag to true once we find a product tag
                                product_info.append(mydict)
                                mydict = {}
                        if flag:
                                mydict[tag] = elt.text.strip()

        product_info.append(mydict)
        product_info.pop(0)
        return product_info

class AmazonObjectUtils:
    OrderRoot = ["Orders", "Order"]
    OrderMap = {
                "ShippingCompanyName":["ShippingAddress", "Name"],
                "BillingCompanyName":["ShippingAddress", "Name"],
                "ShippingName":["ShippingAddress", "Name"],
                "BillingName":["ShippingAddress", "Name"],

                "ShippingAddressLine1":["ShippingAddress", "AddressLine1"],
                "BillingAddressLine1":["ShippingAddress", "AddressLine1"],

                "ShippingCity":["ShippingAddress", "City"],
                "BillingCity":["ShippingAddress", "City"],

                "ShippingStateOrRegion":["ShippingAddress", "StateOrRegion"],
                "BillingStateOrRegion":["ShippingAddress", "StateOrRegion"],

                "ShippingPostalCode":["ShippingAddress", "PostalCode"],
                "BillingPostalCode":["ShippingAddress", "PostalCode"],

                "ShippingPhone":["ShippingAddress", "Phone"],
                "BillingPhone":["ShippingAddress", "Phone"],

                "ShippingCountryCode":["ShippingAddress", "CountryCode"],
                "BillingCountryCode":["ShippingAddress", "CountryCode"],
                
                "Carrier":["ShipServiceLevel"],
                "SalesChannel":["SalesChannel"],
                "FulfillmentChannel":["FulfillmentChannel"],
                "ShippingEmail":["BuyerEmail"],
                "OrderId":["AmazonOrderId"],
                "unique_sales_rec_no":["AmazonOrderId"],
                "PurchaseDate":["PurchaseDate"],
                "NumberOfItemsShipped":["NumberOfItemsShipped"],
                "NumberOfItemsShipped":["NumberOfItemsShipped"],
                "OrderStatus":["OrderStatus"],
                "PaymentMethod":["PaymentMethod"],
                }

    def toErp(self,object,root,map):
        info = {}
        return info


class ListOrders:
    Session = Session()
    def __init__(self, access_key, secret_key, merchant_id, marketplace_id, site):
        self.Session.Initialize(access_key, secret_key, merchant_id, marketplace_id, site)

    def getErrors(self, node):
        info = {}
        for node in node:
            for cNode in node.childNodes:
                if cNode.nodeName == 'Message':
                     info['Error'] = cNode.childNodes[0].data
        return info
    def getOrderdetails(self, nodelist):
        transDetails = []
        for node in nodelist:
            info = {}
            for cNode in node.childNodes:
                if cNode.nodeName == 'ShippingAddress':
                    if len(cNode.childNodes):
                        for gcNode in cNode.childNodes:
                            if gcNode.nodeName == 'Name':
                                info['ShippingCompanyName'] = gcNode.childNodes[0].data
                                info['BillingCompanyName'] = gcNode.childNodes[0].data
                                info['ShippingName'] = gcNode.childNodes[0].data
                                info['BillingName'] = gcNode.childNodes[0].data
                            elif gcNode.nodeName == 'AddressLine1':
                                info['ShippingAddressLine1'] = gcNode.childNodes[0].data
                                info['BillingAddressLine1'] = gcNode.childNodes[0].data
                            elif gcNode.nodeName == 'AddressLine2':
                                info['ShippingAddressLine2'] = gcNode.childNodes[0].data
                                info['BillingAddressLine2'] = gcNode.childNodes[0].data
                            elif gcNode.nodeName == 'City':
                                info['ShippingCity'] = gcNode.childNodes[0].data
                                info['BillingCity'] = gcNode.childNodes[0].data
                            elif gcNode.nodeName == 'StateOrRegion':
                                info['ShippingStateOrRegion'] = gcNode.childNodes[0].data
                                info['BillingStateOrRegion'] = gcNode.childNodes[0].data
                            elif gcNode.nodeName == 'PostalCode':
                                info['ShippingPostalCode'] = gcNode.childNodes[0].data
                                info['BillingPostalCode'] = gcNode.childNodes[0].data
                            elif gcNode.nodeName == 'Phone':
                                info['ShippingPhone'] = gcNode.childNodes[0].data
                                info['BillingPhone'] = gcNode.childNodes[0].data
                            elif gcNode.nodeName == 'CountryCode':
                                info['ShippingCountryCode'] = gcNode.childNodes[0].data
                                info['BillingCountryCode'] = gcNode.childNodes[0].data
                elif cNode.nodeName == 'ShipServiceLevel':
                    info['Carrier'] = cNode.childNodes[0].data.split(" ")[0]
                elif cNode.nodeName == 'SalesChannel':
                    info[cNode.nodeName] = cNode.childNodes[0].data
                elif cNode.nodeName == 'FulfillmentChannel':
                    info[cNode.nodeName] = cNode.childNodes[0].data
                elif cNode.nodeName == 'BuyerEmail':
                    info['ShippingEmail'] = cNode.childNodes[0].data
                elif cNode.nodeName == 'AmazonOrderId':
                    info['OrderId'] = cNode.childNodes[0].data
                    info['unique_sales_rec_no'] = cNode.childNodes[0].data
                elif cNode.nodeName == 'PurchaseDate':
                    info['PurchaseDate'] = cNode.childNodes[0].data
                elif cNode.nodeName == 'NumberOfItemsShipped':
                    info[cNode.nodeName] = cNode.childNodes[0].data
                elif cNode.nodeName == 'OrderStatus':
                    info[cNode.nodeName] = cNode.childNodes[0].data
                elif cNode.nodeName == 'LastUpdateDate':
                    info[cNode.nodeName] = cNode.childNodes[0].data
                elif cNode.nodeName == 'PaymentMethod':
                    info[cNode.nodeName] = cNode.childNodes[0].data
            info['paid'] = True
            transDetails.append(info)
        return transDetails

    def Get(self,timefrom,timeto,fulfilmentChannel):
        x = mws.Orders(access_key=access_key, secret_key=secret_key, account_id=merchant_id,region=region)
        orders = x.list_orders(marketplaceids=[market_place_id], created_after='2014-08-04T11:00:00Z', created_before='2014-08-04T13:00:00Z')#, lastupdatedafter, lastupdatedbefore, orderstatus, fulfillment_channels, payment_methods, buyer_email, seller_orderid, max_results)
        response_data = orders.original
        print response_data
        
        od = orders.parsed
        
        api = Call()
        api.Session = self.Session
        version = '2011-01-01'
        method= 'ListOrders'
        command = '/Orders/2011-01-01?'
        url_params ={'Action':method,'SellerId':self.Session.merchant_id,'MarketplaceId.Id.1':self.Session.marketplace_id,'AWSAccessKeyId':self.Session.access_key,'SignatureVersion':'2','SignatureMethod':'HmacSHA256','Version':version}
#        url_params ={'Action':method,'SellerId':self.Session.merchant_id,'MarketplaceId.Id.1':self.Session.marketplace_id,'OrderStatus.Status.1':'Shipped','AWSAccessKeyId':self.Session.access_key,'SignatureVersion':'2','SignatureMethod':'HmacSHA256','Version':version}

        if timefrom:
            url_params['LastUpdatedAfter'] = timefrom
        if timeto:
            url_params['LastUpdatedBefore'] = timeto

        if fulfilmentChannel == 'MFN':
            url_params['OrderStatus.Status.1'] = 'Unshipped'
            url_params['OrderStatus.Status.2'] = 'PartiallyShipped'
        else:
            url_params['OrderStatus.Status.1'] = 'Shipped'

        url_params['FulfillmentChannel.Channel.1'] = fulfilmentChannel

        post_data = '/Orders/2011-01-01'
        api.RequestData =''
        url_string = api.calc_signature(url_params,post_data)
        api.url_string  = str(command) + url_string
        responseDOM = api.MakeCall('ListOrders')
        getOrderdetails = {}

        responseDOM = api.MakeCallRepeat(responseDOM,url_params,post_data,command,method)
        #After successful result
        getOrderdetails = self.getOrderdetails(responseDOM.getElementsByTagName('Order'))
        print 'getOrderdetails',getOrderdetails
        print 'responseDOM.getElementsByTagName',responseDOM.getElementsByTagName('NextToken')

        if responseDOM.getElementsByTagName('NextToken'):
            getOrderdetails = getOrderdetails + [{'NextToken':responseDOM.getElementsByTagName('NextToken')[0].childNodes[0].data}]
            
        return getOrderdetails

class GetOrderBYID:
    Session = Session()
    def __init__(self, access_key, secret_key, merchant_id, marketplace_id, site):
        self.Session.Initialize(access_key, secret_key, merchant_id, marketplace_id, site)

    def getErrors(self, node):
        info = {}
        for node in node:
            for cNode in node.childNodes:
                if cNode.nodeName == 'Message':
                     info['Error'] = cNode.childNodes[0].data
        return info
    def getOrderdetails(self, nodelist):
        transDetails = []
        for node in nodelist:
            info = {}
            for cNode in node.childNodes:
                if cNode.nodeName == 'ShippingAddress':
                    if len(cNode.childNodes):
                        for gcNode in cNode.childNodes:
                            if gcNode.nodeName == 'Name':
                                info['ShippingCompanyName'] = gcNode.childNodes[0].data
                                info['BillingCompanyName'] = gcNode.childNodes[0].data
                                info['ShippingName'] = gcNode.childNodes[0].data
                                info['BillingName'] = gcNode.childNodes[0].data
                            elif gcNode.nodeName == 'AddressLine1':
                                info['ShippingAddressLine1'] = gcNode.childNodes[0].data
                                info['BillingAddressLine1'] = gcNode.childNodes[0].data
                            elif gcNode.nodeName == 'AddressLine2':
                                info['ShippingAddressLine2'] = gcNode.childNodes[0].data
                                info['BillingAddressLine2'] = gcNode.childNodes[0].data
                            elif gcNode.nodeName == 'City':
                                info['ShippingCity'] = gcNode.childNodes[0].data
                                info['BillingCity'] = gcNode.childNodes[0].data
                            elif gcNode.nodeName == 'StateOrRegion':
                                info['ShippingStateOrRegion'] = gcNode.childNodes[0].data
                                info['BillingStateOrRegion'] = gcNode.childNodes[0].data
                            elif gcNode.nodeName == 'PostalCode':
                                info['ShippingPostalCode'] = gcNode.childNodes[0].data
                                info['BillingPostalCode'] = gcNode.childNodes[0].data
                            elif gcNode.nodeName == 'Phone':
                                info['ShippingPhone'] = gcNode.childNodes[0].data
                                info['BillingPhone'] = gcNode.childNodes[0].data
                            elif gcNode.nodeName == 'CountryCode':
                                info['ShippingCountryCode'] = gcNode.childNodes[0].data
                                info['BillingCountryCode'] = gcNode.childNodes[0].data
                elif cNode.nodeName == 'ShipServiceLevel':
                    info['Carrier'] = cNode.childNodes[0].data.split(" ")[0]
                elif cNode.nodeName == 'FulfillmentChannel':
                    info[cNode.nodeName] = cNode.childNodes[0].data
                elif cNode.nodeName == 'BuyerEmail':
                    info['ShippingEmail'] = cNode.childNodes[0].data
                elif cNode.nodeName == 'AmazonOrderId':
                    info['OrderId'] = cNode.childNodes[0].data
                elif cNode.nodeName == 'PurchaseDate':
                    info['PurchaseDate'] = cNode.childNodes[0].data
                elif cNode.nodeName == 'NumberOfItemsShipped':
                    info[cNode.nodeName] = cNode.childNodes[0].data
                elif cNode.nodeName == 'OrderStatus':
                    info[cNode.nodeName] = cNode.childNodes[0].data
            info['paid'] = True
            transDetails.append(info)
        return transDetails

    def Get(self,order_id):
        api = Call()
        api.Session = self.Session
        version = '2011-01-01'
        method= 'GetOrder'
        command = '/Orders/2011-01-01?'
        url_params = {'Action':method,'SellerId':self.Session.merchant_id,'AWSAccessKeyId':self.Session.access_key,'SignatureVersion':'2','SignatureMethod':'HmacSHA256','Version':version}
        url_params['Timestamp'] = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime())+ 'Z'
        url_params['AmazonOrderId.Id.1'] = order_id
        post_data = '/Orders/2011-01-01'
        url_params['Signature'] = api.calc_signature(url_params,post_data)[0]

        url_string = api.calc_signature(url_params,post_data)[1].replace('%0A','')
        api.url_string  = str(command) + url_string
        api.RequestData =''
        responseDOM = api.MakeCall('GetOrder')
        #print"responseDom",responseDOM.toprettyxml()
        getOrderdetails = {}
        getErrordetails = {}
        getOrderdetails = self.getOrderdetails(responseDOM.getElementsByTagName('Order'))
        print 'getOrderdetails',getOrderdetails
        getErrordetails = self.getErrors(responseDOM.getElementsByTagName('Error'))
        if getErrordetails.get('Error',False):
            raise osv.except_osv(_('Error!'), _((getErrordetails.get('Error',False))))
        if responseDOM.getElementsByTagName('NextToken'):
            getOrderdetails = getOrderdetails + [{'NextToken':responseDOM.getElementsByTagName('NextToken')[0].childNodes[0].data}]
        return getOrderdetails

class ListOrderItems:
    Session = Session()
    def __init__(self, access_key, secret_key, merchant_id, marketplace_id, site):
        self.Session.Initialize(access_key, secret_key, merchant_id, marketplace_id, site)

###############################for getting products price###################################
    def getItemPrice(self, node):
        info = {}
        for cNode in node.childNodes:
            if cNode.nodeName == 'Amount':
                 return cNode.childNodes[0].data

    def getShippingPrice(self, node):
        info = {}
        shipping_amount = 0.0
        for cNode in node.childNodes:
            if cNode.nodeName == 'Amount':
                 shipping_amount =  cNode.childNodes[0].data
        return shipping_amount

    def getItemTax(self, node):
        info = {}
        for cNode in node.childNodes:
            if cNode.nodeName == 'Amount':
                 return cNode.childNodes[0].data
#############################for getting product details######################################
    def getProductdetails(self, nodelist):
        productDetails = []
        for node in nodelist:
            info = {}
            for cNode in node.childNodes:
                if cNode.nodeName == 'OrderItem':
                    if len(cNode.childNodes):
                        for gcNode in cNode.childNodes:
                            if gcNode.nodeName == 'ASIN':
                                info['listing_id'] = gcNode.childNodes[0].data
                            elif gcNode.nodeName == 'Title':
                                info[gcNode.nodeName] = gcNode.childNodes[0].data
                            elif gcNode.nodeName == 'SellerSKU':
                                info[gcNode.nodeName] = gcNode.childNodes[0].data
                            elif gcNode.nodeName == 'OrderItemId':
                                info[gcNode.nodeName] = gcNode.childNodes[0].data
                                info['unique_sales_line_rec_no'] = gcNode.childNodes[0].data
                            elif gcNode.nodeName == 'ItemPrice':
                                info['ItemPriceTotal'] = self.getItemPrice(gcNode)
                            elif gcNode.nodeName == 'ShippingPrice':
                                info[gcNode.nodeName] = self.getShippingPrice(gcNode)
                            elif gcNode.nodeName == 'ItemTax':
                                info[gcNode.nodeName] = self.getItemTax(gcNode)
                            elif gcNode.nodeName == 'ShippingTax':
                                info[gcNode.nodeName] = self.getItemTax(gcNode)
                            elif gcNode.nodeName == 'QuantityOrdered':
                                info[gcNode.nodeName] = gcNode.childNodes[0].data

                        print 'info===',info
                        if int(info['QuantityOrdered']) > 0:
                            print "innnnnnnnnnnnnnnnnnnnnnnn"
                            info['ItemPrice'] = float(info['ItemPriceTotal']) / float(info['QuantityOrdered'])
                            productDetails.append(info)
                        print "--------------------------------------kkkkkkkkkkkkkkkkkkkkkkkkkkk"
                        info ={}

        return productDetails


    def Get(self,order_id):
        api = Call()
        api.Session = self.Session
        version = '2011-01-01'
        method= 'ListOrderItems'
        command = '/Orders/2011-01-01?'
        url_params = {'Action':method,'SellerId':self.Session.merchant_id,'AWSAccessKeyId':self.Session.access_key,'SignatureVersion':'2','SignatureMethod':'HmacSHA256','Version':version}
        url_params['Timestamp'] = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime())+ 'Z'
        url_params['AmazonOrderId'] = order_id
        post_data = '/Orders/2011-01-01'
        api.RequestData =''
        url_string = api.calc_signature(url_params,post_data)
        api.url_string  = str(command) + url_string
        responseDOM = api.MakeCall('ListOrderItems')
        getproductinfo = {}

        responseDOM = api.MakeCallRepeat(responseDOM,url_params,post_data,command,method)

        getproductinfo = self.getProductdetails(responseDOM.getElementsByTagName('OrderItems'))
        if responseDOM.getElementsByTagName('NextToken'):
            getproductinfo = getOrderdetails + [{'NextToken':responseDOM.getElementsByTagName('NextToken')[0].childNodes[0].data}]
        return getproductinfo

class ListOrdersByNextToken:
    Session = Session()
    def __init__(self, access_key, secret_key, merchant_id, marketplace_id, site):
        self.Session.Initialize(access_key, secret_key, merchant_id, marketplace_id, site)


    def getOrderdetails(self, nodelist):
        transDetails = []
        for node in nodelist:
            info = {}
            for cNode in node.childNodes:
                if cNode.nodeName == 'ShippingAddress':
                    if len(cNode.childNodes):
                        for gcNode in cNode.childNodes:
                            if gcNode.nodeName == 'Name':
                                info['ShippingCompanyName'] = gcNode.childNodes[0].data
                                info['BillingCompanyName'] = gcNode.childNodes[0].data
                                info['ShippingName'] = gcNode.childNodes[0].data
                                info['BillingName'] = gcNode.childNodes[0].data
                            elif gcNode.nodeName == 'AddressLine1':
                                info['ShippingAddressLine1'] = gcNode.childNodes[0].data
                                info['BillingAddressLine1'] = gcNode.childNodes[0].data
                            elif gcNode.nodeName == 'AddressLine2':
                                info['ShippingAddressLine2'] = gcNode.childNodes[0].data
                                info['BillingAddressLine2'] = gcNode.childNodes[0].data
                            elif gcNode.nodeName == 'City':
                                info['ShippingCity'] = gcNode.childNodes[0].data
                                info['BillingCity'] = gcNode.childNodes[0].data
                            elif gcNode.nodeName == 'StateOrRegion':
                                info['ShippingStateOrRegion'] = gcNode.childNodes[0].data
                                info['BillingStateOrRegion'] = gcNode.childNodes[0].data
                            elif gcNode.nodeName == 'PostalCode':
                                info['ShippingPostalCode'] = gcNode.childNodes[0].data
                                info['BillingPostalCode'] = gcNode.childNodes[0].data
                            elif gcNode.nodeName == 'Phone':
                                info['ShippingPhone'] = gcNode.childNodes[0].data
                                info['BillingPhone'] = gcNode.childNodes[0].data
                            elif gcNode.nodeName == 'CountryCode':
                                info['ShippingCountryCode'] = gcNode.childNodes[0].data
                                info['BillingCountryCode'] = gcNode.childNodes[0].data
                elif cNode.nodeName == 'ShipServiceLevel':
                    info['Carrier'] = cNode.childNodes[0].data.split(" ")[0]
                elif cNode.nodeName == 'SalesChannel':
                    info[cNode.nodeName] = cNode.childNodes[0].data
                elif cNode.nodeName == 'FulfillmentChannel':
                    info[cNode.nodeName] = cNode.childNodes[0].data
                elif cNode.nodeName == 'BuyerEmail':
                    info['ShippingEmail'] = cNode.childNodes[0].data
                elif cNode.nodeName == 'AmazonOrderId':
                    info['OrderId'] = cNode.childNodes[0].data
                elif cNode.nodeName == 'PurchaseDate':
                    info['PurchaseDate'] = cNode.childNodes[0].data
                elif cNode.nodeName == 'NumberOfItemsShipped':
                    info[cNode.nodeName] = cNode.childNodes[0].data
                elif cNode.nodeName == 'OrderStatus':
                    info[cNode.nodeName] = cNode.childNodes[0].data
            info['paid'] = True
            transDetails.append(info)
        return transDetails

    def Get(self,next_token):
        api = Call()
        api.Session = self.Session
        version = '2011-01-01'
        method= 'ListOrdersByNextToken'
        command = '/Orders/2011-01-01?'
        url_params = {'Action':method,'SellerId':self.Session.merchant_id,'AWSAccessKeyId':self.Session.access_key,'SignatureVersion':'2','SignatureMethod':'HmacSHA256','Version':version}
        url_params['NextToken'] = next_token
        post_data = '/Orders/2011-01-01'
        api.RequestData =''

        url_string = api.calc_signature(url_params,post_data)
        api.url_string  = str(command) + url_string
        responseDOM = api.MakeCall('ListOrdersByNextToken')
#        print"responseDom",responseDOM.toprettyxml()
        getOrderdetails = {}

        responseDOM = api.MakeCallRepeat(responseDOM,url_params,post_data,command,method)

        #After successful result
        getOrderdetails = self.getOrderdetails(responseDOM.getElementsByTagName('Order'))
        print 'getOrderdetails',getOrderdetails
        print"Next token",responseDOM.getElementsByTagName('NextToken')
        if responseDOM.getElementsByTagName('NextToken'):
            getOrderdetails = getOrderdetails + [{'NextToken':responseDOM.getElementsByTagName('NextToken')[0].childNodes[0].data}]
        return getOrderdetails

class ListOrderItemsByNextToken:
    Session = Session()
    def __init__(self, access_key, secret_key, merchant_id, marketplace_id, site):
        self.Session.Initialize(access_key, secret_key, merchant_id, marketplace_id, site)

    def Get(self,next_token):
        api = Call()
        api.Session = self.Session
        version = '2011-01-01'
        method= 'ListOrderItemsByNextToken'
        command = '/Orders/2011-01-01?'
        url_params = {'Action':method,'SellerId':self.Session.merchant_id,'MarketplaceId.Id.1':self.Session.marketplace_id,'AWSAccessKeyId':self.Session.access_key,'SignatureVersion':'2','SignatureMethod':'HmacSHA256','Version':version}
        url_params['Timestamp'] = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime())+ 'Z'
        url_params['NextToken'] = next_token
        post_data = '/Orders/2011-01-01'
        url_params['Signature'] = api.calc_signature(url_params,post_data)[0]
        url_string = api.calc_signature(url_params,post_data)[1].replace('%0A','')
        api.url_string  = str(command) + url_string
        api.RequestData =''
        responseDoM = api.MakeCall('ListOrderItemsByNextToken')
#        print"responseDom",responseDoM.toprettyxml()

class GetFeedSubmissionResult:
    Session = Session()

    def __init__(self, access_key, secret_key, merchant_id, marketplace_id, site):
        self.Session.Initialize(access_key, secret_key, merchant_id, marketplace_id, site)

    def submitfeedresult(self, nodelist):
        for node in nodelist:
            info = {}
            for cNode in node.childNodes:
                if cNode.nodeName == 'ProcessingReport':
                        if cNode.childNodes:
                            for gcNode in cNode.childNodes:
#                                if gcNode.nodeName == 'Summary':
#                                    for gcNode in gcNode.childNodes:
                                        if gcNode.nodeName == 'ProcessingSummary':
                                            for gccNode in gcNode.childNodes:
                                                if gccNode.nodeName == 'MessagesWithError':
                                                    info[gccNode.nodeName] = gccNode.childNodes[0].data
                                                elif gccNode.nodeName == 'MessagesWithWarning':
                                                    info[gccNode.nodeName] = gccNode.childNodes[0].data
#                                elif gcNode.nodeName == 'Result':
#                                        for gccNode in gcNode.childNodes:
#                                            if gccNode.nodeName == 'ResultDescription':
#                                                info[gccNode.nodeName] = gccNode.childNodes[0].data
        return info
    def Get(self,FeedSubmissionId):
        api = Call()
        api.Session = self.Session
        version = '2009-01-01'
        method= 'GetFeedSubmissionResult'
        command = '/?'
        url_params = {'Action':method,'Merchant':self.Session.merchant_id,'AWSAccessKeyId':self.Session.access_key,'SignatureVersion':'2','SignatureMethod':'HmacSHA256','Version':version}
        url_params['FeedSubmissionId'] = FeedSubmissionId
        post_data = '/'
        url_string = api.calc_signature(url_params,post_data)
        api.url_string  = str(command) + url_string
        api.RequestData =''
        responseDoM = api.MakeCall('GetFeedSubmissionResult')
        print"responseDom",responseDoM.toprettyxml()
        getsubmitfeedresult = {}
        getsubmitfeedresult = self.submitfeedresult(responseDoM.getElementsByTagName('Message'))
        print"getsubmitfeedresult",getsubmitfeedresult
        return getsubmitfeedresult


class POST_INVENTORY_AVAILABILITY_DATA:
    Session = Session()

    def getErrors(self, node):
        info = {}
        for node in node:
            for cNode in node.childNodes:
                if cNode.nodeName == 'Message':
                     info['Error'] = cNode.childNodes[0].data
        return info


    def submitresult(self, nodelist):
        info = {}
        for node in nodelist:

            for cNode in node.childNodes:
                if cNode.nodeName == 'FeedSubmissionInfo':
                    if cNode.childNodes[0].childNodes:
                        for gcNode in cNode.childNodes:
                            if gcNode.nodeName == 'FeedSubmissionId':
                                info[gcNode.nodeName] = gcNode.childNodes[0].data
        return info

    def __init__(self, access_key, secret_key, merchant_id, marketplace_id, site_id):
        self.Session.Initialize(access_key, secret_key, merchant_id, marketplace_id, site_id)

    def Get(self,requestData):
        requestData = requestData.strip()
        print"requestData In INVENTORY",requestData
        api = Call()
        api.Session = self.Session
        version = '2009-01-01'
        method = 'SubmitFeed'
        command = '/?'
        url_params = {'Action':method,'Merchant':self.Session.merchant_id,'FeedType':'_POST_INVENTORY_AVAILABILITY_DATA_','AWSAccessKeyId':self.Session.access_key,'SignatureVersion':'2','SignatureMethod':'HmacSHA256','Version':version}
        url_params['PurgeAndReplace'] = 'false'
        post_data = '/'
        url_string = api.calc_signature(url_params,post_data)
        api.url_string  = str(command) + url_string
        api.RequestData = requestData
        responseDOM = api.MakeCall('POST_INVENTORY_AVAILABILITY_DATA')
#        print"responseDom",responseDOM.toprettyxml()
        getsubmitfeed = {}
        responseDOM = api.MakeCallRepeat(responseDOM,url_params,post_data,command,'POST_INVENTORY_AVAILABILITY_DATA')

        getsubmitfeed = self.submitresult(responseDOM.getElementsByTagName('SubmitFeedResult'))
        return getsubmitfeed

class POST_ORDER_FULFILLMENT_DATA:
    Session = Session()
    def __init__(self, access_key, secret_key, merchant_id, marketplace_id, site):
        self.Session.Initialize(access_key, secret_key, merchant_id, marketplace_id, site)

    def getErrors(self, node):
        info = {}
        for node in node:
            for cNode in node.childNodes:
                if cNode.nodeName == 'Message':
                     info['Error'] = cNode.childNodes[0].data
        return info


    def submitresult(self, nodelist):
        for node in nodelist:
            info = {}
            for cNode in node.childNodes:
                if cNode.nodeName == 'FeedSubmissionInfo':
                    if cNode.childNodes[0].childNodes:
                        for gcNode in cNode.childNodes:
                            if gcNode.nodeName == 'FeedSubmissionId':
                                info[gcNode.nodeName] = gcNode.childNodes[0].data
        return info
    def Get(self,requestData):
        requestData = requestData.strip()
        print"requestdata",requestData
        api = Call()
        api.Session = self.Session
        version = '2009-01-01'
        method = 'SubmitFeed'
        command = '/?'
        url_params = {'Action':method,'Merchant':self.Session.merchant_id,'FeedType':'_POST_ORDER_FULFILLMENT_DATA_','AWSAccessKeyId':self.Session.access_key,'SignatureVersion':'2','SignatureMethod':'HmacSHA256','Version':version}
        
        url_params['PurgeAndReplace'] = 'false'
        post_data = '/'
        url_string = api.calc_signature(url_params,post_data)
        api.url_string  = str(command) + url_string
        api.RequestData = requestData
        responseDOM = api.MakeCall('POST_ORDER_FULFILLMENT_DATA')
        responseDOM = api.MakeCallRepeat(responseDOM,url_params,post_data,command,'POST_ORDER_FULFILLMENT_DATA')

        getsubmitfeed = {}
        getsubmitfeed = self.submitresult(responseDOM.getElementsByTagName('SubmitFeedResult'))
        print"getsubmitfee",getsubmitfeed
        return getsubmitfeed

    
class GetMyPriceForSKU:
    Session = Session()
    def __init__(self, access_key, secret_key, merchant_id, marketplace_id, site):
        self.Session.Initialize(access_key, secret_key, merchant_id, marketplace_id, site)

    def getErrors(self, node):
        info = {}
        for node in node:
            for cNode in node.childNodes:
                if cNode.nodeName == 'Message':
                     info['Error'] = cNode.childNodes[0].data
        return info
    
    def Get(self,asin_list):
        api = Call()
        api.Session = self.Session
        buy_box=False
        command = '/Products/2011-10-01?'
        version = '2011-10-01'
        method = 'GetMyPriceForSKU'
        url_params ={'Action':method,'SellerId':self.Session.merchant_id,'MarketplaceId':self.Session.marketplace_id,'AWSAccessKeyId':self.Session.access_key,'SignatureVersion':'2','SignatureMethod':'HmacSHA256','Version':version}
        if len(asin_list):
            count = 1
            for asin in asin_list:
                if asin:
                    asin_key = 'ASINList.ASIN.'+ str(count)
                    print 'm====='
                    count += 1
                    url_params[asin_key] = asin
                    if count ==21:
                        break

        post_data = '/Products/2011-10-01'
        url_string = api.calc_signature(url_params,post_data)
        api.url_string  = str(command) + url_string
        api.RequestData = ''
        responseDOM = api.MakeCall(method)

        responseDOM = api.MakeCallRepeat(responseDOM,url_params,post_data,command,'GetMyPriceForSKU')
        
        data_list=[]
        node_list=responseDOM.getElementsByTagName('GetMyPriceForSKUResult')
        for cNode in node_list:
            info={}
            for cNode1 in cNode.childNodes:
                if cNode1.nodeName == 'Product':
                    for cNode3 in cNode1.childNodes:
                        if cNode3.nodeName == 'Identifiers':
                            for cNode4 in cNode3.childNodes:
                                if cNode4.nodeName == 'MarketplaceASIN':
                                    for cNode5 in cNode4.childNodes:
                                        if cNode5.nodeName == 'ASIN':
                                            info[cNode5.nodeName] = cNode5.childNodes[0].data
                        if cNode3.nodeName == 'SalesRankings':
                            for cNode4 in cNode3.childNodes:
                                if cNode4.nodeName == 'SalesRank':
                                    for cNode5 in cNode4.childNodes:
                                        if cNode5.nodeName == 'Rank':
                                            info[cNode5.nodeName] = cNode5.childNodes[0].data
                                        elif cNode5.nodeName == 'ProductCategoryId':
                                            info[cNode5.nodeName] = cNode5.childNodes[0].data
                    for cNode11 in cNode1.childNodes:
                        if cNode11.nodeName == 'Offers':
                            for cNode21 in cNode11.childNodes:
                                if cNode21.nodeName == 'Offer':
                                    for cNode3 in cNode21.childNodes:
                                        print 'ccNode21===',cNode3.nodeName
                                        if cNode3.nodeName == 'BuyingPrice':
                                            for cNode4 in cNode3.childNodes:
                                                if cNode4.nodeName == 'LandedPrice':
                                                    for cNode5 in cNode4.childNodes:
                                                        if cNode5.nodeName == 'Amount':
                                                            info[cNode5.nodeName] = cNode5.childNodes[0].data
                                                if cNode4.nodeName == 'Shipping':
                                                    for cNode5 in cNode4.childNodes:
                                                        if cNode5.nodeName == 'Amount':
                                                            info['Shipping'] = cNode5.childNodes[0].data
                                        if cNode3.nodeName in ['ItemCondition','ItemSubCondition']:
                                           info[cNode3.nodeName] = cNode3.childNodes[0].data
                                           

            data_list.append(info)
        print'data_list',data_list
        return data_list
    
class GetCompetitivePricingForASIN:
    Session = Session()
    def __init__(self, access_key, secret_key, merchant_id, marketplace_id):
        self.Session.Initialize(access_key, secret_key, merchant_id, marketplace_id)

    def getErrors(self, node):
        info = {}
        for node in node:
            for cNode in node.childNodes:
                if cNode.nodeName == 'Message':
                     info['Error'] = cNode.childNodes[0].data
        return info

    def Get(self,asin_list):
        api = Call()
        api.Session = self.Session
        buy_box=False
        command = '/Products/2011-10-01?'
        version = '2011-10-01'
        method = 'GetCompetitivePricingForASIN'
        url_params ={'Action':method,'SellerId':self.Session.merchant_id,'MarketplaceId':self.Session.marketplace_id,'AWSAccessKeyId':self.Session.access_key,'SignatureVersion':'2','SignatureMethod':'HmacSHA256','Version':version}
        if len(asin_list):
            count = 1
            for asin in asin_list:
                if asin:
                    asin_key = 'ASINList.ASIN.'+ str(count)
                    print 'm====='
                    count += 1
                    url_params[asin_key] = asin
                    if count ==21:
                        break

        post_data = '/Products/2011-10-01'
        url_string = api.calc_signature(url_params,post_data)
        api.url_string  = str(command) + url_string
        api.RequestData = ''
        responseDOM = api.MakeCall(method)

        responseDOM = api.MakeCallRepeat(responseDOM,url_params,post_data,command,'GetCompetitivePricingForASIN')

        data_list=[]
        node_list=responseDOM.getElementsByTagName('GetCompetitivePricingForASINResult')
        for cNode in node_list:
            info={}
            for cNode1 in cNode.childNodes:
                if cNode1.nodeName == 'Product':
                    for cNode3 in cNode1.childNodes:
                        if cNode3.nodeName == 'Identifiers':
                            for cNode4 in cNode3.childNodes:
                                if cNode4.nodeName == 'MarketplaceASIN':
                                    for cNode5 in cNode4.childNodes:
                                        if cNode5.nodeName == 'ASIN':
                                            info[cNode5.nodeName] = cNode5.childNodes[0].data
                        if cNode3.nodeName == 'SalesRankings':
                            for cNode4 in cNode3.childNodes:
                                if cNode4.nodeName == 'SalesRank':
                                    for cNode5 in cNode4.childNodes:
                                        if cNode5.nodeName == 'Rank':
                                            info[cNode5.nodeName] = cNode5.childNodes[0].data
                                        elif cNode5.nodeName == 'ProductCategoryId':
                                            info[cNode5.nodeName] = cNode5.childNodes[0].data
                    for cNode11 in cNode1.childNodes:
                        if cNode11.nodeName == 'CompetitivePricing':
                            for cNode2 in cNode11.childNodes:
                                if cNode2.nodeName == 'CompetitivePrices':
                                    for cNode21 in cNode2.childNodes:
                                        if cNode21.nodeName == 'CompetitivePrice':
                                            if cNode21.getAttribute('belongsToRequester')=='true':
                                                info['buy_box']=True
                                            for cNode3 in cNode21.childNodes:
                                                print 'ccNode21===',cNode3.nodeName
                                                if cNode3.nodeName == 'Price':
                                                    for cNode4 in cNode3.childNodes:
                                                        if cNode4.nodeName == 'LandedPrice':
                                                            for cNode5 in cNode4.childNodes:
                                                                if cNode5.nodeName == 'Amount':
                                                                    info[cNode5.nodeName] = cNode5.childNodes[0].data
                                                        if cNode4.nodeName == 'Shipping':
                                                            for cNode5 in cNode4.childNodes:
                                                                if cNode5.nodeName == 'Amount':
                                                                    info['Shipping'] = cNode5.childNodes[0].data

            data_list.append(info)
        print'data_list',data_list
        return data_list

    
class POST_PRODUCT_PRICING_DATA:
    Session = Session()
    def __init__(self, access_key, secret_key, merchant_id, marketplace_id, site_id):
        self.Session.Initialize(access_key, secret_key, merchant_id, marketplace_id, site_id)

    def getErrors(self, node):
        info = {}
        for node in node:
            for cNode in node.childNodes:
                if cNode.nodeName == 'Message':
                     info['Error'] = cNode.childNodes[0].data
        return info

    def submitresult(self, nodelist):
        info = {}
        for node in nodelist:
            for cNode in node.childNodes:
                if cNode.nodeName == 'FeedSubmissionInfo':
                    if cNode.childNodes[0].childNodes:
                        for gcNode in cNode.childNodes:
                            if gcNode.nodeName == 'FeedSubmissionId':
                                info[gcNode.nodeName] = gcNode.childNodes[0].data
        return info
    def Get(self,requestData):
        requestData = requestData.strip()
        api = Call()
        api.Session = self.Session
        version = '2009-01-01'
        method = 'SubmitFeed'
        command = '/?'
        url_params = {'Action':method,'Merchant':self.Session.merchant_id,'FeedType':'_POST_PRODUCT_PRICING_DATA_','AWSAccessKeyId':self.Session.access_key,'SignatureVersion':'2','SignatureMethod':'HmacSHA256','Version':version}
        url_params['PurgeAndReplace'] = 'false'
        post_data = '/'
        url_string = api.calc_signature(url_params,post_data)
        api.url_string  = str(command) + url_string
        api.RequestData = requestData
        responseDOM = api.MakeCall('POST_PRODUCT_PRICING_DATA')
        print"responseDom pricing Update",responseDOM.toprettyxml()

        getsubmitfeed = {}
        responseDOM = api.MakeCallRepeat(responseDOM,url_params,post_data,command,'POST_PRODUCT_PRICING_DATA')

        getsubmitfeed = self.submitresult(responseDOM.getElementsByTagName('SubmitFeedResult'))
        return getsubmitfeed

class POST_PRODUCT_DATA:
    Session = Session()
    def __init__(self, access_key, secret_key, merchant_id, marketplace_id, site_id):
        self.Session.Initialize(access_key, secret_key, merchant_id, marketplace_id, site_id)

    def submitresult(self, nodelist):
        info = {}
        for node in nodelist:
            for cNode in node.childNodes:
                if cNode.nodeName == 'FeedSubmissionInfo':
                    if cNode.childNodes[0].childNodes:
                        for gcNode in cNode.childNodes:
                            if gcNode.nodeName == 'FeedSubmissionId':
                                info[gcNode.nodeName] = gcNode.childNodes[0].data
        return info
    def Get(self,requestData):
        requestData = requestData.strip()
        api = Call()
        api.Session = self.Session
        version = '2009-01-01'
        method = 'SubmitFeed'
        command = '/?'
        url_params = {'Action':method,'Merchant':self.Session.merchant_id,'FeedType':'_POST_PRODUCT_DATA_','AWSAccessKeyId':self.Session.access_key,'SignatureVersion':'2','SignatureMethod':'HmacSHA256','Version':version}
        url_params['Timestamp'] = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime())+ 'Z'
        url_params['PurgeAndReplace'] = 'false'
        post_data = '/'
        api.RequestData =requestData
        url_string = api.calc_signature(url_params,post_data)
        api.url_string  = str(command) + url_string
        responseDOM = api.MakeCall('POST_PRODUCT_DATA')
        getOrderdetails = {}

        responseDOM = api.MakeCallRepeat(responseDOM,url_params,post_data,command,method)
      
        print"responseDom",responseDOM.toprettyxml()
        getsubmitfeed = {}
        getsubmitfeed = self.submitresult(responseDOM.getElementsByTagName('SubmitFeedResult'))
        print"getsubmitfee",getsubmitfeed
        return getsubmitfeed

class RequestReport:
    Session = Session()
    def __init__(self, access_key, secret_key, merchant_id, marketplace_id, site):
        self.Session.Initialize(access_key, secret_key, merchant_id, marketplace_id, site)

    def getErrors(self, nodes):
        info = {}
        for node in nodes:
            for cNode in node.childNodes:
                if cNode.nodeName == 'Message':
                     info['Error'] = cNode.childNodes[0].data

        return info

    def submitresult(self, nodelist):
        info = {}

        for node in nodelist:
            for cNode in node.childNodes:
                if cNode.nodeName == 'ReportRequestId':
                   info[cNode.nodeName] = cNode.childNodes[0].data
                elif cNode.nodeName == 'ReportProcessingStatus':
                   info[cNode.nodeName] = cNode.childNodes[0].data
        return info

    def Get(self,requestData,request_type,date):
        requestData = requestData.strip()
        print"requestdata",requestData
        api = Call()
        api.Session = self.Session
        version = '2009-01-01'
        method = 'RequestReport'
        command = '/?'
        url_params = {}
        if date:
            url_params['StartDate'] = date
        url_params = {'Action':method,'Merchant':self.Session.merchant_id,'ReportType':request_type,'AWSAccessKeyId':self.Session.access_key,'SignatureVersion':'2','SignatureMethod':'HmacSHA256','Version':version}
        
        post_data = '/'
        url_string = api.calc_signature(url_params,post_data)
        api.url_string  = str(command) + url_string
        api.RequestData = requestData
        responseDOM = api.MakeCall('RequestReport')
        print "=======responseDOM=========>",(responseDOM.toprettyxml()).encode('utf-8')
        responseDOM = api.MakeCallRepeat(responseDOM,url_params,post_data,command,method)

        #After successful result
        getsubmitfeed = self.submitresult(responseDOM.getElementsByTagName('ReportRequestInfo'))
        return getsubmitfeed

class CreateInboundShipmentPlan:
    Session = Session()
    def __init__(self, access_key, secret_key, merchant_id, marketplace_id, site):
        self.Session.Initialize(access_key, secret_key, merchant_id, marketplace_id, site)

    def submitresult(self, nodelist):
        info = {}

        for node in nodelist:
            for cNode in node.childNodes:
                if cNode.nodeName == 'ReportRequestId':
                   info[cNode.nodeName] = cNode.childNodes[0].data
                elif cNode.nodeName == 'ReportProcessingStatus':
                   info[cNode.nodeName] = cNode.childNodes[0].data
        return info

    def Get(self,requestData):
        api = Call()
        api.Session = self.Session
        version = '2010-10-01'
        method = 'CreateInboundShipmentPlan'
        command = '/FulfillmentInboundShipment/2010-10-01?'
        url_params = {'Action':method,'SellerId':self.Session.merchant_id,'AWSAccessKeyId':self.Session.access_key,'SignatureVersion':'2','SignatureMethod':'HmacSHA256','Version':version}
        url_params.update(requestData)
        post_data = '/FulfillmentInboundShipment/2010-10-01'
        url_string = api.calc_signature(url_params,post_data)
#        url_string = url_string.replace('+','%20')
        api.url_string  = str(command) + url_string
        api.RequestData = ''
        responseDOM = api.MakeCall(method)
        responseDOM = api.MakeCallRepeat(responseDOM,url_params,post_data,command,method)
        print'responseDOM',responseDOM.toprettyxml()
#        After successful result
#        api = Call()
#        api.Session = self.Session
#        version = '2011-01-01'
#        method= 'CreateInboundShipmentPlan'
#        command = '/FulfillmentInboundShipment/2010-10-01?'
#        post_data = '/FulfillmentInboundShipment/2010-10-01'
#        url_params = {'Action':method,'SellerId':self.Session.merchant_id,'AWSAccessKeyId':self.Session.access_key,'SignatureVersion':'2','SignatureMethod':'HmacSHA256','Version':version}
#        url_params += requestData
#        url_string = api.calc_signature(url_params,post_data)
#        api.url_string  = str(command) + url_string
#        api.RequestData =''
#        responseDOM = api.MakeCall('CreateInboundShipmentPlan')
#        responseDOM = api.MakeCallRepeat(responseDOM,url_params,post_data,command,method)
#        print'responseDOM',responseDOM.toprettyxml()
        
        all_items=[]
        results=[]
        node_list=responseDOM.getElementsByTagName('CreateInboundShipmentPlanResult')
        for cNode in node_list:
            for cNode1 in cNode.childNodes:
                if cNode1.nodeName == 'InboundShipmentPlans':
                    for cNode3 in cNode1.childNodes:
                        ship_data ={}
                        if cNode3.nodeName == 'member':
                            all_items=[]
                            for cNode4 in cNode3.childNodes:
                                if cNode4.nodeName == 'ShipmentId':
                                    print'cNode4.nodeName',cNode4.childNodes[0].data
                                    ship_data['ShipmentId']= cNode4.childNodes[0].data
                                elif cNode4.nodeName == 'DestinationFulfillmentCenterId':
                                    ship_data['CenterId']= cNode4.childNodes[0].data
                                elif cNode4.nodeName == 'ShipToAddress':
                                    for cNode5 in cNode4.childNodes:
                                        if cNode5.nodeName == 'Name':
                                            ship_data['AddressName']=cNode5.childNodes[0].data
                                        if cNode5.nodeName == 'PostalCode':
                                            ship_data['PostalCode']=cNode5.childNodes[0].data
                                        if cNode5.nodeName == 'CountryCode':
                                            ship_data['CountryCode']=cNode5.childNodes[0].data
                                        if cNode5.nodeName == 'StateOrProvinceCode':
                                            ship_data['StateOrProvinceCode']=cNode5.childNodes[0].data
                                        if cNode5.nodeName == 'AddressLine1':
                                            ship_data['AddressLine1']=cNode5.childNodes[0].data
                                        if cNode5.nodeName == 'City':
                                            ship_data['City']=cNode5.childNodes[0].data
                                elif cNode4.nodeName == 'Items':
                                    for cNode5 in cNode4.childNodes:
                                        if cNode5.nodeName == 'member':
                                            produts_list={}
                                            for cNode6 in cNode5.childNodes:
                                                if cNode6.nodeName == 'SellerSKU':
                                                    produts_list['SellerSKU']=cNode6.childNodes[0].data
                                                if cNode6.nodeName == 'Quantity':
                                                    produts_list['Quantity']=cNode6.childNodes[0].data
                                            all_items.append(produts_list)
                            ship_data['Items']=all_items
                            results.append(ship_data)
                            
        return results

class CreateInboundShipment:
    Session = Session()
    def __init__(self, access_key, secret_key, merchant_id, marketplace_id, site):
        self.Session.Initialize(access_key, secret_key, merchant_id, marketplace_id, site)

    def Get(self,requestData):
        api = Call()
        api.Session = self.Session
        version = '2010-10-01'
        method = 'CreateInboundShipment'
        command = '/FulfillmentInboundShipment/2010-10-01?'
        url_params = {'Action':method,'SellerId':self.Session.merchant_id,'AWSAccessKeyId':self.Session.access_key,'SignatureVersion':'2','SignatureMethod':'HmacSHA256','Version':version}
        url_params.update(requestData)
        post_data = '/FulfillmentInboundShipment/2010-10-01'
        url_string = api.calc_signature(url_params,post_data)
#        url_string = url_string.replace('+','%2')
        api.url_string  = str(command) + url_string
        
        api.RequestData = ''
        responseDOM = api.MakeCall(method)
        responseDOM = api.MakeCallRepeat(responseDOM,url_params,post_data,command,method)
#        print'responseDOM',responseDOM.toprettyxml()
        #After successful result
        shipment_id = False
        node_list=responseDOM.getElementsByTagName('CreateInboundShipmentResult')
        for cNode in node_list:
            for cNode1 in cNode.childNodes:
                if cNode1.nodeName == 'ShipmentId':
                    shipment_id = cNode1.childNodes[0].data
        print 'shipment_id',shipment_id
        return shipment_id

class GetPackageLabels:
    Session = Session()
    def __init__(self, access_key, secret_key, merchant_id, marketplace_id):
        self.Session.Initialize(access_key, secret_key, merchant_id, marketplace_id)

    def submitresult(self, nodelist):
        info = {}

        for node in nodelist:
            for cNode in node.childNodes:
                if cNode.nodeName == 'ReportRequestId':
                   info[cNode.nodeName] = cNode.childNodes[0].data
                elif cNode.nodeName == 'ReportProcessingStatus':
                   info[cNode.nodeName] = cNode.childNodes[0].data
        return info

    def Get(self,requestData):
        api = Call()
        api.Session = self.Session
        version = '2009-01-01'
        method = 'CreateInboundShipment'
        command = '/FulfillmentInboundShipment/2010-10-01?'
        url_params = {'Action':method,'Merchant':self.Session.merchant_id,'AWSAccessKeyId':self.Session.access_key,'SignatureVersion':'2','SignatureMethod':'HmacSHA256','Version':version}
        url_params.update(requestData)
        post_data = '/FulfillmentInboundShipment/2010-10-01'
        url_string = api.calc_signature(url_params,post_data)
        api.url_string  = str(command) + url_string
        api.RequestData = requestData
        responseDOM = api.MakeCall(method)
        responseDOM = api.MakeCallRepeat(responseDOM,url_params,post_data,command,method)

        #After successful result
        results = self.get_details(responseDOM.getElementsByTagName('ReportRequestInfo'))
        return results


class GetReportRequestList:
    Session = Session()
    def __init__(self, access_key, secret_key, merchant_id, marketplace_id):
        self.Session.Initialize(access_key, secret_key, merchant_id, marketplace_id)

    def submitresult(self, nodelist):
        info = {}
        for node in nodelist:
            for cNode in node.childNodes:
                if cNode.nodeName == 'ReportRequestInfo':
                    for ccNode in cNode.childNodes:
                        if ccNode.nodeName == 'ReportProcessingStatus':
                            info[ccNode.nodeName] = ccNode.childNodes[0].data
                        elif ccNode.nodeName == 'GeneratedReportId':
                            info[ccNode.nodeName] = ccNode.childNodes[0].data

        return info

    def Get(self,requestData,report_id):
        requestData = requestData.strip()
        print"requestdata",requestData
        api = Call()
        api.Session = self.Session
        version = '2009-01-01'
        method = requestData
        command = '/?'
        url_params = {'Action':method,'Merchant':self.Session.merchant_id,'ReportRequestIdList.Id.1':report_id,'AWSAccessKeyId':self.Session.access_key,'SignatureVersion':'2','SignatureMethod':'HmacSHA256','Version':version}
        post_data = '/'
        url_string = api.calc_signature(url_params,post_data)
        api.url_string  = str(command) + url_string
        api.RequestData = requestData
        responseDoM = api.MakeCall(requestData)
        print"responseDom",responseDoM.toprettyxml()
        getsubmitfeed = {}
        getsubmitfeed = self.submitresult(responseDoM.getElementsByTagName('GetReportRequestListResult'))
        print"getsubmitfee",getsubmitfeed
        return getsubmitfeed

class GetReportList:
    Session = Session()
    def __init__(self, access_key, secret_key, merchant_id, marketplace_id, site):
        self.Session.Initialize(access_key, secret_key, merchant_id, marketplace_id, site)

    def getErrors(self, node):
        info = {}
        for node in node:
            for cNode in node.childNodes:
                if cNode.nodeName == 'Message':
                     info['Error'] = cNode.childNodes[0].data

        return info

    def submitresult(self, nodelist):
        info = {}
        returninfo = []
        for node in nodelist:
            for cNode in node.childNodes:
                if cNode.nodeName == 'ReportInfo':
                    for ccNode in cNode.childNodes:
                        if ccNode.nodeName == 'ReportId':
                            returninfo.append(ccNode.childNodes[0].data)
        return returninfo

    def Get(self,requestData,report_type,request_id,date_from,date_to):
        requestData = requestData.strip()
        print"requestdata",requestData
        api = Call()
        api.Session = self.Session
        version = '2009-01-01'
        method = requestData
        command = '/?'
        url_params = {'Action':method,'Merchant':self.Session.merchant_id,'AWSAccessKeyId':self.Session.access_key,'SignatureVersion':'2','SignatureMethod':'HmacSHA256','Version':version}
        if report_type:
            url_params['ReportTypeList.Type.1'] = report_type
        if request_id:
            url_params['ReportRequestIdList.Id.1'] = request_id
        if date_from:
            url_params['AvailableFromDate'] = date_from
        if date_to:
            url_params['AvailableToDate'] = date_to


        post_data = '/'
        url_string = api.calc_signature(url_params,post_data)
        api.url_string  = str(command) + url_string
        api.RequestData = requestData
        responseDOM = api.MakeCall(requestData)
        print "=======responseDOM=======>",(responseDOM.toprettyxml()).encode('utf-8')
        getErrordetails = self.getErrors(responseDOM.getElementsByTagName('Error'))
        print 'getErrordetails',getErrordetails

        if getErrordetails.get('Error',False):
            count = 1
            while ( getErrordetails.get('Error').lower().find('request signature we calculated') != -1 or getErrordetails.get('Error').lower().find('throttled') != -1 or getErrordetails.get('Error').lower().find('internal service') != -1):
                count = count + 1
                time.sleep(25)
                del url_params['Signature']
                url_string = api.calc_signature(url_params,post_data)
                api.url_string  = str(command) + url_string
                responseDOM = api.MakeCall(requestData)
                getErrordetails = self.getErrors(responseDOM.getElementsByTagName('Error'))
                print 'getErrordetails',getErrordetails
                if count >= 5 or len(getErrordetails) == 0:
                    break

        #Raise Error even after calling it five times, because it can be some other issue other than signature mismatch or throttled
        if getErrordetails.get('Error',False):
            raise osv.except_osv(_('Error!'), _((getErrordetails.get('Error',False))))

        getsubmitfeed = {}
        getsubmitfeed = self.submitresult(responseDOM.getElementsByTagName('GetReportListResult'))
        print"getsubmitfee",getsubmitfeed
        if responseDOM.getElementsByTagName('NextToken') and len(responseDOM.getElementsByTagName('NextToken') and responseDOM.getElementsByTagName('NextToken')[0].childNodes ):
            getsubmitfeed.append({'NextToken':responseDOM.getElementsByTagName('NextToken')[0].childNodes[0].data})
        return getsubmitfeed


class GetReportListByNextToken:
    Session = Session()
    def __init__(self, access_key, secret_key, merchant_id, marketplace_id):
        self.Session.Initialize(access_key, secret_key, merchant_id, marketplace_id)

    def submitresult(self, nodelist):
        info = {}
        returninfo = []
        for node in nodelist:
            for cNode in node.childNodes:
                if cNode.nodeName == 'ReportInfo':
                    for ccNode in cNode.childNodes:
                        if ccNode.nodeName == 'ReportId':
                            returninfo.append(ccNode.childNodes[0].data)
        return returninfo

    def Get(self,requestData,nexttoken):
        requestData = requestData.strip()
        print"requestdata",requestData
        api = Call()
        api.Session = self.Session
        version = '2009-01-01'
        method = requestData
        command = '/?'
        url_params = {'Action':method,'Merchant':self.Session.merchant_id,'NextToken':nexttoken,'AWSAccessKeyId':self.Session.access_key,'SignatureVersion':'2','SignatureMethod':'HmacSHA256','Version':version}
        url_params['Timestamp'] = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime())+ 'Z'
        post_data = '/'
        url_params['Signature'] = api.calc_signature(url_params,post_data)[0]
        url_string = api.calc_signature(url_params,post_data)[1].replace('%0A','')
        api.url_string  = str(command) + url_string
        api.RequestData = requestData
        responseDoM = api.MakeCall(requestData)
#        print"responseDom--->",responseDoM.toprettyxml()
        getsubmitfeed = self.submitresult(responseDoM.getElementsByTagName('GetReportListByNextTokenResult'))
        print"getsubmitfee",getsubmitfeed
        if responseDoM.getElementsByTagName('NextToken') and len(responseDoM.getElementsByTagName('NextToken') and responseDoM.getElementsByTagName('NextToken')[0].childNodes ):
            getsubmitfeed.append({'NextToken':responseDoM.getElementsByTagName('NextToken')[0].childNodes[0].data})
        return getsubmitfeed


class GetReport:
    Session = Session()
    def __init__(self, access_key, secret_key, merchant_id, marketplace_id, site):
        self.Session.Initialize(access_key, secret_key, merchant_id, marketplace_id, site)

    def getErrors(self, node):
        info = {}
        for node in node:
            for cNode in node.childNodes:
                if cNode.nodeName == 'Message':
                     info['Error'] = cNode.childNodes[0].data
        return info

    def Get(self,requestData,report_id):
        requestData = requestData.strip()
        print"requestdata",requestData
        api = Call()
        api.Session = self.Session
        version = '2009-01-01'
        method = requestData
        command = '/?'
        url_params = {'Action':method,'Merchant':self.Session.merchant_id,'ReportId':report_id,'AWSAccessKeyId':self.Session.access_key,'SignatureVersion':'2','SignatureMethod':'HmacSHA256','Version':version}
        post_data = '/'
        url_string = api.calc_signature(url_params,post_data)
        api.url_string  = str(command) + url_string
        api.RequestData = requestData
        data = api.MakeCall(requestData)
        '''responseDOM = parseString(data)

        getErrordetails = self.getErrors(responseDOM.getElementsByTagName('Error'))
        print 'getErrordetails',getErrordetails

        if getErrordetails.get('Error',False):
            count = 1
            while ( getErrordetails.get('Error').lower().find('request signature we calculated') != -1 or getErrordetails.get('Error').lower().find('throttled') != -1 ):
                count = count + 1
                time.sleep(25)
                del url_params['Signature']
                url_params['Timestamp'] = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime())+ 'Z'
                url_params['Signature'] = api.calc_signature(url_params,api.post_data)[0]
                url_string = api.calc_signature(url_params,api.post_data)[1].replace('%0A','')
                api.url_string  = str(command) + url_string
                responseDOM = api.MakeCall(requestData)
                getErrordetails = self.getErrors(responseDOM.getElementsByTagName('Error'))
                print 'getErrordetails',getErrordetails
                if count >= 5 or len(getErrordetails) == 0:
                    break

        #Raise Error even after calling it five times, because it can be some other issue other than signature mismatch or throttled
        if getErrordetails.get('Error',False):
            raise osv.except_osv(_('Error!'), _((getErrordetails.get('Error',False'))))'''

        return data

class GetLowestOfferListingsForASIN:
    Session = Session()
    def __init__(self, access_key, secret_key, merchant_id, marketplace_id):
        self.Session.Initialize(access_key, secret_key, merchant_id, marketplace_id)

    def getErrors(self, node):
        info = {}
        for node in node:
            for cNode in node.childNodes:
                if cNode.nodeName == 'Message':
                     info['Error'] = cNode.childNodes[0].data
        return info
    
    def Get(self,asin_list):
        api = Call()
        api.Session = self.Session
        buy_box=False
        command = '/Products/2011-10-01?'
        version = '2011-10-01'
        method = 'GetLowestOfferListingsForASIN'
        url_params ={'Action':method,'SellerId':self.Session.merchant_id,'MarketplaceId':self.Session.marketplace_id,'AWSAccessKeyId':self.Session.access_key,'SignatureVersion':'2','SignatureMethod':'HmacSHA256','Version':version}
#        print'fbfb', asin_list
        if len(asin_list):
            count = 1
            for asin in asin_list:
                if asin:
                    asin_key = 'ASINList.ASIN.'+ str(count)
                    print 'm====='
                    count += 1
                    url_params[asin_key] = asin
                    if count ==21:
                        break
                        
#        print'asin_key',asin_key
        post_data = '/Products/2011-10-01'
        url_string = api.calc_signature(url_params,post_data)
        api.url_string  = str(command) + url_string
        api.RequestData = ''
        responseDOM = api.MakeCall(method)
        getErrordetails = self.getErrors(responseDOM.getElementsByTagName('Error'))
        print 'getErrordetails',getErrordetails

        if getErrordetails.get('Error',False):
            count = 1
            while ( getErrordetails.get('Error').lower().find('request signature we calculated') != -1 or getErrordetails.get('Error').lower().find('throttled') != -1 or getErrordetails.get('Error').lower().find('internal service') != -1):
                count = count + 1
                time.sleep(25)
                del url_params['Signature']
                url_string = api.calc_signature(url_params,post_data)
                api.url_string  = str(command) + url_string
                responseDOM = api.MakeCall(method)
                getErrordetails = self.getErrors(responseDOM.getElementsByTagName('Error'))
                print 'getErrordetails',getErrordetails
                if count >= 5 or len(getErrordetails) == 0:
                    break

        #Raise Error even after calling it five times, because it can be some other issue other than signature mismatch or throttled
        if getErrordetails.get('Error',False):
            raise osv.except_osv(_('Error!'), _((getErrordetails.get('Error',False))))

        node_list=responseDOM.getElementsByTagName('GetLowestOfferListingsForASINResult')
        print'node_list-------GetLowestOfferListingsForASINResult------',node_list
        all_data_list = []
        asin_dict = {}
        ASIN = False
        for cNode in node_list:
            for cNode1 in cNode.childNodes:
                    data_list=[]
                    if cNode1.nodeName == 'Product':
                        for cNode3 in cNode1.childNodes:
                            if cNode3.nodeName == 'Identifiers':
                                for cNode4 in cNode3.childNodes:
                                        if cNode4.nodeName == 'MarketplaceASIN':
                                            for cNode5 in cNode4.childNodes:
                                                if cNode5.nodeName == 'ASIN':
                                                    ASIN = cNode5.childNodes[0].data
                                                    
                        for cNode11 in cNode1.childNodes:
                            asin_dict[ASIN] = []
                            if cNode11.nodeName == 'LowestOfferListings':
                                for cNode2 in cNode11.childNodes:
                                    LowestOfferListings_dic = {}
                                    if cNode2.nodeName == 'LowestOfferListing':
                                        for cNode21 in cNode2.childNodes:
                                            if cNode21.nodeName == 'Qualifiers':
                                                for cNode12 in cNode21.childNodes:
                                                    if cNode12.nodeName in ['FulfillmentChannel','SellerPositiveFeedbackRating','ItemSubcondition','ItemCondition','ShipsDomestically']:
                                                        LowestOfferListings_dic[cNode12.nodeName] = cNode12.childNodes[0].data
                                                    if cNode12.nodeName == 'SellerPositiveFeedbackRating':
                                                        LowestOfferListings_dic[cNode12.nodeName] = cNode12.childNodes[0].data
                                                    if cNode12.nodeName == 'ShippingTime':
                                                        for cNode13 in cNode12.childNodes:
                                                            if cNode13.nodeName == 'Max':
                                                                LowestOfferListings_dic['ShippingTime'] = cNode13.childNodes[0].data
                                            if cNode21.nodeName == 'NumberOfOfferListingsConsidered':
                                                LowestOfferListings_dic[cNode21.nodeName] = cNode21.childNodes[0].data
                                            if cNode21.nodeName == 'SellerFeedbackCount':
                                                LowestOfferListings_dic[cNode21.nodeName] = cNode21.childNodes[0].data
                                            if cNode21.nodeName == 'Price':
                                                for cNode4 in cNode21.childNodes:
                                                    if cNode4.nodeName == 'LandedPrice':
                                                        for cNode5 in cNode4.childNodes:
                                                            if cNode5.nodeName == 'Amount':
                                                                LowestOfferListings_dic[cNode5.nodeName] = cNode5.childNodes[0].data
                                                    if cNode4.nodeName == 'Shipping':
                                                        for cNode6 in cNode4.childNodes:
                                                            if cNode6.nodeName == 'Amount':
                                                                LowestOfferListings_dic['Shipping'] = cNode6.childNodes[0].data
                                        
                                        asin_dict[ASIN].append(LowestOfferListings_dic)
                                                
#                        all_data_list.append(data_list)
                        
        print'all_data_list',asin_dict
        return asin_dict
    
class POST_PRODUCT_IMAGE_DATA:
    Session = Session()
    def __init__(self, access_key, secret_key, merchant_id, marketplace_id, site_id):
        self.Session.Initialize(access_key, secret_key, merchant_id, marketplace_id, site_id)

    def submitresult(self, nodelist):
        info = {}
        for node in nodelist:
            for cNode in node.childNodes:
                if cNode.nodeName == 'FeedSubmissionInfo':
                    if cNode.childNodes[0].childNodes:
                        for gcNode in cNode.childNodes:
                            if gcNode.nodeName == 'FeedSubmissionId':
                                info[gcNode.nodeName] = gcNode.childNodes[0].data
        return info
    def Get(self,requestData):
        requestData = requestData.strip()
        print"requestdata",requestData
        api = Call()
        api.Session = self.Session
        version = '2009-01-01'
        method = 'SubmitFeed'
        command = '/?'
        url_params = {'Action':method,'Merchant':self.Session.merchant_id,'FeedType':'_POST_PRODUCT_IMAGE_DATA_','AWSAccessKeyId':self.Session.access_key,'SignatureVersion':'2','SignatureMethod':'HmacSHA256','Version':version}
        url_params['Timestamp'] = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime())+ 'Z'
        url_params['PurgeAndReplace'] = 'false'
        post_data = '/'
        api.RequestData = requestData
        url_string = api.calc_signature(url_params,post_data)
        api.url_string  = str(command) + url_string
        responseDOM = api.MakeCall('POST_PRODUCT_IMAGE_DATA')
        responseDOM = api.MakeCallRepeat(responseDOM,url_params,post_data,command,method)
        print"responseDom",responseDOM.toprettyxml()
        getsubmitfeed = {}
        getsubmitfeed = self.submitresult(responseDOM.getElementsByTagName('SubmitFeedResult'))
        print"getsubmitfee",getsubmitfeed
        return getsubmitfeed


class GetFeedSubmissionResult:
    
    Session = Session()

    def __init__(self, access_key, secret_key, merchant_id, marketplace_id, site_id):
        self.Session.Initialize(access_key, secret_key, merchant_id, marketplace_id, site_id)

    def submitfeedresult(self, nodelist):
        for node in nodelist:
            info = {}
            for cNode in node.childNodes:
                if cNode.nodeName == 'ProcessingReport':
                        if cNode.childNodes:
                            for gcNode in cNode.childNodes:
#                                if gcNode.nodeName == 'Summary':
#                                    for gcNode in gcNode.childNodes:
                                        if gcNode.nodeName == 'ProcessingSummary':
                                            for gccNode in gcNode.childNodes:
                                                if gccNode.nodeName == 'MessagesWithError':
                                                    info[gccNode.nodeName] = gccNode.childNodes[0].data
                                                elif gccNode.nodeName == 'MessagesWithWarning':
                                                    info[gccNode.nodeName] = gccNode.childNodes[0].data
#                                elif gcNode.nodeName == 'Result':
#                                        for gccNode in gcNode.childNodes:
#                                            if gccNode.nodeName == 'ResultDescription':
#                                                info[gccNode.nodeName] = gccNode.childNodes[0].data
        return info
    def Get(self,FeedSubmissionId):
        api = Call()
        api.Session = self.Session
        version = '2009-01-01'
        method= 'GetFeedSubmissionResult'
        command = '/?'
        url_params = {'Action':method,'Merchant':self.Session.merchant_id,'AWSAccessKeyId':self.Session.access_key,'SignatureVersion':'2','SignatureMethod':'HmacSHA256','Version':version}
        url_params['Timestamp'] = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime())+ 'Z'
        url_params['FeedSubmissionId'] = FeedSubmissionId
        post_data = '/'
        api.RequestData = ''
        url_string = api.calc_signature(url_params,post_data)
        api.url_string  = str(command) + url_string
        responseDOM = api.MakeCall('GetFeedSubmissionResult')
        responseDOM = api.MakeCallRepeat(responseDOM,url_params,post_data,command,method)
        print"responseDom",responseDOM.toprettyxml()
        getsubmitfeed = {}
        getsubmitfeedresult = self.submitfeedresult(responseDOM.getElementsByTagName('Message'))
        print"getsubmitfeedresult",getsubmitfeedresult
        return getsubmitfeedresult
    
    def Get_all(self,FeedSubmissionId):
        api = Call()
        api.Session = self.Session
        version = '2009-01-01'
        method= 'GetFeedSubmissionResult'
        command = '/?'
        url_params = {'Action':method,'Merchant':self.Session.merchant_id,'AWSAccessKeyId':self.Session.access_key,'SignatureVersion':'2','SignatureMethod':'HmacSHA256','Version':version}
        url_params['Timestamp'] = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime())+ 'Z'
        url_params['FeedSubmissionId'] = FeedSubmissionId
        post_data = '/'
#        url_params['Signature'] = api.calc_signature(url_params,post_data)[0]
#        url_string = api.calc_signature(url_params,post_data)[1].replace('%0A','')
        url_string = api.calc_signature(url_params,post_data)
        api.url_string  = str(command) + url_string
        api.RequestData =''
        responseDOM = api.MakeCall('GetFeedSubmissionResult')
        responseDOM = api.MakeCallRepeat(responseDOM,url_params,post_data,command,method)
#        print"responseDom",responseDoM.toprettyxml()
        return responseDOM.toprettyxml()  

class GetCompetitivePricingForSKU:
    Session = Session()
    def __init__(self, access_key, secret_key, merchant_id, marketplace_id, site_id):
        self.Session.Initialize(access_key, secret_key, merchant_id, marketplace_id, site_id)
        
    def getErrors(self, node):
        info = {}
        for node in node:
            for cNode in node.childNodes:
                if cNode.nodeName == 'Message':
                    info['Error'] = cNode.childNodes[0].data
        return info
    
    def Get(self,sku_list):
        count = 1
        api = Call()
        api.Session = self.Session
        command = '/Products/2011-10-01?'
        version = '2011-10-01'
        method = 'GetCompetitivePricingForSKU'
        url_params ={'Action':method,'SellerId':self.Session.merchant_id,'MarketplaceId':self.Session.marketplace_id,'AWSAccessKeyId':self.Session.access_key,'SignatureVersion':'2','SignatureMethod':'HmacSHA256','Version':version}
        if len(sku_list):
            
            for sku in sku_list:
                sku_key = 'SellerSKUList.SellerSKU.'+ str(count)
                print 'm====='
                count += 1
                url_params[sku_key] = sku
                if count ==len(sku_list):
                    break
                if count ==20:
                    break        
        url_params['Timestamp'] = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime())+ '.000Z'
        post_data = '/Products/2011-10-01'
#        url_params['Signature'] = api.calc_signature(url_params,post_data)[0]
#        url_string = api.calc_signature(url_params,post_data)[1].replace('%0A','')
#       
        url_string = api.calc_signature(url_params,post_data)
        print 'url_string',url_string
        api.url_string  = str(command) + url_string.replace('+','%20')

        
        print'api.url_string=========',api.url_string
    
        api.RequestData =''
        responseDOM = api.MakeCall(method)
        responseDOM = api.MakeCallRepeat(responseDOM,url_params,post_data,command,method)

        getErrordetails = self.getErrors(responseDOM.getElementsByTagName('Error'))
        print 'getErrordetails',getErrordetails

        if getErrordetails.get('Error',False):
            count = 1
            while ( getErrordetails.get('Error').lower().find('request signature we calculated') != -1 or getErrordetails.get('Error').lower().find('throttled') != -1 ):
                count = count + 1
                time.sleep(25)
                del url_params['Signature']
                url_string = api.calc_signature(url_params,post_data)
                api.url_string  = str(command) + url_string
                responseDOM = api.MakeCall('GetCompetitivePricingForSKU')
                getErrordetails = self.getErrors(responseDOM.getElementsByTagName('Error'))
                print 'getErrordetails',getErrordetails
                if count >= 5 or len(getErrordetails) == 0:
                    break
        info = {}
        data_list=[]
        node_list=responseDOM.getElementsByTagName('GetCompetitivePricingForSKUResult')
        for cNode in node_list:
            print'1111'
            print'cnode.nodeame',cNode.nodeName
            print '=================',cNode.getAttribute('SellerSKU')
            info['SellerSKU']=cNode.getAttribute('SellerSKU')
            for cNode1 in cNode.childNodes:
                    print'22222'
                    if cNode1.nodeName == 'Product':
                        print'3333'
                        for cNode3 in cNode1.childNodes:
                            if cNode3.nodeName == 'Identifiers':
                                print'3333'
                                for cNode4 in cNode3.childNodes:
                                    if cNode4.nodeName == 'MarketplaceASIN':
                                            for cNode5 in cNode4.childNodes:
                                                if cNode5.nodeName == 'ASIN':
                                                    info['ASIN'] = cNode5.childNodes[0].data
                                                    print'cNode5.childNodes[0].data=========>',cNode5.childNodes[0].data
                        for cNode11 in cNode1.childNodes:
                          if cNode11.nodeName == 'CompetitivePricing':
                            
                            print'nnnnnnnnnn'
                            for cNode2 in cNode11.childNodes:
                                print 'cNode2.nodeName',cNode2.nodeName
                                if cNode2.nodeName == 'CompetitivePrices':
                                    for cNode21 in cNode2.childNodes:
                                        print 'ccNode21',cNode21.nodeName
                                        if cNode21.nodeName == 'CompetitivePrice':
                                            if cNode21.getAttribute('belongsToRequester')=='true':
                                                buy_box=True
                                                info['buy_box']=buy_box
                                            for cNode3 in cNode21.childNodes:
                                                print 'ccNode21===',cNode3.nodeName
                                                if cNode3.nodeName == 'Price':
                                                    for cNode4 in cNode3.childNodes:
                                                        if cNode4.nodeName == 'LandedPrice':
                                                            for cNode5 in cNode4.childNodes:
                                                                if cNode5.nodeName == 'Amount':
                                                                    info[cNode5.nodeName] = cNode5.childNodes[0].data                
                                                
  
            if info!={}:
                data_list.append(info)
                info={}
        print'data_list',data_list
        return data_list
        

    def call(amazon_instance, method, *arguments):
        result=False
        if method == 'GetCompetitivePricingForSKU':
            lmp = GetCompetitivePricingForSKU(amazon_instance.aws_access_key, amazon_instance.secret_key, amazon_instance.merchant_id, amazon_instance.market_place_id)
            result = lmp.Get(arguments[0])
        return result

class PutTransportContent:
    Session = Session()
    def __init__(self, access_key, secret_key, merchant_id, marketplace_id, site):
        self.Session.Initialize(access_key, secret_key, merchant_id, marketplace_id, site)

    def submitresult(self, nodelist):
        info = 'Failed'
        print 'nodelist',nodelist
        for eachNode in nodelist:
            info = eachNode.childNodes[0].data

        return info

    def Get(self,requestData):
        api = Call()
        api.Session = self.Session
        version = '2010-10-01'
        method = 'PutTransportContent'
        command = '/FulfillmentInboundShipment/2010-10-01?'
        url_params = {'Action':method,'SellerId':self.Session.merchant_id,'AWSAccessKeyId':self.Session.access_key,'SignatureVersion':'2','SignatureMethod':'HmacSHA256','Version':version}
        url_params.update(requestData)
        post_data = '/FulfillmentInboundShipment/2010-10-01'
        url_string = api.calc_signature(url_params,post_data)
        print'url_string---calc_signature---',url_string
        api.url_string  = str(command) + url_string
        api.RequestData = ''
        responseDOM = api.MakeCall(method)
        responseDOM = api.MakeCallRepeat(responseDOM,url_params,post_data,command,method)
        print'responseDOM',responseDOM.toprettyxml()
        #After successful result
        result = self.submitresult(responseDOM.getElementsByTagName('TransportStatus'))
        print"result",result
        return result

class EstimateTransportRequest:
    Session = Session()
    def __init__(self, access_key, secret_key, merchant_id, marketplace_id, site):
        self.Session.Initialize(access_key, secret_key, merchant_id, marketplace_id, site)

    def submitresult(self, nodelist):
        info = 'Failed'
        print 'nodelist',nodelist
        for eachNode in nodelist:
            info = eachNode.childNodes[0].data

        return info

    def Get(self,requestData):
        api = Call()
        api.Session = self.Session
        version = '2010-10-01'
        method = 'EstimateTransportRequest'
        command = '/FulfillmentInboundShipment/2010-10-01?'
        url_params = {'Action':method,'SellerId':self.Session.merchant_id,'AWSAccessKeyId':self.Session.access_key,'SignatureVersion':'2','SignatureMethod':'HmacSHA256','Version':version}
        url_params.update(requestData)
        post_data = '/FulfillmentInboundShipment/2010-10-01'
        url_string = api.calc_signature(url_params,post_data)
        print'url_string---calc_signature---',url_string
        api.url_string  = str(command) + url_string
        api.RequestData = ''
        responseDOM = api.MakeCall(method)
        responseDOM = api.MakeCallRepeat(responseDOM,url_params,post_data,command,method)
#        print'responseDOM',responseDOM.toprettyxml()
        #After successful result
        result = self.submitresult(responseDOM.getElementsByTagName('TransportStatus'))
#        print"result",re
        return result

class GetTransportContent:
    Session = Session()
    def __init__(self, access_key, secret_key, merchant_id, marketplace_id, site):
        self.Session.Initialize(access_key, secret_key, merchant_id, marketplace_id, site)

    def submitresult(self, nodelist):
        info = 'Failed'
        print 'nodelist',nodelist
        for eachNode in nodelist:
            print 'eachNode',eachNode.nodeName
            for cNode21 in eachNode.childNodes:
                if cNode21.nodeName == 'Value':
                    info = cNode21.childNodes[0].data

        return info

    def Get(self,requestData):
        api = Call()
        api.Session = self.Session
        version = '2010-10-01'
        method = 'GetTransportContent'
        command = '/FulfillmentInboundShipment/2010-10-01?'
        url_params = {'Action':method,'SellerId':self.Session.merchant_id,'AWSAccessKeyId':self.Session.access_key,'SignatureVersion':'2','SignatureMethod':'HmacSHA256','Version':version}
        url_params.update(requestData)
        post_data = '/FulfillmentInboundShipment/2010-10-01'
        url_string = api.calc_signature(url_params,post_data)
        print'url_string---calc_signature---',url_string
        api.url_string  = str(command) + url_string
        api.RequestData = ''
        responseDOM = api.MakeCall(method)
        responseDOM = api.MakeCallRepeat(responseDOM,url_params,post_data,command,method)
        print'responseDOM',responseDOM.toprettyxml()
        #After successful result
        result = self.submitresult(responseDOM.getElementsByTagName('Amount'))
        print"result",result
        return result

class GetPackageLabels:
    Session = Session()
    def __init__(self, access_key, secret_key, merchant_id, marketplace_id, site):
        self.Session.Initialize(access_key, secret_key, merchant_id, marketplace_id, site)

    def submitresult(self, nodelist):
        info = {}
        for node in nodelist:
            for cNode in node.childNodes:
                if cNode.nodeName == 'PdfDocument':
                   info[cNode.nodeName] = cNode.childNodes[0].data
        return info

    def Get(self,requestData):
        api = Call()
        api.Session = self.Session
        version = '2010-10-01'
        method = 'GetPackageLabels'
        command = '/FulfillmentInboundShipment/2010-10-01?'
        url_params = {'Action':method,'SellerId':self.Session.merchant_id,'AWSAccessKeyId':self.Session.access_key,'SignatureVersion':'2','SignatureMethod':'HmacSHA256','Version':version}
        url_params.update(requestData)
        post_data = '/FulfillmentInboundShipment/2010-10-01'
        url_string = api.calc_signature(url_params,post_data)
        api.url_string  = str(command) + url_string
        api.RequestData = ''
        responseDOM = api.MakeCall(method)
        responseDOM = api.MakeCallRepeat(responseDOM,url_params,post_data,command,method)

        #After successful result
        results = self.submitresult(responseDOM.getElementsByTagName('TransportDocument'))
        return results

class ConfirmTransportRequest:
    Session = Session()
    def __init__(self, access_key, secret_key, merchant_id, marketplace_id, site):
        self.Session.Initialize(access_key, secret_key, merchant_id, marketplace_id, site)

    def submitresult(self, nodelist):
        info = 'Failed'
        print 'nodelist',nodelist
        for eachNode in nodelist:
            info = eachNode.childNodes[0].data

        return info

    def Get(self,requestData):
        api = Call()
        api.Session = self.Session
        version = '2010-10-01'
        method = 'ConfirmTransportRequest'
        command = '/FulfillmentInboundShipment/2010-10-01?'
        url_params = {'Action':method,'SellerId':self.Session.merchant_id,'AWSAccessKeyId':self.Session.access_key,'SignatureVersion':'2','SignatureMethod':'HmacSHA256','Version':version}
        url_params.update(requestData)
        post_data = '/FulfillmentInboundShipment/2010-10-01'
        url_string = api.calc_signature(url_params,post_data)
        print'url_string---calc_signature---',url_string
        api.url_string  = str(command) + url_string
        api.RequestData = ''
        responseDOM = api.MakeCall(method)
        responseDOM = api.MakeCallRepeat(responseDOM,url_params,post_data,command,method)
        print'responseDOM',responseDOM.toprettyxml()
        #After successful result
        result = self.submitresult(responseDOM.getElementsByTagName('TransportStatus'))
        print"result",result
        return result

class ListInboundShipmentItems:
    Session = Session()
    def __init__(self, access_key, secret_key, merchant_id, marketplace_id, site):
        self.Session.Initialize(access_key, secret_key, merchant_id, marketplace_id, site)

    def submitresult(self, nodelist):
        info_list =  []
        print 'nodelist',nodelist
        for eachNode in nodelist:
            print 'eachNode',eachNode.nodeName
            info = {}
            for cNode21 in eachNode.childNodes:
                if cNode21.nodeName in  ['SellerSKU','QuantityShipped','QuantityInCase','QuantityReceived','FulfillmentNetworkSKU']:
                    info[cNode21.nodeName] = cNode21.childNodes[0].data
            info_list.append(info)

        return info_list

    def Get(self,requestData):
        api = Call()
        api.Session = self.Session
        version = '2010-10-01'
        method = 'ListInboundShipmentItems'
        command = '/FulfillmentInboundShipment/2010-10-01?'
        url_params = {'Action':method,'SellerId':self.Session.merchant_id,'AWSAccessKeyId':self.Session.access_key,'SignatureVersion':'2','SignatureMethod':'HmacSHA256','Version':version}
        url_params.update(requestData)
        post_data = '/FulfillmentInboundShipment/2010-10-01'
        url_string = api.calc_signature(url_params,post_data)
        print'url_string---calc_signature---',url_string
        api.url_string  = str(command) + url_string
        api.RequestData = ''
        responseDOM = api.MakeCall(method)
        responseDOM = api.MakeCallRepeat(responseDOM,url_params,post_data,command,method)
        print'responseDOM',responseDOM.toprettyxml()
        #After successful result
        result = self.submitresult(responseDOM.getElementsByTagName('member'))
        print"result",result
        return result

class ListInventorySupply:
    Session = Session()
    def __init__(self, access_key, secret_key, merchant_id, marketplace_id, site):
        self.Session.Initialize(access_key, secret_key, merchant_id, marketplace_id, site)

    def getResult(self, nodelist):
        info = {}
        total_info = []
        for node in nodelist:
            for cNode in node.childNodes:
                if cNode.nodeName == 'member':
                    for ccNode in cNode.childNodes:
                        if ccNode.nodeName == 'InStockSupplyQuantity':
                            info[ccNode.nodeName] = ccNode.childNodes[0].data
                        elif ccNode.nodeName == 'SellerSKU':
                            info[ccNode.nodeName] = ccNode.childNodes[0].data
                        elif ccNode.nodeName == 'FNSKU':
                            info[ccNode.nodeName] = ccNode.childNodes[0].data
                    total_info.append(info)
                    info = {}

        print 'total_info',total_info
        return total_info

    def Get(self,method,skus):
        api = Call()
        api.Session = self.Session
        version = '2010-10-01'
        command = '/FulfillmentInventory/2010-10-01?'
        url_params = {'Action':method,'SellerId':self.Session.merchant_id,'AWSAccessKeyId':self.Session.access_key,'SignatureVersion':'2','SignatureMethod':'HmacSHA256','Version':version}
        url_params['Timestamp'] = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime())+ 'Z'
        if len(skus):
            count = 1
            for sku in skus:
                if sku:
                    sku_key = 'SellerSkus.member.'+ str(count)
                    print 'm====='
                    count += 1
                    url_params[sku_key] = sku
                    if count ==21:
                        break

        post_data = '/FulfillmentInventory/2010-10-01'
        url_string = api.calc_signature(url_params,post_data)
        api.url_string  = str(command) + url_string
        responseDOM = api.MakeCall(method)
        responseDOM = api.MakeCallRepeat(responseDOM,url_params,post_data,command,method)
        '''responseDOM = parseString(data)
        tag = responseDOM.getElementsByTagName('Error')
        if (tag.count!=0):
            for error in tag:
                print "\n",error.toprettyxml("  ")

        getsubmitfeed = {}'''
        getsubmitfeed = self.getResult(responseDOM.getElementsByTagName('InventorySupplyList'))

        return getsubmitfeed



class amazonerp_osv(osv.osv):
    _name = 'amazonerp.osv'
    
    def call(self, amazon_instance, method, *arguments):
        print"=iiiiiii"
        print "--------------method",method
        if method == 'ListOrders':
            print "hhhhhhhhhhhhhhhh"
            print "****************Orders",amazon_instance.aws_access_key_id, amazon_instance.aws_secret_access_key, amazon_instance.aws_merchant_id, amazon_instance.aws_market_place_id, amazon_instance.site
            lo = ListOrders(amazon_instance.aws_access_key_id, amazon_instance.aws_secret_access_key, amazon_instance.aws_merchant_id, amazon_instance.aws_market_place_id, amazon_instance.site)
            result = lo.Get(arguments[0],arguments[1],arguments[2])
            return result
        if method == 'GetOrder':
            go = GetOrderBYID(amazon_instance.aws_access_key_id, amazon_instance.aws_secret_access_key, amazon_instance.aws_merchant_id, amazon_instance.aws_market_place_id, amazon_instance.site)
            result = go.Get(arguments[0])
            return result
        elif method == 'ListOrderItems':
            lo = ListOrderItems(amazon_instance.aws_access_key_id, amazon_instance.aws_secret_access_key, amazon_instance.aws_merchant_id, amazon_instance.aws_market_place_id, amazon_instance.site)
            result = lo.Get(arguments[0])
            return result
        elif method == 'ListOrdersByNextToken':
            lo = ListOrdersByNextToken(amazon_instance.aws_access_key_id, amazon_instance.aws_secret_access_key, amazon_instance.aws_merchant_id, amazon_instance.aws_market_place_id, amazon_instance.site)
            result = lo.Get(arguments[0])
            return result
        elif method == 'ListOrderItemsByNextToken':
            lo = ListOrderItemsByNextToken(amazon_instance.aws_access_key_id, amazon_instance.aws_secret_access_key, amazon_instance.aws_merchant_id, amazon_instance.aws_market_place_id, amazon_instance.site)
            result = lo.Get(arguments[0],arguments[1])
            return result
        elif method == 'POST_INVENTORY_AVAILABILITY_DATA':
            pi = POST_INVENTORY_AVAILABILITY_DATA(amazon_instance.aws_access_key_id, amazon_instance.aws_secret_access_key, amazon_instance.aws_merchant_id, amazon_instance.aws_market_place_id, amazon_instance.site)
            result = pi.Get(arguments[0])
            return result
        elif method == 'POST_ORDER_FULFILLMENT_DATA':
            po = POST_ORDER_FULFILLMENT_DATA(amazon_instance.aws_access_key_id, amazon_instance.aws_secret_access_key, amazon_instance.aws_merchant_id, amazon_instance.aws_market_place_id, amazon_instance.site)
            result = po.Get(arguments[0])
            return result
        elif method == 'POST_PRODUCT_PRICING_DATA':
            print "0000000000000000000000000000000000000000000000"
            po = POST_PRODUCT_PRICING_DATA(amazon_instance.aws_access_key_id, amazon_instance.aws_secret_access_key, amazon_instance.aws_merchant_id, amazon_instance.aws_market_place_id, amazon_instance.site)
            result = po.Get(arguments[0])
            return result
        elif method == 'POST_PRODUCT_DATA':
            pp = POST_PRODUCT_DATA(amazon_instance.aws_access_key_id, amazon_instance.aws_secret_access_key, amazon_instance.aws_merchant_id, amazon_instance.aws_market_place_id, amazon_instance.site)
            result = pp.Get(arguments[0])
            return result
        elif method == 'POST_PRODUCT_IMAGE_DATA':
            pi = POST_PRODUCT_IMAGE_DATA(amazon_instance.aws_access_key_id, amazon_instance.aws_secret_access_key, amazon_instance.aws_merchant_id, amazon_instance.aws_market_place_id, amazon_instance.site)
            result = pi.Get(arguments[0])
            return result
        elif method == 'GetFeedSubmissionResult':
            gfs = GetFeedSubmissionResult(amazon_instance.aws_access_key_id, amazon_instance.aws_secret_access_key, amazon_instance.aws_merchant_id, amazon_instance.aws_market_place_id, amazon_instance.site)
            result = gfs.Get(arguments[0])
            return result
        elif method == 'ListMatchingProducts':
            lmp = ListMatchingProducts(amazon_instance.aws_access_key_id, amazon_instance.aws_secret_access_key, amazon_instance.aws_merchant_id, amazon_instance.aws_market_place_id, amazon_instance.site)
            result = lmp.Get(arguments[0],arguments[1])
            return result
        elif method == 'GetMatchingProduct':
            lmp = GetMatchingProduct(amazon_instance.aws_access_key, amazon_instance.secret_key, amazon_instance.merchant_id, amazon_instance.market_place_id, amazon_instance.site)
            result = lmp.Get(arguments[0])
            return result
        elif method == 'RequestReport':
            print "innnnnnnnnnnnnnnnnnnn"
            lmp = RequestReport(amazon_instance.aws_access_key_id, amazon_instance.aws_secret_access_key, amazon_instance.aws_merchant_id, amazon_instance.aws_market_place_id, amazon_instance.site)
            result = lmp.Get(method,arguments[0],arguments[1])
            return result
        elif method == 'GetReportList':
            print "innnnnnnnn"
            lmp = GetReportList(amazon_instance.aws_access_key_id, amazon_instance.aws_secret_access_key, amazon_instance.aws_merchant_id, amazon_instance.aws_market_place_id, amazon_instance.site)
            result = lmp.Get(method,arguments[0],arguments[1],arguments[2],arguments[3])
            return result
        elif method == 'GetReportListByNextToken':
            lmp = GetReportListByNextToken(amazon_instance.aws_access_key_id, amazon_instance.aws_secret_access_key, amazon_instance.aws_merchant_id, amazon_instance.aws_market_place_id, amazon_instance.site)
            result = lmp.Get(method,arguments[0])
            return result
        elif method == 'GetReport':
            lmp = GetReport(amazon_instance.aws_access_key_id, amazon_instance.aws_secret_access_key, amazon_instance.aws_merchant_id, amazon_instance.aws_market_place_id, amazon_instance.site)
            result = lmp.Get(method,arguments[0])
            return result
        elif method == 'GetReportRequestList':
            lmp = GetReportRequestList(amazon_instance.aws_access_key_id, amazon_instance.aws_secret_access_key, amazon_instance.aws_merchant_id, amazon_instance.aws_market_place_id, amazon_instance.site)
            result = lmp.Get(method,arguments[0])
            return result
        elif method == 'ListInventorySupply':
            print "ikkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk"
            lmp = ListInventorySupply(amazon_instance.aws_access_key_id, amazon_instance.aws_secret_access_key, amazon_instance.aws_merchant_id, amazon_instance.aws_market_place_id, amazon_instance.site)
            result = lmp.Get(method,arguments[0])
            return result
        elif method == 'GetCompetitivePricingForASIN':
            lmp = GetCompetitivePricingForASIN(amazon_instance.aws_access_key_id, amazon_instance.aws_secret_access_key, amazon_instance.aws_merchant_id, amazon_instance.aws_market_place_id, amazon_instance.site)
            result = lmp.Get(arguments[0])
            return result
        elif method == 'GetMyPriceForSKU':
            lmp = GetMyPriceForSKU(amazon_instance.aws_access_key_id, amazon_instance.aws_secret_access_key, amazon_instance.aws_merchant_id, amazon_instance.aws_market_place_id, amazon_instance.site)
            result = lmp.Get(arguments[0])
            return result
        elif method == 'CreateInboundShipmentPlan':
            print "*************************inbound",amazon_instance.aws_access_key_id, amazon_instance.aws_secret_access_key, amazon_instance.aws_merchant_id, amazon_instance.aws_market_place_id, amazon_instance.site
            lmp = CreateInboundShipmentPlan(amazon_instance.aws_access_key_id, amazon_instance.aws_secret_access_key, amazon_instance.aws_merchant_id, amazon_instance.aws_market_place_id, amazon_instance.site)
            result = lmp.Get(arguments[0])
            return result
        elif method == 'CreateInboundShipment':
            lmp = CreateInboundShipment(amazon_instance.aws_access_key_id, amazon_instance.aws_secret_access_key, amazon_instance.aws_merchant_id, amazon_instance.aws_market_place_id, amazon_instance.site)
            result = lmp.Get(arguments[0])
            return result
        elif method == 'GetPackageLabels':
            lmp = GetPackageLabels(amazon_instance.aws_access_key_id, amazon_instance.aws_secret_access_key, amazon_instance.aws_merchant_id, amazon_instance.aws_market_place_id, amazon_instance.site)
            result = lmp.Get(arguments[0])
            return result
        elif method == 'GetFeedSubmissionResultall':
            gfs = GetFeedSubmissionResult(amazon_instance.aws_access_key_id, amazon_instance.aws_secret_access_key, amazon_instance.aws_merchant_id, amazon_instance.aws_market_place_id, amazon_instance.site)
            result = gfs.Get_all(arguments[0])
            return result
        elif method == 'GetCompetitivePricingForSKU':
            lmp = GetCompetitivePricingForSKU(amazon_instance.aws_access_key_id, amazon_instance.aws_secret_access_key, amazon_instance.aws_merchant_id, amazon_instance.aws_market_place_id, amazon_instance.site)
            print arguments[0]
            result = lmp.Get(arguments[0])
            print'result==============>',result
            return result
        elif method == 'PutTransportContent':
            print "**************************************************"
            lmp = PutTransportContent(amazon_instance.aws_access_key_id, amazon_instance.aws_secret_access_key, amazon_instance.aws_merchant_id, amazon_instance.aws_market_place_id, amazon_instance.site)
            result = lmp.Get(arguments[0])
            return result
        elif method == 'EstimateTransportRequest':
            lmp = EstimateTransportRequest(amazon_instance.aws_access_key_id, amazon_instance.aws_secret_access_key, amazon_instance.aws_merchant_id, amazon_instance.aws_market_place_id, amazon_instance.site)
            result = lmp.Get(arguments[0])
            return result
        elif method == 'GetTransportContent':
            lmp = GetTransportContent(amazon_instance.aws_access_key_id, amazon_instance.aws_secret_access_key, amazon_instance.aws_merchant_id, amazon_instance.aws_market_place_id, amazon_instance.site)
            result = lmp.Get(arguments[0])
            return result
        elif method == 'GetPackageLabels':
            lmp = GetPackageLabels(amazon_instance.aws_access_key_id, amazon_instance.aws_secret_access_key, amazon_instance.aws_merchant_id, amazon_instance.aws_market_place_id, amazon_instance.site)
            result = lmp.Get(arguments[0])
            return result
        elif method == 'ConfirmTransportRequest':
            lmp = ConfirmTransportRequest(amazon_instance.aws_access_key_id, amazon_instance.aws_secret_access_key, amazon_instance.aws_merchant_id, amazon_instance.aws_market_place_id, amazon_instance.site)
            result = lmp.Get(arguments[0])
            return result
        elif method == 'ListInboundShipmentItems':
            lmp = ListInboundShipmentItems(amazon_instance.aws_access_key_id, amazon_instance.aws_secret_access_key, amazon_instance.aws_merchant_id, amazon_instance.aws_market_place_id, amazon_instance.site)
            result = lmp.Get(arguments[0])
            return result
        
amazonerp_osv()
