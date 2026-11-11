import unittest

from recommendation_service.app import app


class RecommendationAPITests(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()
        self.endpoint = "/api/v2/recommendations/"

    def test_health_check(self):
        response = self.client.get("/health/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["status"], "ok")

    def test_valid_recommendation(self):
        response = self.client.post(self.endpoint, json={
            "category_name": "Comida",
            "spent": "50",
            "limit": "100"
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.get_json()["recommendation"])

    def test_exceeded_budget(self):
        response = self.client.post(self.endpoint, json={
            "category_name": "Transporte",
            "spent": "150",
            "limit": "100"
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn("Superaste", response.get_json()["recommendation"])

    def test_zero_limit(self):
        response = self.client.post(self.endpoint, json={
            "category_name": "Comida",
            "spent": "50",
            "limit": "0"
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()["error"], "invalid_limit")

    def test_negative_expense(self):
        response = self.client.post(self.endpoint, json={
            "category_name": "Comida",
            "spent": "-10",
            "limit": "100"
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()["error"], "invalid_spent")

    def test_missing_fields(self):
        response = self.client.post(self.endpoint, json={
            "spent": "50"
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()["error"], "missing_fields")

    def test_invalid_json(self):
        response = self.client.post(
            self.endpoint,
            data="invalid",
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)

    def test_english_response(self):
        response = self.client.post(self.endpoint, json={
            "category_name": "Food",
            "spent": "80",
            "limit": "100",
            "language": "en"
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.get_json()["recommendation"])


if __name__ == "__main__":
    unittest.main()
