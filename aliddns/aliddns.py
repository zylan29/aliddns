import argparse
from datetime import datetime
import json
import socket
from urllib.request import urlopen

from aliyunsdkcore.client import AcsClient
from aliyunsdkalidns.request.v20150109.DescribeDomainRecordsRequest import DescribeDomainRecordsRequest
from aliyunsdkalidns.request.v20150109.UpdateDomainRecordRequest import UpdateDomainRecordRequest
from aliyunsdkalidns.request.v20150109.AddDomainRecordRequest import AddDomainRecordRequest


ipv4_api = 'api-ipv4.ip.sb'
ipv6_api = 'api-ipv6.ip.sb'
ipv4_api_url = 'https://' + ipv4_api + '/ip'
ipv6_api_url = 'https://' + ipv6_api + '/ip'

default_RRs = ['@', '*']

ipv4_record_type = 'A'
ipv6_record_type = 'AAAA'

accept_format = 'json'

default_timeout = 5


class AliDDNS(object):

    def __init__(self, accesskeyId, accesskeySecret, regionId):
        self.acs_client = AcsClient(accesskeyId, accesskeySecret, regionId)

    def describe(self, domainName: str, recordType: str):
        request = DescribeDomainRecordsRequest()
        
        request.set_DomainName(domainName)
        request.set_Type(recordType)
        request.set_accept_format(accept_format)
        
        return json.loads(self.acs_client.do_action_with_exception(request))
    
    def update(self, RR: str, recordId: str, recordType: str, value):
        request = UpdateDomainRecordRequest()
        
        request.set_RR(RR)
        request.set_RecordId(recordId)
        request.set_Type(recordType)
        request.set_Value(value)
        request.set_accept_format(accept_format)

        return self.acs_client.do_action_with_exception(request)
    
    def add(self, RR: str, domainName: str, recordType: str, value: str): 
        request = AddDomainRecordRequest()
        
        request.set_RR(RR)
        request.set_DomainName(domainName)
        request.set_Type(recordType)
        request.set_Value(value)
        request.set_accept_format(accept_format)

        return self.acs_client.do_action_with_exception(request)
    
    @staticmethod
    def get_publib_ip():
        publicIPv4 = ''
        try:
            publicIPv4 = str(urlopen(ipv4_api_url, timeout=default_timeout).read().strip(), encoding='utf-8')
        except:
            pass
        
        publicIPv6 = ''
        try:
            publicIPv6 = str(urlopen(ipv6_api_url, timeout=default_timeout).read().strip(), encoding='utf-8')
        except:
            pass

        return publicIPv4, publicIPv6
    
    @staticmethod
    def get_local_ip():
        localIPv4 = ''
        try:
            socketIPv4 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            socketIPv4.settimeout(default_timeout)
            socketIPv4.connect((ipv4_api, 443))
            localIPv4 = socketIPv4.getsockname()[0]
        finally:
            socketIPv4.close()
        
        localIPv6 = ''
        try:
            socketIPv6 = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
            socketIPv6.settimeout(default_timeout)
            socketIPv6.connect((ipv6_api, 443))
            localIPv6 = socketIPv6.getsockname()[0]
        finally:
            socketIPv6.close()

        return localIPv4, localIPv6
    
    def _ddns(self, domainName: str, recordType: str, resourceRecords: list, publicIP: str):
        domain = self.describe(domainName, recordType)
        if domain['TotalCount'] == 0:
            for resourceRecord in resourceRecords:
                self.add(resourceRecord, domainName, recordType, publicIP)
                print('{} Add {} record for {}.{}: {}'.format(datetime.now(), recordType, resourceRecord, domainName, publicIP))
        elif domain['TotalCount'] > 0:
            records = domain['DomainRecords']['Record']
            for resourceRecord in resourceRecords:
                found = False
                for record in records:
                    if record['RR'] == resourceRecord and record['Type'] == recordType:
                        found = True
                        recordIPAddr = record['Value'].strip()
                        if recordIPAddr != publicIP:
                            self.update(record['RR'], record['RecordId'], recordType, publicIP)
                            print('{} Update {} record for {}.{}: from {} to {}'.format(datetime.now(), recordType, record['RR'], domainName, recordIPAddr, publicIP))
                    if not found:
                        self.add(resourceRecord, domainName, recordType, publicIP)
                        print('{} Add {} record for {}.{}: {}'.format(datetime.now(), recordType, resourceRecord, domainName, publicIP))
    
    def ddns(self, domainName: str, resourceRecords=default_RRs):
        localIPv4, localIPv6 = self.get_local_ip()
        publicIPv4, publicIPv6 = self.get_publib_ip()

        if publicIPv4 == '' and publicIPv6 == '':
            print('WARN: no public IP found.')
            return

        if publicIPv4 != '' and localIPv4 == publicIPv4:
            self._ddns(domainName, ipv4_record_type, resourceRecords, publicIPv4)

        if publicIPv6 != '' and localIPv6 == publicIPv6:
            self._ddns(domainName, ipv6_record_type, resourceRecords, publicIPv6)
    

def main():
    parser = argparse.ArgumentParser(prog='aliddns', description='Ali DDNS command-line tool.')
    parser.add_argument('-k', '--accesskey-id', help='AccessKey ID')
    parser.add_argument('-s', '--accesskey-secret', help='AccessKey secret')
    parser.add_argument('-d', '--domain-name', help='Your domain name')
    parser.add_argument('-r', '--resource-records', type=list, default=default_RRs, help='Your resource record, e.g. @ *')
    parser.add_argument('--region-id', default='cn-hangzhou', help='Region ID')

    args = parser.parse_args()
   
    ddns = AliDDNS(args.accesskey_id, args.accesskey_secret, args.region_id)
    ddns.ddns(args.domain_name, args.resource_records)
    