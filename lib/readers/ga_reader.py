import click
import config
import os
import logging
import httplib2

from googleapiclient import discovery
from oauth2client import client, GOOGLE_REVOKE_URI

from lib.commands.command import processor
from lib.readers.reader import Reader
from lib.utils.args import extract_args

DISCOVERY_URI = ('https://analyticsreporting.googleapis.com/$discovery/rest')


@click.command(name="read_ga")
@click.option("--ga-access-token", default = None)
@click.option("--ga-refresh-token", required = True)
@click.option("--ga-client-id", required = True)
@click.option("--ga-client-secret", required = True)
@click.option("--ga-view-id", required = True)
@click.option("--ga-metric", multiple = True)
@click.option("--ga-dimension", multiple = True)
@click.option("--ga-date-range", nargs=2, type=click.DateTime(), multiple = True, default = None)
@processor()
def ga(**kwargs):
    #Should handle valid combinations dimensions/metrics in the API
    return GaReader(**extract_args('ga_', kwargs))


class GaReader(Reader):

    def __init__(self, access_token, refresh_token, client_secret, client_id, **kwargs):
        credentials = client.GoogleCredentials(
        access_token,
        client_id=client_id,
        client_secret=client_secret,
        refresh_token=refresh_token,
        token_expiry=None,
        token_uri='https://accounts.google.com/o/oauth2/token',
        user_agent=None,
        revoke_uri=GOOGLE_REVOKE_URI)
        
        http = credentials.authorize(httplib2.Http())
        credentials.refresh(http)

        self.client_v3 = discovery.build('analytics', 'v3', http=http)   
        self.client_v4 = discovery.build('analytics', 'v4', http=http)    
        self.kwargs = kwargs
    
    def get_date_ranges(self):
        date_ranges = self.kwargs.get('date_range')
        if date_ranges:
            starts = [date_range.split()[0] for date_range in date_ranges]
            idxs = sorted(range(len(starts)), key=lambda k: starts[k])
            date_ranges_sorted = [{"startDate":date_ranges[idx][0], "endDate":date_ranges[idx][1]}  for idx in idxs]
            # checking that all start dates < end dates
            assert (len([el for el in date_ranges_sorted if el["startDate"] > el["endDate"] ]) == 0) , "date start should be inferior to date end"
            return date_ranges_sorted
        else:
            return []

    def get_report_requests(self):
        view_ids = self.kwargs.get('view_id')
        date_ranges = self.get_date_ranges()
        report_requests =  [
                                {
                                        'viewId': view_id,
                                        'metrics': [{'expression': val } for val in self.kwargs.get('metric', [])],
                                        'dimensions':[{'name': val } for val in self.kwargs.get('dimension', [])],
                                }
                                if (len(date_ranges) > 0)
                                else
                                {       'dateRanges': date_ranges,
                                        'viewId': view_id,
                                        'metrics': [{'expression': val } for val in self.kwargs.get('metric', [])],
                                        'dimensions':[{'name': val } for val in self.kwargs.get('dimension', [])],
                                }
                                for view_id in view_ids
                            ]
        return report_requests
    
            
    def get_body(self):
        body = {
            'reportRequests': self.get_report_requests()
        }
        return body


