import unittest
import sys
import os
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR.parent))

from backend.app import create_app

class BackendAPITestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()

    def test_01_health_check(self):
        res = self.client.get('/api/health')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data['status'], 'healthy')

    def test_02_login_success(self):
        res = self.client.post('/api/auth/login', json={
            'email': 'admin@aicte.gov.in',
            'password': os.environ['INITIAL_ADMIN_PASSWORD']
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['user']['name'], 'Deransiya Dorin J')
        self.assertEqual(data['user']['role'], 'Cloud Architect')

    def test_03_login_failure(self):
        res = self.client.post('/api/auth/login', json={
            'email': 'admin@aicte.gov.in',
            'password': 'wrongpassword'
        })
        self.assertEqual(res.status_code, 401)
        data = res.get_json()
        self.assertFalse(data['success'])

    def test_04_dashboard_stats(self):
        res = self.client.get('/api/dashboard/stats')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])
        self.assertGreaterEqual(data['data']['totalComplaints'], 20)
        self.assertIn('resolutionRate', data['data'])

    def test_05_dashboard_charts(self):
        res = self.client.get('/api/dashboard/charts')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(len(data['data']['monthlyTrends']), 12)
        self.assertGreaterEqual(len(data['data']['statusDistribution']), 4)

    def test_06_complaint_lifecycle(self):
        # 1. Create Complaint
        new_comp = {
            'institution': 'Delhi Engineering Academy',
            'institutionId': 'AICTE-IN-99123',
            'institutionType': 'Engineering',
            'state': 'Delhi',
            'district': 'South Delhi',
            'contactPerson': 'Prof. Rajesh Khanna',
            'email': 'rajesh.k@dea.edu.in',
            'phone': '+91-9811223344',
            'category': 'Infrastructure',
            'subject': 'Automated Test: Insufficient computer lab terminals',
            'description': 'Over 200 students are sharing 15 working terminals during scheduled practical sessions.',
            'priority': 'High',
            'consent': True
        }
        res_create = self.client.post('/api/complaints', json=new_comp)
        self.assertEqual(res_create.status_code, 201)
        create_data = res_create.get_json()
        self.assertTrue(create_data['success'])
        comp_id = create_data['complaintId']
        self.assertTrue(comp_id.startswith('AIC-2026-'))

        # 2. Get Complaint
        res_get = self.client.get(f'/api/complaints/{comp_id}')
        self.assertEqual(res_get.status_code, 200)
        get_data = res_get.get_json()
        self.assertEqual(get_data['data']['id'], comp_id)
        self.assertEqual(get_data['data']['status'], 'New')

        # 3. Update Status
        res_status = self.client.patch(f'/api/complaints/{comp_id}/status', json={
            'status': 'In Progress',
            'note': 'Test inspection scheduled.'
        })
        self.assertEqual(res_status.status_code, 200)

        # 4. Assign Bureau
        res_assign = self.client.patch(f'/api/complaints/{comp_id}/assignment', json={
            'bureau': 'Approval Bureau'
        })
        self.assertEqual(res_assign.status_code, 200)

        # 5. Public Tracking
        res_track = self.client.get(f'/api/complaints/{comp_id}/tracking')
        self.assertEqual(res_track.status_code, 200)
        track_data = res_track.get_json()
        self.assertTrue(track_data['found'])
        self.assertEqual(track_data['complaint']['status'], 'In Progress')

    def test_07_bureaus(self):
        res = self.client.get('/api/bureaus')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(len(data['data']), 5)

    def test_08_notifications(self):
        res = self.client.get('/api/notifications')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])
        self.assertGreater(len(data['data']), 0)

    def test_09_csv_export(self):
        res = self.client.get('/api/reports/export?type=complaints')
        self.assertEqual(res.status_code, 200)
        self.assertIn('text/csv', res.content_type)
        self.assertIn(b'Complaint ID,Subject', res.data)

if __name__ == '__main__':
    unittest.main()
