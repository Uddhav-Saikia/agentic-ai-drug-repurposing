"""
Load testing script using locust
"""
from locust import HttpUser, task, between
import random


class DrugRepurposingUser(HttpUser):
    """Simulate user behavior for load testing"""
    
    wait_time = between(1, 3)
    
    def on_start(self):
        """Setup - check health"""
        self.client.get("/api/v1/health")
    
    @task(3)
    def submit_query(self):
        """Submit analysis query"""
        queries = [
            "Find drugs that could treat Alzheimer's disease",
            "What existing drugs might work for COVID-19?",
            "Repurposing opportunities for diabetes treatments",
            "Alternative uses for cancer drugs"
        ]
        
        response = self.client.post(
            "/api/v1/queries",
            json={
                "question": random.choice(queries),
                "priority": random.choice(["low", "normal", "high"])
            }
        )
        
        if response.status_code == 200:
            query_id = response.json()["id"]
            # Check status
            self.client.get(f"/api/v1/queries/{query_id}/status")
    
    @task(5)
    def list_queries(self):
        """List recent queries"""
        self.client.get("/api/v1/queries?skip=0&limit=10")
    
    @task(2)
    def get_query_status(self):
        """Get query status"""
        # Use random ID between 1-100
        query_id = random.randint(1, 100)
        self.client.get(f"/api/v1/queries/{query_id}/status")
    
    @task(2)
    def get_report(self):
        """Get report details"""
        report_id = random.randint(1, 50)
        self.client.get(f"/api/v1/reports/{report_id}")
    
    @task(1)
    def get_system_status(self):
        """Check system status"""
        self.client.get("/api/v1/agents/system-status")


# Run with: locust -f load_test.py --host=http://localhost:8000
