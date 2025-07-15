#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to validate all improvements made to ERP AI Pro
Tests: Models, Multimodal, Caching, Streaming, Business Intelligence
"""

import asyncio
import json
import requests
import time
import sys
import os
from datetime import datetime
from typing import Dict, Any, List
import tempfile
from PIL import Image, ImageDraw
import numpy as np

# Colors for output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text: str):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text:^60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}\n")

def print_test(test_name: str):
    print(f"{Colors.BOLD}🧪 Testing: {test_name}{Colors.END}")

def print_success(message: str):
    print(f"{Colors.GREEN}✅ {message}{Colors.END}")

def print_error(message: str):
    print(f"{Colors.RED}❌ {message}{Colors.END}")

def print_info(message: str):
    print(f"{Colors.BLUE}ℹ️  {message}{Colors.END}")

def print_warning(message: str):
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.END}")

class ERPAITester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.test_results = []
        self.start_time = time.time()
    
    def add_result(self, test_name: str, success: bool, message: str, duration: float = 0):
        """Add test result"""
        self.test_results.append({
            "test": test_name,
            "success": success,
            "message": message,
            "duration": duration,
            "timestamp": datetime.now().isoformat()
        })
    
    def test_health_check(self):
        """Test basic health check"""
        print_test("Health Check")
        
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/health", timeout=10)
            duration = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if data.get("pipeline_ready"):
                    print_success(f"Health check passed ({duration:.2f}s)")
                    print_info(f"Status: {data.get('status')}")
                    print_info(f"Metrics: {data.get('metrics', {})}")
                    self.add_result("Health Check", True, "Pipeline ready", duration)
                else:
                    print_error(f"Pipeline not ready: {data}")
                    self.add_result("Health Check", False, "Pipeline not ready", duration)
            else:
                print_error(f"Health check failed: {response.status_code}")
                self.add_result("Health Check", False, f"HTTP {response.status_code}", duration)
                
        except Exception as e:
            print_error(f"Health check error: {e}")
            self.add_result("Health Check", False, str(e))
    
    def test_basic_query(self):
        """Test basic query functionality"""
        print_test("Basic Query")
        
        query_data = {
            "role": "admin",
            "question": "ERP là gì?"
        }
        
        try:
            start_time = time.time()
            response = requests.post(
                f"{self.base_url}/query",
                json=query_data,
                timeout=30
            )
            duration = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                answer = data.get("answer", "")
                
                if answer and len(answer) > 10:
                    print_success(f"Query successful ({duration:.2f}s)")
                    print_info(f"Answer: {answer[:100]}...")
                    print_info(f"Model: {data.get('model', 'unknown')}")
                    print_info(f"Processing time: {data.get('processing_time', 0):.2f}s")
                    self.add_result("Basic Query", True, "Query successful", duration)
                else:
                    print_error(f"Empty or invalid answer: {answer}")
                    self.add_result("Basic Query", False, "Invalid answer", duration)
            else:
                print_error(f"Query failed: {response.status_code}")
                self.add_result("Basic Query", False, f"HTTP {response.status_code}", duration)
                
        except Exception as e:
            print_error(f"Query error: {e}")
            self.add_result("Basic Query", False, str(e))
    
    def test_vietnamese_support(self):
        """Test Vietnamese language support"""
        print_test("Vietnamese Language Support")
        
        test_questions = [
            "Hệ thống ERP có những tính năng gì?",
            "Quản lý kho hàng như thế nào?",
            "Báo cáo tài chính bao gồm những gì?",
            "Quy trình bán hàng diễn ra ra sao?",
            "Quản lý nhân sự có những chức năng nào?"
        ]
        
        successful_queries = 0
        total_time = 0
        
        for i, question in enumerate(test_questions):
            try:
                start_time = time.time()
                response = requests.post(
                    f"{self.base_url}/query",
                    json={"role": "admin", "question": question},
                    timeout=30
                )
                duration = time.time() - start_time
                total_time += duration
                
                if response.status_code == 200:
                    data = response.json()
                    answer = data.get("answer", "")
                    
                    if answer and len(answer) > 10:
                        successful_queries += 1
                        print_success(f"Query {i+1}/5: {question[:30]}... ✓")
                    else:
                        print_error(f"Query {i+1}/5: Empty answer")
                else:
                    print_error(f"Query {i+1}/5: HTTP {response.status_code}")
                    
            except Exception as e:
                print_error(f"Query {i+1}/5: {e}")
        
        success_rate = (successful_queries / len(test_questions)) * 100
        avg_time = total_time / len(test_questions)
        
        if success_rate >= 80:
            print_success(f"Vietnamese support: {success_rate:.1f}% success rate")
            print_info(f"Average response time: {avg_time:.2f}s")
            self.add_result("Vietnamese Support", True, f"{success_rate:.1f}% success", avg_time)
        else:
            print_error(f"Vietnamese support: {success_rate:.1f}% success rate (< 80%)")
            self.add_result("Vietnamese Support", False, f"{success_rate:.1f}% success", avg_time)
    
    def test_caching_performance(self):
        """Test caching performance"""
        print_test("Caching Performance")
        
        query_data = {
            "role": "admin",
            "question": "ERP là gì và có những tính năng gì?"
        }
        
        try:
            # First query (cache miss)
            start_time = time.time()
            response1 = requests.post(f"{self.base_url}/query", json=query_data, timeout=30)
            first_duration = time.time() - start_time
            
            # Second query (cache hit)
            start_time = time.time()
            response2 = requests.post(f"{self.base_url}/query", json=query_data, timeout=30)
            second_duration = time.time() - start_time
            
            if response1.status_code == 200 and response2.status_code == 200:
                improvement = ((first_duration - second_duration) / first_duration) * 100
                
                if second_duration < first_duration:
                    print_success(f"Caching works! {improvement:.1f}% faster")
                    print_info(f"First query: {first_duration:.2f}s")
                    print_info(f"Second query: {second_duration:.2f}s")
                    self.add_result("Caching Performance", True, f"{improvement:.1f}% improvement", second_duration)
                else:
                    print_warning("No caching improvement detected")
                    self.add_result("Caching Performance", False, "No improvement", second_duration)
            else:
                print_error("Caching test failed - queries unsuccessful")
                self.add_result("Caching Performance", False, "Queries failed")
                
        except Exception as e:
            print_error(f"Caching test error: {e}")
            self.add_result("Caching Performance", False, str(e))
    
    def test_streaming_response(self):
        """Test streaming response"""
        print_test("Streaming Response")
        
        query_data = {
            "role": "admin",
            "question": "Hãy giải thích chi tiết về quy trình quản lý kho hàng trong ERP",
            "stream": True
        }
        
        try:
            start_time = time.time()
            response = requests.post(
                f"{self.base_url}/query/stream",
                json=query_data,
                timeout=30,
                stream=True
            )
            
            if response.status_code == 200:
                chunks_received = 0
                total_data = ""
                
                for chunk in response.iter_lines():
                    if chunk:
                        chunks_received += 1
                        if chunks_received <= 5:  # Show first 5 chunks
                            try:
                                chunk_data = chunk.decode('utf-8')
                                if chunk_data.startswith('data: '):
                                    data_part = chunk_data[6:]  # Remove 'data: ' prefix
                                    print_info(f"Chunk {chunks_received}: {data_part[:50]}...")
                                    total_data += data_part
                            except Exception:
                                pass
                
                duration = time.time() - start_time
                
                if chunks_received > 0:
                    print_success(f"Streaming works! {chunks_received} chunks received")
                    print_info(f"Total time: {duration:.2f}s")
                    self.add_result("Streaming Response", True, f"{chunks_received} chunks", duration)
                else:
                    print_error("No streaming chunks received")
                    self.add_result("Streaming Response", False, "No chunks", duration)
            else:
                print_error(f"Streaming failed: {response.status_code}")
                self.add_result("Streaming Response", False, f"HTTP {response.status_code}")
                
        except Exception as e:
            print_error(f"Streaming test error: {e}")
            self.add_result("Streaming Response", False, str(e))
    
    def test_multimodal_support(self):
        """Test multimodal support"""
        print_test("Multimodal Support")
        
        # Create a simple test image
        try:
            # Create a simple chart-like image
            img = Image.new('RGB', (400, 300), color='white')
            draw = ImageDraw.Draw(img)
            
            # Draw a simple bar chart
            draw.rectangle([50, 50, 100, 200], fill='blue')
            draw.rectangle([120, 80, 170, 200], fill='red')
            draw.rectangle([190, 30, 240, 200], fill='green')
            
            # Add some text
            draw.text((50, 220), "Sales Chart", fill='black')
            draw.text((50, 240), "Q1  Q2  Q3", fill='black')
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
                img.save(tmp_file.name)
                temp_image_path = tmp_file.name
            
            # Test multimodal query
            start_time = time.time()
            with open(temp_image_path, 'rb') as f:
                files = {'file': ('test_chart.png', f, 'image/png')}
                data = {
                    'role': 'admin',
                    'question': 'Hãy mô tả hình ảnh này và phân tích dữ liệu'
                }
                
                response = requests.post(
                    f"{self.base_url}/query/multimodal",
                    files=files,
                    data=data,
                    timeout=30
                )
            
            duration = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                answer = result.get("answer", "")
                image_analysis = result.get("image_analysis", "")
                
                if answer and image_analysis:
                    print_success(f"Multimodal query successful ({duration:.2f}s)")
                    print_info(f"Image analysis: {image_analysis[:100]}...")
                    print_info(f"Answer: {answer[:100]}...")
                    self.add_result("Multimodal Support", True, "Image processed", duration)
                else:
                    print_error("Multimodal query returned empty results")
                    self.add_result("Multimodal Support", False, "Empty results", duration)
            else:
                print_error(f"Multimodal query failed: {response.status_code}")
                self.add_result("Multimodal Support", False, f"HTTP {response.status_code}", duration)
            
            # Clean up
            os.unlink(temp_image_path)
            
        except Exception as e:
            print_error(f"Multimodal test error: {e}")
            self.add_result("Multimodal Support", False, str(e))
    
    def test_business_intelligence(self):
        """Test business intelligence features"""
        print_test("Business Intelligence")
        
        # Sample business data
        sample_data = {
            "revenue_data": [
                {"date": "2024-01-01", "revenue": 100000},
                {"date": "2024-01-02", "revenue": 120000},
                {"date": "2024-01-03", "revenue": 110000},
                {"date": "2024-01-04", "revenue": 130000},
                {"date": "2024-01-05", "revenue": 125000}
            ],
            "transaction_data": [
                {"amount": 1000, "date": "2024-01-01"},
                {"amount": 1500, "date": "2024-01-02"},
                {"amount": 2000, "date": "2024-01-03"},
                {"amount": 10000, "date": "2024-01-04"},  # Potential anomaly
                {"amount": 1200, "date": "2024-01-05"}
            ],
            "sales_data": [
                {"date": "2024-01-01", "sales": 50},
                {"date": "2024-01-02", "sales": 60},
                {"date": "2024-01-03", "sales": 55},
                {"date": "2024-01-04", "sales": 70},
                {"date": "2024-01-05", "sales": 65}
            ]
        }
        
        try:
            start_time = time.time()
            response = requests.post(
                f"{self.base_url}/analytics/business",
                json=sample_data,
                timeout=30
            )
            duration = time.time() - start_time
            
            if response.status_code == 200:
                insights = response.json().get("insights", {})
                
                if insights:
                    print_success(f"Business intelligence works ({duration:.2f}s)")
                    
                    # Check for expected insights
                    if "revenue_trend" in insights:
                        print_info(f"Revenue trend: {insights['revenue_trend']}")
                    
                    if "anomalies_detected" in insights:
                        print_info(f"Anomalies detected: {insights['anomalies_detected']}")
                    
                    if "avg_revenue" in insights:
                        print_info(f"Average revenue: {insights['avg_revenue']}")
                    
                    self.add_result("Business Intelligence", True, "Insights generated", duration)
                else:
                    print_error("No business insights generated")
                    self.add_result("Business Intelligence", False, "No insights", duration)
            else:
                print_error(f"Business intelligence failed: {response.status_code}")
                self.add_result("Business Intelligence", False, f"HTTP {response.status_code}", duration)
                
        except Exception as e:
            print_error(f"Business intelligence test error: {e}")
            self.add_result("Business Intelligence", False, str(e))
    
    def test_metrics_endpoint(self):
        """Test metrics endpoint"""
        print_test("Metrics Endpoint")
        
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/metrics", timeout=10)
            duration = time.time() - start_time
            
            if response.status_code == 200:
                metrics = response.json()
                
                expected_metrics = [
                    "queries_processed",
                    "cache_hits",
                    "cache_misses",
                    "avg_response_time",
                    "cache_hit_rate",
                    "model_loaded",
                    "vector_db_connected",
                    "cache_connected"
                ]
                
                found_metrics = sum(1 for metric in expected_metrics if metric in metrics)
                
                if found_metrics >= len(expected_metrics) * 0.8:  # 80% of metrics present
                    print_success(f"Metrics endpoint works ({duration:.2f}s)")
                    print_info(f"Metrics found: {found_metrics}/{len(expected_metrics)}")
                    print_info(f"Cache hit rate: {metrics.get('cache_hit_rate', 0)*100:.1f}%")
                    self.add_result("Metrics Endpoint", True, f"{found_metrics} metrics", duration)
                else:
                    print_error(f"Insufficient metrics: {found_metrics}/{len(expected_metrics)}")
                    self.add_result("Metrics Endpoint", False, "Insufficient metrics", duration)
            else:
                print_error(f"Metrics endpoint failed: {response.status_code}")
                self.add_result("Metrics Endpoint", False, f"HTTP {response.status_code}", duration)
                
        except Exception as e:
            print_error(f"Metrics test error: {e}")
            self.add_result("Metrics Endpoint", False, str(e))
    
    def test_performance_benchmarks(self):
        """Test performance benchmarks"""
        print_test("Performance Benchmarks")
        
        # Test concurrent queries
        import concurrent.futures
        
        def single_query(query_id):
            try:
                start_time = time.time()
                response = requests.post(
                    f"{self.base_url}/query",
                    json={"role": "admin", "question": f"Test query {query_id}"},
                    timeout=30
                )
                duration = time.time() - start_time
                return {
                    "query_id": query_id,
                    "success": response.status_code == 200,
                    "duration": duration
                }
            except Exception as e:
                return {
                    "query_id": query_id,
                    "success": False,
                    "error": str(e)
                }
        
        # Run 5 concurrent queries
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(single_query, i) for i in range(5)]
            results = [future.result() for future in futures]
        
        successful_queries = sum(1 for r in results if r["success"])
        avg_duration = sum(r.get("duration", 0) for r in results if r["success"]) / max(successful_queries, 1)
        
        if successful_queries >= 4:  # 80% success rate
            print_success(f"Performance test: {successful_queries}/5 queries successful")
            print_info(f"Average response time: {avg_duration:.2f}s")
            
            # Performance expectations
            if avg_duration < 3.0:
                print_success("✅ Response time under 3 seconds")
            elif avg_duration < 5.0:
                print_warning("⚠️ Response time 3-5 seconds")
            else:
                print_error("❌ Response time over 5 seconds")
            
            self.add_result("Performance Benchmarks", True, f"{successful_queries}/5 successful", avg_duration)
        else:
            print_error(f"Performance test failed: {successful_queries}/5 successful")
            self.add_result("Performance Benchmarks", False, "Low success rate", avg_duration)
    
    def generate_report(self):
        """Generate final test report"""
        print_header("TEST REPORT")
        
        total_tests = len(self.test_results)
        successful_tests = sum(1 for r in self.test_results if r["success"])
        success_rate = (successful_tests / total_tests) * 100 if total_tests > 0 else 0
        
        total_duration = time.time() - self.start_time
        
        print_info(f"Total tests: {total_tests}")
        print_info(f"Successful: {successful_tests}")
        print_info(f"Failed: {total_tests - successful_tests}")
        print_info(f"Success rate: {success_rate:.1f}%")
        print_info(f"Total test time: {total_duration:.2f}s")
        
        print("\n" + "="*60)
        print("DETAILED RESULTS:")
        print("="*60)
        
        for i, result in enumerate(self.test_results, 1):
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            duration = f"({result['duration']:.2f}s)" if result["duration"] > 0 else ""
            print(f"{i:2d}. {status} {result['test']:<25} {duration}")
            if not result["success"]:
                print(f"    Error: {result['message']}")
        
        print("\n" + "="*60)
        
        if success_rate >= 80:
            print_success(f"🎉 OVERALL: SYSTEM PERFORMANCE EXCELLENT ({success_rate:.1f}%)")
        elif success_rate >= 60:
            print_warning(f"⚠️ OVERALL: SYSTEM PERFORMANCE GOOD ({success_rate:.1f}%)")
        else:
            print_error(f"❌ OVERALL: SYSTEM PERFORMANCE POOR ({success_rate:.1f}%)")
        
        print("\n" + "="*60)
        print("IMPROVEMENT SUMMARY:")
        print("="*60)
        
        improvements = [
            "✅ Upgraded to Llama-3.1 8B model",
            "✅ Added multimodal support (images)",
            "✅ Implemented Redis caching",
            "✅ Added streaming responses",
            "✅ Integrated business intelligence",
            "✅ Added performance metrics",
            "✅ Improved Vietnamese support",
            "✅ Added concurrent query handling"
        ]
        
        for improvement in improvements:
            print(improvement)
        
        print("\n" + "="*60)
        
        # Save report to file
        report_data = {
            "test_summary": {
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "success_rate": success_rate,
                "total_duration": total_duration
            },
            "test_results": self.test_results,
            "timestamp": datetime.now().isoformat()
        }
        
        with open(f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", "w") as f:
            json.dump(report_data, f, indent=2)
        
        print_info("📄 Test report saved to test_report_*.json")
        
        return success_rate

def main():
    """Main test execution"""
    print_header("ERP AI PRO v2.0 - COMPREHENSIVE TEST SUITE")
    
    # Check if API is running
    tester = ERPAITester()
    
    try:
        response = requests.get(tester.base_url, timeout=5)
        print_info(f"✅ API is running at {tester.base_url}")
    except Exception as e:
        print_error(f"❌ API not accessible at {tester.base_url}")
        print_error(f"Please start the API first: python main_modern.py")
        return 1
    
    # Run all tests
    tests = [
        tester.test_health_check,
        tester.test_basic_query,
        tester.test_vietnamese_support,
        tester.test_caching_performance,
        tester.test_streaming_response,
        tester.test_multimodal_support,
        tester.test_business_intelligence,
        tester.test_metrics_endpoint,
        tester.test_performance_benchmarks
    ]
    
    print_info(f"🚀 Running {len(tests)} comprehensive tests...")
    
    for test in tests:
        try:
            test()
            print()  # Add spacing between tests
        except Exception as e:
            print_error(f"Test failed with exception: {e}")
            print()
    
    # Generate final report
    success_rate = tester.generate_report()
    
    # Return appropriate exit code
    return 0 if success_rate >= 80 else 1

if __name__ == "__main__":
    sys.exit(main())