import logging
import settings
import os
import json
import codecs
import datetime

def connect():
    try:
        from instagram_private_api import (
            Client, ClientError, ClientLoginError,
            ClientCookieExpiredError, ClientLoginRequiredError,
            __version__ as client_version)
    except ImportError:
        import sys
        sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
        from instagram_private_api import (
            Client, ClientError, ClientLoginError,
            ClientCookieExpiredError, ClientLoginRequiredError,
            __version__ as client_version)


    def to_json(python_object):
        if isinstance(python_object, bytes):
            return {'__class__': 'bytes',
                    '__value__': codecs.encode(python_object, 'base64').decode()}
        raise TypeError(repr(python_object) + ' is not JSON serializable')


    def from_json(json_object):
        if '__class__' in json_object and json_object['__class__'] == 'bytes':
            return codecs.decode(json_object['__value__'].encode(), 'base64')
        return json_object


    def onlogin_callback(api, new_settings_file):
        cache_settings = api.settings
        with open(new_settings_file, 'w') as outfile:
            json.dump(cache_settings, outfile, default=to_json)
            print('SAVED: {0!s}'.format(new_settings_file))

    logging.basicConfig()
    logger = logging.getLogger('instagram_private_api')
    logger.setLevel(logging.WARNING)

    print('Client version: {0!s}'.format(client_version))

    device_id = None
    try:
        cookie_file = "cookie.json"
        if not os.path.isfile(cookie_file):
            # settings file does not exist
            print('Unable to find file: {0!s}'.format(cookie_file))

            # login new
            api = Client(
                settings.env.CRAWLER_INSTAGRAM_LOGIN, settings.env.CRAWLER_INSTAGRAM_PASSWORD,
                on_login=lambda x: onlogin_callback(x, cookie_file))
        else:
            with open(cookie_file) as file_data:
                cached_settings = json.load(file_data, object_hook=from_json)
            print('Reusing settings: {0!s}'.format(cookie_file))

            device_id = cached_settings.get('device_id')
            # reuse auth settings
            api = Client(
                settings.env.CRAWLER_INSTAGRAM_LOGIN, settings.env.CRAWLER_INSTAGRAM_PASSWORD,
                settings=cached_settings)

    except (ClientCookieExpiredError, ClientLoginRequiredError) as e:
        print('ClientCookieExpiredError/ClientLoginRequiredError: {0!s}'.format(e))

        # Login expired
        # Do relogin but use default ua, keys and such
        api = Client(
            settings.env.CRAWLER_INSTAGRAM_LOGIN, settings.env.CRAWLER_INSTAGRAM_PASSWORD,
            device_id=device_id,
            on_login=lambda x: onlogin_callback(x, cookie_file))

    except ClientLoginError as e:
        print('ClientLoginError {0!s}'.format(e))
        exit(9)
    except ClientError as e:
        print('ClientError {0!s} (Code: {1:d}, Response: {2!s})'.format(e.msg, e.code, e.error_response))
        exit(9)
    except Exception as e:
        print('Unexpected Exception: {0!s}'.format(e))
        exit(99)

    # Show when login expires
    cookie_expiry = api.cookie_jar.auth_expires
    print('Cookie Expiry: {0!s}'.format(datetime.datetime.fromtimestamp(cookie_expiry).strftime('%Y-%m-%dT%H:%M:%SZ')))
    return api

INSTAGRAM_API = connect()
