# -*- coding: UTF-8 -*-

from mws import mws

access_key = 'AKIAJXSITADAGOYTURIA' #replace with your access key
merchant_id = 'A1RFE1PW3AS3N' #replace with your merchant id
secret_key = '/T5dWAufa1zJxq0t0/ZmfkQa6/yHz6HH7NkdkUt9' #replace with your secret key

region = 'US'

def get_report(reportid):
    x = mws.Reports(access_key=access_key, secret_key=secret_key, account_id=merchant_id,region=region)
    report = x.get_report(report_id=reportid)
    response_data = report.original
    print response_data
    
def get_reports():
    x = mws.Reports(access_key=access_key, secret_key=secret_key, account_id=merchant_id,region=region)
    report = x.get_report_list(max_count='10')
    response_data = report.original
    print response_data
    
# get_reports()
get_report('18389096353')

