from gsapi_server import app, db
import json
from unittest import TestCase


links_data = [
    dict
    (
        engine_name=f'engine_name{x}',
        target_url=f'http://targeturl{x}.com',
        url=f'http://url{x}'
    )
    for x in range(100)
]

headers = {'Content-Type': 'application/json'}


class GsapiTestCase(TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app = app.test_client()
        db.drop_all()
        db.create_all()
        
        # insert links
        for l in links_data:   
            response = self.post_link(l)
            r_json = json.loads(response.data)
            self.assertEqual(response._status_code, 200)
            self.assertEqual(r_json['success'], 1)

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    ########################
    #### helper methods ####
    ########################

    def post_link(self, l: dict):
        _e = l['engine_name']
        return self.app.post(f'/api/link/create/{_e}', headers=headers, data=json.dumps(l))

    def consume_link(self, e: str):
        return self.app.get(f'/api/link/consume/{e}')

    def set_redirect(self, id_: int, r: str):
        return self.app.get(f'/api/link/set_redirect/{id_}/{r}')

    def verify_redirect(self, id_: int):
        return self.app.get(f'/api/link/verify_redirect/{id_}')

    def set_not_working(self, id_: int):
        return self.app.get(f'/api/link/set_not_working/{id_}')

    ########################
    #### tests ####
    ########################
    # todo verify database counts and integrity

    def test_homepage(self):
        r = self.app.get("/")
        r_json = json.loads(r.data)
        self.assertEqual(r_json['success'], 1)
        self.assertEqual(r_json['results'], "Server works just fine :)")

    def test_consume_links_OK(self):
        for l in links_data:
            response = self.consume_link(l['engine_name'])
            r_json = json.loads(response.data)
            # asserts
            self.assertEqual(r_json['success'], 1)

    def test_consume_links_WARNING(self):
        # first consume
        for l in links_data:
            response = self.consume_link(l['engine_name'])
            r_json = json.loads(response.data)
            self.assertEqual(r_json['success'], 1)

        # second consume, warnings
        for l in links_data:
            response = self.consume_link(l['engine_name'])
            r_json = json.loads(response.data)
            self.assertEqual(r_json['success'], 0)

    def test_set_redirect_links_OK(self):
        for i, l in enumerate(links_data, 1):
            response = self.set_redirect(i, 'http://google.com')
            r_json = json.loads(response.data)
            self.assertEqual(r_json['success'], 1)

    def test_verify_redirects_OK(self):
        # set redirects
        for i, l in enumerate(links_data, 1):
            response = self.set_redirect(i, 'http://google.com')
            r_json = json.loads(response.data)
            self.assertEqual(r_json['success'], 1)
        # verify redirects
        for i, l in enumerate(links_data, 1):
            response = self.verify_redirect(i)
            assert response.headers['location'] == 'http://google.com'

    def test_set_not_working(self):
        for i, l in enumerate(links_data, 1):
            response = self.set_not_working(i)
            r_json = json.loads(response.data)
            self.assertEqual(r_json['success'], 1)

    def test_whole_set1(self):
        # first consume
        for l in links_data:
            response = self.consume_link(l['engine_name'])
            r_json = json.loads(response.data)
            self.assertEqual(r_json['success'], 1)

        # set redirects
        for i, l in enumerate(links_data, 1):
            response = self.set_redirect(i, 'http://google.com')
            r_json = json.loads(response.data)
            self.assertEqual(r_json['success'], 1)

        # second consume, warnings
        for l in links_data:
            response = self.consume_link(l['engine_name'])
            r_json = json.loads(response.data)
            self.assertEqual(r_json['success'], 0)

        # verify redirects
        for i, l in enumerate(links_data, 1):
            response = self.verify_redirect(i)
            assert response.headers['location'] == 'http://google.com'

        # verify redirects
        for i, l in enumerate(links_data, 1):
            response = self.verify_redirect(i)
            assert response.headers['location'] == 'http://google.com'

    def test_whole_set2(self):
        # first consume
        for l in links_data:
            response = self.consume_link(l['engine_name'])
            r_json = json.loads(response.data)
            self.assertEqual(r_json['success'], 1)

        # second consume, warnings
        for l in links_data:
            response = self.consume_link(l['engine_name'])
            r_json = json.loads(response.data)
            self.assertEqual(r_json['success'], 0)

        # set not working
        for i, l in enumerate(links_data, 1):
            response = self.set_not_working(i)
            r_json = json.loads(response.data)
            self.assertEqual(r_json['success'], 1)

        # first consume
        for l in links_data:
            response = self.consume_link(l['engine_name'])
            r_json = json.loads(response.data)
            self.assertEqual(r_json['success'], 1)

        # set redirects
        for i, l in enumerate(links_data, 1):
            response = self.set_redirect(i, 'http://google.com')
            r_json = json.loads(response.data)
            self.assertEqual(r_json['success'], 1)

        # verify redirects
        for i, l in enumerate(links_data, 1):
            response = self.verify_redirect(i)
            assert response.headers['location'] == 'http://google.com'

        # second consume, warnings
        for l in links_data:
            response = self.consume_link(l['engine_name'])
            r_json = json.loads(response.data)
            self.assertEqual(r_json['success'], 0)

        # verify redirects
        for i, l in enumerate(links_data, 1):
            response = self.verify_redirect(i)
            assert response.headers['location'] == 'http://google.com'


if __name__ == '__main__':
    TestCase.main()
