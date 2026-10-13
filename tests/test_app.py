import os, tempfile, unittest
import app as app_module
class AppTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); app_module.DATABASE=os.path.join(self.tmp.name,'test.db')
        app_module.app.config['TESTING']=True; self.client=app_module.app.test_client()
    def tearDown(self): self.tmp.cleanup(); app_module.DATABASE='/app/data/devapps.db'
    def test_health(self):
        r=self.client.get('/health'); self.assertEqual(r.status_code,200); self.assertEqual(r.json['status'],'ok')
    def test_register_and_login(self):
        r=self.client.post('/register',data={'name':'Test Student','email':'student@example.test','password':'student123'},follow_redirects=True); self.assertEqual(r.status_code,200)
        r=self.client.post('/login',data={'email':'student@example.test','password':'student123'},follow_redirects=True); self.assertEqual(r.status_code,200); self.assertIn(b'Gadget inventory',r.data)
if __name__=='__main__': unittest.main()
