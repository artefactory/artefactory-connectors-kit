
REQUEST_TYPES = ["performance", "budget"]

REQUEST_CONFIG = {
    'refresh_agency_token': {
        'url': 'https://target.my.com/api/v2/oauth2/token.json',
        'headers_type': "content_type",
        "offset": False,
        '_campaign_id': False,
        'dates_required': False,
        'ids': False
    },
    'get_campaign_ids_names': {
        'url': 'https://target.my.com/api/v2/campaigns.json?fields=id,name',
        'headers_type': "authorization",
        "offset": True,
        '_campaign_id': False,
        'dates_required': False,
        'ids': False
    },
    'get_banner_ids_names': {
        'url': 'https://target.my.com/api/v2/banners.json?fields=id,name,campaign_id',
        'headers_type': "authorization",
        'offset': True,
        '_campaign_id': False,
        'dates_required': False,
        'ids': False
    },
    'get_banner_stats': {
        'url': 'https://target.my.com/api/v2/statistics/banners/day.json',
        'headers_type': 'authorization',
        'offset': False,
        '_campaign_id': False,
        'dates_required': True,
        'ids': False
    },
    'get_campaign_budgets': {
        'url': "https://target.my.com/api/v2/campaigns.json?fields=id,name,budget_limit,budget_limit_day",
        'headers_type': "authorization",
        "offset": True,
        '_campaign_id': False,
        'dates_required': False,
        'ids': False
    }
}
