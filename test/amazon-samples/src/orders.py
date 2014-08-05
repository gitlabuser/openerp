# -*- coding: UTF-8 -*-

from mws import mws

access_key = 'AKIAJXSITADAGOYTURIA' #replace with your access key
merchant_id = 'A1RFE1PW3AS3N' #replace with your merchant id
secret_key = '/T5dWAufa1zJxq0t0/ZmfkQa6/yHz6HH7NkdkUt9' #replace with your secret key
market_place_id = 'ATVPDKIKX0DER'
region = 'US'

# def get_order(reportid):
#     x = mws.Reports(access_key=access_key, secret_key=secret_key, account_id=merchant_id,region=region)
#     report = x.get_report(report_id=reportid)
#     response_data = report.original
#     print response_data
    
def get_orders():
    x = mws.Orders(access_key=access_key, secret_key=secret_key, account_id=merchant_id,region=region)
    orders = x.list_orders(marketplaceids=[market_place_id], created_after='2014-08-04T11:00:00Z', created_before='2014-08-04T13:00:00Z')#, lastupdatedafter, lastupdatedbefore, orderstatus, fulfillment_channels, payment_methods, buyer_email, seller_orderid, max_results)
    response_data = orders.original
    print response_data
    
    od = orders.parsed
    orders = od.Orders.Order
    
    if not isinstance(orders,list) :
        orders=[orders]
        
    for order in orders:
        for key in order:
            print key
            print order[key]
    
get_orders()

