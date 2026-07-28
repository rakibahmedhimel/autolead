import os
import unittest
from uuid import uuid4
from unittest.mock import patch


@unittest.skipUnless(os.getenv("TEST_DATABASE_URL"), "TEST_DATABASE_URL is required")
class PostgreSQLIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.environ["DATABASE_URL"] = os.environ["TEST_DATABASE_URL"]
        from fastapi.testclient import TestClient
        from backend.app.main import app
        cls.client = TestClient(app)

    def register_and_login(self, prefix):
        email = f"{prefix}-{uuid4().hex[:8]}@example.com"
        registration = self.client.post("/auth/register", json={
            "name": prefix, "email": email, "password": "StrongPassword123!",
            "is_admin": True,
        })
        self.assertEqual(registration.status_code, 201, registration.text)
        self.assertFalse(registration.json()["is_admin"])
        login = self.client.post("/auth/login", json={"email": email, "password": "StrongPassword123!"})
        self.assertEqual(login.status_code, 200, login.text)
        return {"Authorization": f"Bearer {login.json()['access_token']}"}

    def test_auth_ownership_uniqueness_and_job_idempotency(self):
        first = self.register_and_login("First")
        second = self.register_and_login("Second")
        self.assertEqual(self.client.get("/projects/").status_code, 401)

        created = self.client.post("/projects/", headers=first, json={"name": " India Files ", "description": ""})
        self.assertEqual(created.status_code, 201, created.text)
        project_id = created.json()["id"]
        duplicate = self.client.post("/projects/", headers=first, json={"name": "india   files", "description": ""})
        self.assertEqual(duplicate.status_code, 409, duplicate.text)
        other = self.client.post("/projects/", headers=second, json={"name": "INDIA FILES", "description": ""})
        self.assertEqual(other.status_code, 201, other.text)
        self.assertEqual(self.client.get(f"/projects/{project_id}", headers=second).status_code, 404)

        payload = {"project_id": project_id, "country": "India", "province": None,
                   "industries": ["Retail"], "lead_count": 5}
        key = uuid4().hex
        with patch("backend.app.routers.jobs.generate_leads", return_value={"id": "agent-test"}):
            one = self.client.post("/jobs/generate", headers={**first, "Idempotency-Key": key}, json=payload)
            two = self.client.post("/jobs/generate", headers={**first, "Idempotency-Key": key}, json=payload)
            three = self.client.post("/jobs/generate", headers={**first, "Idempotency-Key": uuid4().hex}, json=payload)
        self.assertEqual(one.status_code, 200, one.text)
        self.assertEqual(one.json()["job_id"], two.json()["job_id"])
        self.assertNotEqual(one.json()["job_id"], three.json()["job_id"])

    def test_spreadsheet_missing_cells_credit_once_and_download(self):
        headers = self.register_and_login("Sheet")
        project = self.client.post("/projects/", headers=headers, json={"name": f"Sheet {uuid4().hex}", "description": ""}).json()
        uploaded = self.client.post(
            "/spreadsheets/upload",
            headers={**headers, "Idempotency-Key": uuid4().hex},
            data={"project_id": project["id"]},
            files={"file": ("companies.csv", b"Website,Email,LinkedIn\nhttps://example.com,existing@example.com,\n", "text/csv")},
        )
        self.assertEqual(uploaded.status_code, 201, uploaded.text)
        job_id = uploaded.json()["id"]
        mapped = self.client.put(f"/spreadsheets/{job_id}/mapping", headers=headers, json={
            "website_column": "Website", "field_columns": {"email": "Email", "linkedin": "LinkedIn"},
        })
        self.assertEqual(mapped.status_code, 200, mapped.text)
        with patch("backend.app.routers.spreadsheets.crawl_company",
                   return_value=({"email": "new@example.com", "linkedin": "https://linkedin.com/company/example"},
                                 "https://example.com")):
            first = self.client.post(f"/spreadsheets/{job_id}/enrich?limit=5", headers=headers)
            second = self.client.post(f"/spreadsheets/{job_id}/enrich?limit=5", headers=headers)
        self.assertEqual(first.json()["credits_added"], 1)
        self.assertEqual(first.json()["credits_used"], 1)
        self.assertEqual(second.json()["credits_added"], 0)
        download = self.client.get(f"/spreadsheets/{job_id}/download.xlsx", headers=headers)
        self.assertEqual(download.status_code, 200)


if __name__ == "__main__":
    unittest.main()
