import requests
from entities import Error
from restore import config_object
import os

API_URL = 'https://app.octobrowser.net/api/v2/automation/'
LOCAL_API_URL = 'http://localhost:58888/api/'


def get_profiles():
    request_data = {
        'search_tags': config_object.tag_name,
        'fields': 'title',
        'ordering': 'created',
        'page': 0
    }

    headers = {
        'X-Octo-Api-Token': config_object.api_token
    }

    result = []

    while 1:
        try:
            r = requests.get(API_URL + 'profiles', params=request_data, headers=headers).json()
        except Exception as e:
            return Error('Profiles searching error', 'An error occurred while processing the response from OctoBrowser', e)
        else:
            if not r.get('success'):
                return Error('Profiles searching error', r)
            else:
                if not r['data']:
                    return result

                for i in r['data']:
                    result.append(i)

                request_data['page'] += 1


def run_profile(uuid):
    metamask_path = os.path.abspath('metamask')

    request_data = {
        'uuid': uuid,
        'debug_port': True,
        'flags': [f'--load-extension={metamask_path}']
    }

    try:
        r = requests.post(LOCAL_API_URL + 'profiles/start', json=request_data).json()
    except Exception as e:
        return Error('Profile launching error', 'An error occurred while processing the response from OctoBrowser', e)
    else:
        if r.get('state') != 'STARTED':
            return Error('Profile launching error', r)
        else:
            return r.get('debug_port')
