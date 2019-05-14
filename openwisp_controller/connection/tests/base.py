import os

from django.conf import settings
from openwisp_controller.config.models import Config, Device
from openwisp_controller.config.tests import CreateConfigTemplateMixin

from openwisp_users.tests.utils import TestOrganizationMixin

from .. import settings as app_settings
from ..models import Credentials, DeviceConnection


class CreateConnectionsMixin(CreateConfigTemplateMixin, TestOrganizationMixin):
    device_model = Device
    config_model = Config

    def _create_credentials(self, **kwargs):
        opts = dict(name='Test credentials',
                    connector=app_settings.CONNECTORS[0][0],
                    params={'username': 'root',
                            'password': 'password',
                            'port': 22})
        opts.update(kwargs)
        if 'organization' not in opts:
            opts['organization'] = self._create_org()
        c = Credentials(**opts)
        c.full_clean()
        c.save()
        return c

    def _create_credentials_with_key(self, username='root', port=22, **kwargs):
        opts = dict(name='Test SSH Key',
                    params={'username': username,
                            'key': self._SSH_PRIVATE_KEY,
                            'port': port})
        opts.update(kwargs)
        return self._create_credentials(**opts)

    def _create_device_connection(self, **kwargs):
        opts = dict(enabled=True,
                    params={})
        opts.update(kwargs)
        if 'credentials' not in opts:
            cred_opts = {}
            if 'device' in opts:
                cred_opts = {'organization': opts['device'].organization}
            opts['credentials'] = self._create_credentials(**cred_opts)
        org = opts['credentials'].organization
        if 'device' not in opts:
            opts['device'] = self._create_device(organization=org)
            self._create_config(device=opts['device'])
        dc = DeviceConnection(**opts)
        dc.full_clean()
        dc.save()
        return dc


class SshMixin(object):
    _TEST_RSA_KEY_PATH = os.path.join(settings.BASE_DIR, 'test-key.rsa')
    _SSH_PRIVATE_KEY = None

    class ssh_server:
        host = '127.0.0.1'
        port = 5555

    @classmethod
    def setUpClass(cls):
        super(SshMixin, cls).setUpClass()
        with open(cls._TEST_RSA_KEY_PATH, 'r') as f:
            cls._SSH_PRIVATE_KEY = f.read()