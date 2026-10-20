"""Local browser/caching protection tests; not public-cloud/load acceptance."""

import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from valuation_platform.api.app import create_app
from tests.api.test_cases import BundleFixture, payload


class PublicBoundaryTests(BundleFixture, unittest.TestCase):
    def test_cross_site_rejected_before_body_or_parser(self):
        with TestClient(create_app(self.bundle)) as client:
            with patch('valuation_platform.api.app.body_bytes', side_effect=AssertionError('body read')):
                for path, method in (('/api/v1/cases/run', 'POST'),
                                     ('/api/v1/cases/validate', 'POST'),
                                     ('/api/v1/catalog', 'GET')):
                    response = client.request(method, path, headers={'Sec-Fetch-Site': 'cross-site'})
                    self.assertEqual(response.status_code, 403)
                    self.assertEqual(response.json()['error']['code'], 'cross_site_request')
                    self.assertEqual(response.headers['cache-control'], 'no-store')
                    self.assertEqual(response.headers['x-content-type-options'], 'nosniff')
                    self.assertNotIn('access-control-allow-origin', response.headers)

    def test_same_origin_and_headerless_clients_still_use_existing_contract(self):
        with TestClient(create_app(self.bundle)) as client:
            for site in (None, 'same-origin', 'same-site', 'none'):
                headers = {} if site is None else {'Sec-Fetch-Site': site}
                response = client.post('/api/v1/cases/validate', json=payload(), headers=headers)
                self.assertEqual(response.status_code, 200)
                self.assertFalse(response.json()['calculation_performed'])
            # Origin/CORS is not authentication. A scripted caller can spoof or
            # omit browser metadata; no origin allowlist/distributed quota claim.
            self.assertEqual(client.post('/api/v1/cases/validate', json=payload(),
                                         headers={'Origin': 'https://untrusted.example'}).status_code, 200)

    def test_uniform_no_store_on_validation_errors_unknown_routes_and_failures(self):
        with TestClient(create_app(self.bundle), raise_server_exceptions=False) as client:
            responses = [client.get('/health'), client.get('/api/v1/catalog'),
                         client.get('/missing'), client.get('/api/v1/cases/run'),
                         client.post('/api/v1/cases/validate', content='{',
                                     headers={'Content-Type': 'application/json'}),
                         client.post('/api/v1/cases/validate', content='{}',
                                     headers={'Content-Type': 'text/plain'})]
            with patch('valuation_platform.api.app.body_bytes', side_effect=RuntimeError('SECRET SENTINEL')):
                responses.append(client.post('/api/v1/cases/run', json=payload()))
            self.assertEqual([r.status_code for r in responses], [200, 200, 404, 405, 422, 415, 500])
            for response in responses:
                self.assertEqual(response.headers['cache-control'], 'no-store')
                self.assertEqual(response.headers['x-content-type-options'], 'nosniff')
                self.assertNotIn('SECRET SENTINEL', response.text)


if __name__ == '__main__':
    unittest.main()
