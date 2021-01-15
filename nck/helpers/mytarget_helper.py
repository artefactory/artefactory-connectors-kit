from string import Template

REQUEST_CONFIG = {
    'refresh_agency_token': {
        'url': 'https://target.my.com/api/v2/oauth2/token.json',
        'headers_type': "content_type",
        "offset": False,
        '_campaign_id': False,
        'dates_required': False,
        'ids': False
    },
    'get_campaign_ids': {
        'url': 'https://target.my.com/api/v2/banners.json',
        'headers_type': "authorization",
        "offset": True,
        '_campaign_id': False,
        'dates_required': False,
        'ids': False
    },
    'get_campaign_names': {
        'url': 'https://target.my.com/api/v2/campaigns.json',
        'headers_type': "authorization",
        "offset": True,
        '_campaign_id': False,
        'dates_required': False,
        'ids': False
    },
    'get_banner_ids': {
        'url': 'https://target.my.com/api/v2/banners.json',
        'headers_type': "authorization",
        'offset': True,
        '_campaign_id': True,
        'dates_required': False,
        'ids': True
    },
    'get_banner_stats': {
        'url': 'https://target.my.com/api/v2/statistics/banners/day.json',
        'headers_type': 'authorization',
        'offset': False,
        '_campaign_id': False,
        'dates_required': True,
        'ids': True
    },
    'get_banner_names': {
        'url': Template('https://target.my.com/api/v2/banners/$id.json?fields=id,name'),
        'headers_type': 'authorization',
        "offset": False,
        '_campaign_id': False,
        'dates_required': False,
        'ids': False
    }
}
