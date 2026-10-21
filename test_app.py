import unittest
import json
import io
import os
import pypdf
from app import app
import database

class FlaskAppTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'test-secret'
        self.client = app.test_client()
        database.init_db()

    def test_index_page(self):
        """Test GET / returns 200 and loads HTML template"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'TalentSync', response.data)


    def test_roles_api(self):
        """Test GET /api/roles returns presets and taxonomy"""
        response = self.client.get('/api/roles')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('presets', data)
        self.assertIn('Software Developer', data['presets'])
        self.assertIn('taxonomy', data)

    def test_save_role_api(self):
        """Test POST /api/roles saves new role and JD into database"""
        payload = {
            'role_title': 'Cloud Reliability Engineer',
            'description': 'Kubernetes Docker AWS Terraform Golang Prometheus Helm CI/CD Linux',
            'required_skills': 'Kubernetes, AWS, Docker'
        }
        res = self.client.post('/api/roles', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['role']['role_title'], 'Cloud Reliability Engineer')

    def test_analyze_api(self):
        """Test POST /api/analyze with valid resume and JD"""
        payload = {
            'resume_text': 'John Doe\nSummary: Software engineer skilled in Python, Flask, SQL, Docker, and REST APIs. Projects: Built web apps. Education: BCA Degree.',
            'job_description': 'Python Flask SQL Docker Git REST APIs Microservices',
            'target_role': 'Python Backend Engineer'
        }
        response = self.client.post('/api/analyze',
                                   data=json.dumps(payload),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('final_score', data)
        self.assertGreater(data['final_score'], 0)
        self.assertIn('PYTHON', data['detected_skills'])
        self.assertIn('FLASK', data['detected_skills'])
        self.assertIn('analysis_id', data)

    def test_user_auth_flow(self):
        """Test registration, login, current user check, and logout"""
        # 1. Register
        reg_payload = {
            'full_name': 'Test User',
            'email': 'testuser@example.com',
            'password': 'securepassword123'
        }
        res = self.client.post('/api/auth/register',
                               data=json.dumps(reg_payload),
                               content_type='application/json')
        self.assertIn(res.status_code, [200, 400]) # 400 if already exists

        # 2. Login
        login_payload = {
            'email': 'testuser@example.com',
            'password': 'securepassword123'
        }
        res_login = self.client.post('/api/auth/login',
                                     data=json.dumps(login_payload),
                                     content_type='application/json')
        self.assertEqual(res_login.status_code, 200)
        login_data = json.loads(res_login.data)
        self.assertTrue(login_data['success'])

        # 3. Current User
        res_user = self.client.get('/api/auth/current-user')
        self.assertEqual(res_user.status_code, 200)
        user_data = json.loads(res_user.data)
        self.assertIsNotNone(user_data['user'])
        self.assertEqual(user_data['user']['email'], 'testuser@example.com')

        # 4. History check
        res_hist = self.client.get('/api/history')
        self.assertEqual(res_hist.status_code, 200)

        # 5. Logout
        res_logout = self.client.post('/api/auth/logout')
        self.assertEqual(res_logout.status_code, 200)

        # 6. Current User should be None after logout
        res_user_after = self.client.get('/api/auth/current-user')
        user_data_after = json.loads(res_user_after.data)
        self.assertIsNone(user_data_after['user'])

    def test_pdf_upload_api(self):
        """Test POST /api/upload-pdf by generating an in-memory PDF"""
        # Create a small valid PDF using pypdf Writer
        writer = pypdf.PdfWriter()
        page = writer.add_blank_page(width=200, height=200)
        stream = io.BytesIO()
        writer.write(stream)
        stream.seek(0)

        response = self.client.post('/api/upload-pdf',
                                   data={'pdf': (stream, 'sample_resume.pdf')},
                                   content_type='multipart/form-data')
        # Even if blank page has no text, it handles cleanly with 422 or 200
        self.assertIn(response.status_code, [200, 422])

if __name__ == '__main__':
    unittest.main()

