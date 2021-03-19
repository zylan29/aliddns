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

default_RR = '@'

ipv4_record_type = 'A'
ipv6_record_type = 'AAAA'

accept_format = 'json'


class AliDDNS(object):

    def __init__(self, acs_client: AcsClient):
        self.acs_client = acs_client

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

        response = self.acs_client.do_action_with_exception(request)
    
    def add(self, RR: str, domainName: str, recordType: str, value: str): 
        request = AddDomainRecordRequest()
        
        request.set_RR(RR)
        request.set_DomainName(domainName)
        request.set_Type(recordType)
        request.set_Value(value)
        request.set_accept_format(accept_format)

        response = self.acs_client.do_action_with_exception(request)
    
    @staticmethod
    def get_publib_ip():
        publicIPv4 = str(urlopen(ipv4_api_url).read().strip(), encoding='utf-8')
        publicIPv6 = str(urlopen(ipv6_api_url).read().strip(), encoding='utf-8')

        return publicIPv4, publicIPv6
    
    @staticmethod
    def get_local_ip():
        try:
            socketIPv4 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            socketIPv4.connect((ipv4_api, 443))
            localIPv4 = socketIPv4.getsockname()[0]
            socketIPv6 = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
            socketIPv6.connect((ipv6_api, 443))
            localIPv6 = socketIPv6.getsockname()[0]
        finally:
            socketIPv4.close()
            socketIPv6.close()

        return localIPv4, localIPv6
    
    def _ddns(self, domainName: str, recordType: str, publicIP: str):
        domain = self.describe(domainName, recordType)
        if domain['TotalCount'] == 0:
            self.add(default_RR, domainName, recordType, publicIP)
            print('{} Add {} record for {}.{}: {}'.format(datetime.now(), recordType, default_RR, domainName, publicIP))
        elif domain['TotalCount'] > 0:
            if domain['TotalCount'] > 1:
                print('{} CAUTION: Found {} {} records for {}. Simply update the first one!'.format(datetime.now(), domain['TotalCount'], recordType, domainName))

            record = domain['DomainRecords']['Record'][0]
            recordIPAddr = record['Value'].strip()
            if recordIPAddr != publicIP:
                self.update(record['RR'], record['RecordId'], recordType, publicIP)
                print('{} Update {} record for {}.{}: from {} to {}'.format(datetime.now(), recordType, record['RR'], domainName, recordIPAddr, publicIP))
    
    def ddns(self, domainName: str):
        localIPv4, localIPv6 = self.get_local_ip()
        publicIPv4, publicIPv6 = self.get_publib_ip()

        if localIPv4 == publicIPv4:
            self._ddns(domainName, ipv4_record_type, publicIPv4)

        if localIPv6 == publicIPv6:
            self._ddns(domainName, ipv6_record_type, publicIPv6)
    

def main():
    parser = argparse.ArgumentParser(prog='aliddns', description='Ali DDNS command-line tool.')
    parser.add_argument('-k', '--accesskey-id', help='AccessKey ID')
    parser.add_argument('-s', '--accesskey-secret', help='AccessKey secret')
    parser.add_argument('-r', '--region-id', default='cn-hangzhou', help='Region ID')
    parser.add_argument('-d', '--domain-name', help='Your domain name')

    args = parser.parse_args()
    
    client = AcsClient(args.accesskey_id, args.accesskey_secret, args.region_id)
    ddns = AliDDNS(client)
    ddns.ddns(args.domain_name)
    