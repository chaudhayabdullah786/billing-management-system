#!/usr/bin/env python3
"""
API Test Script for Grocery Store Billing System
Run this script to test the API endpoints.
"""

import requests
import json

BASE_URL = "http://localhost:5000"

class APITester:
    def __init__(self, base_url):
        self.base_url = base_url
        self.session = requests.Session()
    
    def login(self, username="admin", password="admin123"):
        """Login and get session cookie"""
        print(f"\n{'='*50}")
        print("Testing Login...")
        print(f"{'='*50}")
        
        response = self.session.post(
            f"{self.base_url}/login",
            data={"username": username, "password": password},
            allow_redirects=False
        )
        
        if response.status_code == 302:
            print(f"[OK] Login successful for user: {username}")
            return True
        else:
            print(f"[FAIL] Login failed: {response.status_code}")
            return False
    
    def test_get_products(self):
        """Test GET /api/products"""
        print(f"\n{'='*50}")
        print("Testing GET /api/products...")
        print(f"{'='*50}")
        
        response = self.session.get(f"{self.base_url}/api/products")
        
        if response.status_code == 200:
            products = response.json()
            print(f"[OK] Retrieved {len(products)} products")
            if products:
                print(f"     Sample: {products[0]['name']} - ${products[0]['price']}")
            return products
        else:
            print(f"[FAIL] Status: {response.status_code}")
            return None
    
    def test_search_products(self, query="milk"):
        """Test GET /api/products/search"""
        print(f"\n{'='*50}")
        print(f"Testing GET /api/products/search?q={query}...")
        print(f"{'='*50}")
        
        response = self.session.get(
            f"{self.base_url}/api/products/search",
            params={"q": query}
        )
        
        if response.status_code == 200:
            products = response.json()
            print(f"[OK] Found {len(products)} products matching '{query}'")
            return products
        else:
            print(f"[FAIL] Status: {response.status_code}")
            return None
    
    def test_get_customers(self):
        """Test GET /api/customers"""
        print(f"\n{'='*50}")
        print("Testing GET /api/customers...")
        print(f"{'='*50}")
        
        response = self.session.get(f"{self.base_url}/api/customers")
        
        if response.status_code == 200:
            customers = response.json()
            print(f"[OK] Retrieved {len(customers)} customers")
            return customers
        else:
            print(f"[FAIL] Status: {response.status_code}")
            return None
    
    def test_get_dashboard_stats(self):
        """Test GET /api/dashboard/stats"""
        print(f"\n{'='*50}")
        print("Testing GET /api/dashboard/stats...")
        print(f"{'='*50}")
        
        response = self.session.get(f"{self.base_url}/api/dashboard/stats")
        
        if response.status_code == 200:
            stats = response.json()
            print(f"[OK] Dashboard stats retrieved")
            print(f"     Daily sales data points: {len(stats.get('daily_sales', []))}")
            print(f"     Top products: {len(stats.get('top_products', []))}")
            print(f"     Out of stock: {stats.get('out_of_stock', 0)}")
            print(f"     Low stock: {stats.get('low_stock', 0)}")
            return stats
        else:
            print(f"[FAIL] Status: {response.status_code}")
            return None
    
    def test_create_invoice(self):
        """Test POST /api/invoice/create"""
        print(f"\n{'='*50}")
        print("Testing POST /api/invoice/create...")
        print(f"{'='*50}")
        
        products = self.test_get_products()
        if not products or len(products) < 2:
            print("[SKIP] Need at least 2 products to test invoice creation")
            return None
        
        invoice_data = {
            "customer_id": None,
            "items": [
                {"product_id": products[0]["id"], "quantity": 2},
                {"product_id": products[1]["id"], "quantity": 1}
            ],
            "discount_percent": 5,
            "payment_method": "cash"
        }
        
        response = self.session.post(
            f"{self.base_url}/api/invoice/create",
            json=invoice_data
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                invoice = result["invoice"]
                print(f"[OK] Invoice created: {invoice['invoice_number']}")
                print(f"     Total: ${invoice['total_amount']:.2f}")
                print(f"     Items: {len(invoice['items'])}")
                return invoice
            else:
                print(f"[FAIL] {result.get('error', 'Unknown error')}")
                return None
        else:
            print(f"[FAIL] Status: {response.status_code}")
            return None
    
    def test_get_invoice(self, invoice_id):
        """Test GET /api/invoice/<id>"""
        print(f"\n{'='*50}")
        print(f"Testing GET /api/invoice/{invoice_id}...")
        print(f"{'='*50}")
        
        response = self.session.get(f"{self.base_url}/api/invoice/{invoice_id}")
        
        if response.status_code == 200:
            invoice = response.json()
            print(f"[OK] Invoice retrieved: {invoice['invoice_number']}")
            return invoice
        else:
            print(f"[FAIL] Status: {response.status_code}")
            return None
    
    def run_all_tests(self):
        """Run all API tests"""
        print("\n" + "="*60)
        print("   GROCERY STORE BILLING SYSTEM - API TEST SUITE")
        print("="*60)
        
        if not self.login():
            print("\n[ERROR] Cannot proceed without login")
            return
        
        self.test_get_products()
        self.test_search_products("Apple")
        self.test_get_customers()
        self.test_get_dashboard_stats()
        
        invoice = self.test_create_invoice()
        if invoice:
            self.test_get_invoice(invoice["id"])
        
        print("\n" + "="*60)
        print("   TEST SUITE COMPLETED")
        print("="*60)


if __name__ == "__main__":
    tester = APITester(BASE_URL)
    tester.run_all_tests()
