"""
Human Resource Management (HRM) Agent for ERP AI Pro Version
Comprehensive HR management including recruitment, payroll, performance, training, and employee lifecycle.
"""

import os
import requests
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from enum import Enum

# Configuration
ERP_API_BASE_URL = os.getenv("ERP_API_BASE_URL", "http://localhost:9000/api")
ERP_API_TOKEN = os.getenv("ERP_API_TOKEN", "demo-token")

HEADERS = {
    "Authorization": f"Bearer {ERP_API_TOKEN}",
    "Content-Type": "application/json"
}

class EmployeeStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    TERMINATED = "terminated"
    ON_LEAVE = "on_leave"
    PROBATION = "probation"

class LeaveType(Enum):
    ANNUAL = "annual"
    SICK = "sick"
    MATERNITY = "maternity"
    PATERNITY = "paternity"
    PERSONAL = "personal"
    EMERGENCY = "emergency"

class PerformanceRating(Enum):
    OUTSTANDING = "outstanding"
    EXCEEDS_EXPECTATIONS = "exceeds_expectations"
    MEETS_EXPECTATIONS = "meets_expectations"
    BELOW_EXPECTATIONS = "below_expectations"
    POOR = "poor"

# ===== EMPLOYEE MANAGEMENT =====

class CreateEmployeeInput(BaseModel):
    employee_data: Dict[str, Any] = Field(description="The data for the new employee, including personal_info, employment, and compensation details.")

class CreateEmployeeOutput(BaseModel):
    success: bool = Field(description="True if the employee was created successfully, False otherwise.")
    data: Optional[Dict[str, Any]] = Field(None, description="The created employee data if successful.")
    error: Optional[str] = Field(None, description="Error message if the operation failed.")

class CreateEmployeeTool:
    """Tạo hồ sơ nhân viên mới."""
    input_schema = CreateEmployeeInput
    output_schema = CreateEmployeeOutput

    def run(self, employee_data: Dict[str, Any]) -> CreateEmployeeOutput:
        url = f"{ERP_API_BASE_URL}/employees"
        try:
            resp = requests.post(url, headers=HEADERS, json=employee_data, timeout=15)
            resp.raise_for_status()
            return CreateEmployeeOutput(success=True, data=resp.json())
        except Exception as e:
            return CreateEmployeeOutput(success=False, error=str(e))

def update_employee_info(employee_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
    """Cập nhật thông tin nhân viên."""
    url = f"{ERP_API_BASE_URL}/employees/{employee_id}"
    try:
        resp = requests.put(url, headers=HEADERS, json=update_data, timeout=15)
        resp.raise_for_status()
        return {"success": True, "data": resp.json()}
    except Exception as e:
        return {"success": False, "error": str(e)}

class GetEmployeeProfileInput(BaseModel):
    employee_id: str = Field(description="The ID of the employee to get the profile for.")

class GetEmployeeProfileOutput(BaseModel):
    success: bool = Field(description="True if the operation was successful, False otherwise.")
    data: Optional[Dict[str, Any]] = Field(None, description="The employee profile data if successful.")
    error: Optional[str] = Field(None, description="Error message if the operation failed.")

class GetEmployeeProfileTool:
    """Lấy hồ sơ chi tiết nhân viên."""
    input_schema = GetEmployeeProfileInput
    output_schema = GetEmployeeProfileOutput

    def run(self, employee_id: str) -> GetEmployeeProfileOutput:
        url = f"{ERP_API_BASE_URL}/employees/{employee_id}/profile"
        try:
            resp = requests.get(url, headers=HEADERS, timeout=10)
            resp.raise_for_status()
            return GetEmployeeProfileOutput(success=True, data=resp.json())
        except Exception as e:
            return GetEmployeeProfileOutput(success=False, error=str(e))

def terminate_employee(employee_id: str, termination_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Kết thúc hợp đồng lao động.
    
    Args:
        termination_data: {
            "termination_date": "2024-06-15",
            "reason": "resignation",
            "notice_period": 30,
            "final_pay_calculation": True,
            "return_company_assets": True,
            "exit_interview_scheduled": True
        }
    """
    url = f"{ERP_API_BASE_URL}/employees/{employee_id}/terminate"
    try:
        resp = requests.post(url, headers=HEADERS, json=termination_data, timeout=15)
        resp.raise_for_status()
        return {"success": True, "data": resp.json()}
    except Exception as e:
        return {"success": False, "error": str(e)}

# ===== RECRUITMENT MANAGEMENT =====

def create_job_posting(job_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Tạo tin tuyển dụng.
    
    Args:
        job_data: {
            "title": "Senior Software Developer",
            "department": "IT",
            "location": "Ho Chi Minh City",
            "employment_type": "full_time",
            "description": "We are looking for...",
            "requirements": ["5+ years experience", "React, Node.js"],
            "salary_range": {"min": 20000000, "max": 35000000},
            "application_deadline": "2024-03-15",
            "hiring_manager": "EMP100",
            "positions_available": 2
        }
    """
    url = f"{ERP_API_BASE_URL}/recruitment/jobs"
    try:
        resp = requests.post(url, headers=HEADERS, json=job_data, timeout=15)
        resp.raise_for_status()
        return {"success": True, "data": resp.json()}
    except Exception as e:
        return {"success": False, "error": str(e)}

def submit_application(application_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Nộp đơn ứng tuyển.
    
    Args:
        application_data: {
            "job_id": "JOB001",
            "candidate_info": {
                "name": "Trần Thị B",
                "email": "tranthib@email.com",
                "phone": "0987654321",
                "resume_url": "https://...",
                "cover_letter": "Dear hiring manager..."
            },
            "source": "website"
        }
    """
    url = f"{ERP_API_BASE_URL}/recruitment/applications"
    try:
        resp = requests.post(url, headers=HEADERS, json=application_data, timeout=15)
        resp.raise_for_status()
        return {"success": True, "data": resp.json()}
    except Exception as e:
        return {"success": False, "error": str(e)}

def schedule_interview(interview_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Lên lịch phỏng vấn.
    
    Args:
        interview_data: {
            "application_id": "APP001",
            "interview_type": "technical",
            "date": "2024-02-20",
            "time": "14:00",
            "duration": 90,
            "interviewers": ["EMP100", "EMP101"],
            "location": "Meeting Room A",
            "notes": "Technical interview focusing on React"
        }
    """
    url = f"{ERP_API_BASE_URL}/recruitment/interviews"
    try:
        resp = requests.post(url, headers=HEADERS, json=interview_data, timeout=15)
        resp.raise_for_status()
        return {"success": True, "data": resp.json()}
    except Exception as e:
        return {"success": False, "error": str(e)}

def evaluate_candidate(evaluation_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Đánh giá ứng viên sau phỏng vấn.
    
    Args:
        evaluation_data: {
            "application_id": "APP001",
            "interview_id": "INT001",
            "evaluator_id": "EMP100",
            "scores": {
                "technical_skills": 8,
                "communication": 7,
                "cultural_fit": 9,
                "experience": 8
            },
            "overall_rating": "recommend",
            "feedback": "Strong technical skills...",
            "next_steps": "Proceed to final interview"
        }
    """
    url = f"{ERP_API_BASE_URL}/recruitment/evaluations"
    try:
        resp = requests.post(url, headers=HEADERS, json=evaluation_data, timeout=15)
        resp.raise_for_status()
        return {"success": True, "data": resp.json()}
    except Exception as e:
        return {"success": False, "error": str(e)}

# ===== PAYROLL MANAGEMENT =====

class CalculatePayrollInput(BaseModel):
    payroll_data: Dict[str, Any] = Field(description="The data for payroll calculation, including employee_id, pay_period, base_salary, overtime_hours, allowances, deductions, and bonus.")

class CalculatePayrollOutput(BaseModel):
    success: bool = Field(description="True if the payroll was calculated successfully, False otherwise.")
    data: Optional[Dict[str, Any]] = Field(None, description="The calculated payroll data if successful.")
    error: Optional[str] = Field(None, description="Error message if the operation failed.")

class CalculatePayrollTool:
    """Tính lương cho nhân viên."""
    input_schema = CalculatePayrollInput
    output_schema = CalculatePayrollOutput

    def run(self, payroll_data: Dict[str, Any]) -> CalculatePayrollOutput:
        url = f"{ERP_API_BASE_URL}/payroll/calculate"
        try:
            resp = requests.post(url, headers=HEADERS, json=payroll_data, timeout=15)
            resp.raise_for_status()
            return CalculatePayrollOutput(success=True, data=resp.json())
        except Exception as e:
            return CalculatePayrollOutput(success=False, error=str(e))

def generate_payslip(employee_id: str, pay_period: str) -> Dict[str, Any]:
    """Tạo phiếu lương."""
    url = f"{ERP_API_BASE_URL}/payroll/{employee_id}/payslip/{pay_period}"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        return {"success": True, "data": resp.json()}
    except Exception as e:
        return {"success": False, "error": str(e)}

def process_salary_adjustment(adjustment_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Xử lý điều chỉnh lương.
    
    Args:
        adjustment_data: {
            "employee_id": "EMP001",
            "adjustment_type": "promotion",
            "old_salary": 25000000,
            "new_salary": 30000000,
            "effective_date": "2024-02-01",
            "reason": "Performance-based promotion",
            "approved_by": "EMP100"
        }
    """
    url = f"{ERP_API_BASE_URL}/payroll/adjustments"
    try:
        resp = requests.post(url, headers=HEADERS, json=adjustment_data, timeout=15)
        resp.raise_for_status()
        return {"success": True, "data": resp.json()}
    except Exception as e:
        return {"success": False, "error": str(e)}

# ===== LEAVE MANAGEMENT =====

class SubmitLeaveRequestInput(BaseModel):
    leave_data: Dict[str, Any] = Field(description="The data for the leave request, including employee_id, leave_type, start_date, end_date, days_requested, reason, emergency_contact, and work_handover.")

class SubmitLeaveRequestOutput(BaseModel):
    success: bool = Field(description="True if the leave request was submitted successfully, False otherwise.")
    data: Optional[Dict[str, Any]] = Field(None, description="The submitted leave request data if successful.")
    error: Optional[str] = Field(None, description="Error message if the operation failed.")

class SubmitLeaveRequestTool:
    """Nộp đơn xin nghỉ phép."""
    input_schema = SubmitLeaveRequestInput
    output_schema = SubmitLeaveRequestOutput

    def run(self, leave_data: Dict[str, Any]) -> SubmitLeaveRequestOutput:
        url = f"{ERP_API_BASE_URL}/leave/requests"
        try:
            resp = requests.post(url, headers=HEADERS, json=leave_data, timeout=15)
            resp.raise_for_status()
            return SubmitLeaveRequestOutput(success=True, data=resp.json())
        except Exception as e:
            return SubmitLeaveRequestOutput(success=False, error=str(e))

def approve_leave_request(request_id: str, approval_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Phê duyệt đơn xin nghỉ phép.
    
    Args:
        approval_data: {
            "approved_by": "EMP100",
            "status": "approved",
            "approved_days": 5,
            "comments": "Approved as requested",
            "approval_date": "2024-02-15"
        }
    """
    url = f"{ERP_API_BASE_URL}/leave/requests/{request_id}/approve"
    try:
        resp = requests.put(url, headers=HEADERS, json=approval_data, timeout=15)
        resp.raise_for_status()
        return {"success": True, "data": resp.json()}
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_leave_balance(employee_id: str) -> Dict[str, Any]:
    """Kiểm tra số ngày phép còn lại."""
    url = f"{ERP_API_BASE_URL}/leave/{employee_id}/balance"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        return {"success": True, "data": resp.json()}
    except Exception as e:
        return {"success": False, "error": str(e)}

# ===== PERFORMANCE MANAGEMENT =====

class CreatePerformanceGoalInput(BaseModel):
    goal_data: Dict[str, Any] = Field(description="The data for the new performance goal, including employee_id, goal_period, goals (list of title, description, weight, deadline, success_criteria), and set_by.")

class CreatePerformanceGoalOutput(BaseModel):
    success: bool = Field(description="True if the performance goal was created successfully, False otherwise.")
    data: Optional[Dict[str, Any]] = Field(None, description="The created performance goal data if successful.")
    error: Optional[str] = Field(None, description="Error message if the operation failed.")

class CreatePerformanceGoalTool:
    """Tạo mục tiêu hiệu suất."""
    input_schema = CreatePerformanceGoalInput
    output_schema = CreatePerformanceGoalOutput

    def run(self, goal_data: Dict[str, Any]) -> CreatePerformanceGoalOutput:
        url = f"{ERP_API_BASE_URL}/performance/goals"
        try:
            resp = requests.post(url, headers=HEADERS, json=goal_data, timeout=15)
            resp.raise_for_status()
            return CreatePerformanceGoalOutput(success=True, data=resp.json())
        except Exception as e:
            return CreatePerformanceGoalOutput(success=False, error=str(e))

def conduct_performance_review(review_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Thực hiện đánh giá hiệu suất.
    
    Args:
        review_data: {
            "employee_id": "EMP001",
            "review_period": "2024-Q1",
            "reviewer_id": "EMP100",
            "self_assessment": {
                "achievements": "Completed all assigned projects",
                "challenges": "Limited resources for project Y",
                "goals_met": 85
            },
            "manager_assessment": {
                "overall_rating": "exceeds_expectations",
                "strengths": ["Technical skills", "Team collaboration"],
                "areas_for_improvement": ["Time management"],
                "development_plan": "Attend project management training"
            },
            "goals_evaluation": [
                {
                    "goal_id": "GOAL001",
                    "achievement_rate": 100,
                    "rating": "outstanding"
                }
            ]
        }
    """
    url = f"{ERP_API_BASE_URL}/performance/reviews"
    try:
        resp = requests.post(url, headers=HEADERS, json=review_data, timeout=15)
        resp.raise_for_status()
        return {"success": True, "data": resp.json()}
    except Exception as e:
        return {"success": False, "error": str(e)}

def track_performance_metrics(employee_id: str, date_range: Dict[str, str]) -> Dict[str, Any]:
    """Theo dõi các chỉ số hiệu suất."""
    url = f"{ERP_API_BASE_URL}/performance/{employee_id}/metrics"
    try:
        resp = requests.get(url, headers=HEADERS, params=date_range, timeout=10)
        resp.raise_for_status()
        return {"success": True, "data": resp.json()}
    except Exception as e:
        return {"success": False, "error": str(e)}

# ===== TRAINING & DEVELOPMENT =====

def create_training_program(program_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Tạo chương trình đào tạo.
    
    Args:
        program_data: {
            "name": "Leadership Development Program",
            "description": "Develop leadership skills for managers",
            "duration": "5 days",
            "instructor": "External Trainer",
            "capacity": 20,
            "start_date": "2024-03-01",
            "end_date": "2024-03-05",
            "location": "Training Room A",
            "cost_per_participant": 5000000,
            "target_audience": ["managers", "senior_staff"],
            "prerequisites": "3+ years management experience"
        }
    """
    url = f"{ERP_API_BASE_URL}/training/programs"
    try:
        resp = requests.post(url, headers=HEADERS, json=program_data, timeout=15)
        resp.raise_for_status()
        return {"success": True, "data": resp.json()}
    except Exception as e:
        return {"success": False, "error": str(e)}

def enroll_employee_training(enrollment_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Đăng ký nhân viên tham gia đào tạo.
    
    Args:
        enrollment_data: {
            "program_id": "TRN001",
            "employee_id": "EMP001",
            "enrolled_by": "EMP100",
            "enrollment_date": "2024-02-15",
            "cost_center": "IT Department",
            "manager_approval": True
        }
    """
    url = f"{ERP_API_BASE_URL}/training/enrollments"
    try:
        resp = requests.post(url, headers=HEADERS, json=enrollment_data, timeout=15)
        resp.raise_for_status()
        return {"success": True, "data": resp.json()}
    except Exception as e:
        return {"success": False, "error": str(e)}

def track_training_completion(completion_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Theo dõi hoàn thành đào tạo.
    
    Args:
        completion_data: {
            "enrollment_id": "ENR001",
            "completion_date": "2024-03-05",
            "final_score": 85,
            "certification_earned": True,
            "feedback": "Very informative and practical",
            "trainer_rating": 4.5
        }
    """
    url = f"{ERP_API_BASE_URL}/training/completions"
    try:
        resp = requests.post(url, headers=HEADERS, json=completion_data, timeout=15)
        resp.raise_for_status()
        return {"success": True, "data": resp.json()}
    except Exception as e:
        return {"success": False, "error": str(e)}

# ===== ATTENDANCE & TIME TRACKING =====

def record_attendance(attendance_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Ghi nhận chấm công.
    
    Args:
        attendance_data: {
            "employee_id": "EMP001",
            "date": "2024-02-15",
            "check_in": "08:00:00",
            "check_out": "17:30:00",
            "break_time": 60,
            "location": "HCM Office",
            "work_type": "office"
        }
    """
    url = f"{ERP_API_BASE_URL}/attendance/records"
    try:
        resp = requests.post(url, headers=HEADERS, json=attendance_data, timeout=15)
        resp.raise_for_status()
        return {"success": True, "data": resp.json()}
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_attendance_report(employee_id: str, date_range: Dict[str, str]) -> Dict[str, Any]:
    """Lấy báo cáo chấm công."""
    url = f"{ERP_API_BASE_URL}/attendance/{employee_id}/report"
    try:
        resp = requests.get(url, headers=HEADERS, params=date_range, timeout=10)
        resp.raise_for_status()
        return {"success": True, "data": resp.json()}
    except Exception as e:
        return {"success": False, "error": str(e)}

def calculate_overtime(employee_id: str, date_range: Dict[str, str]) -> Dict[str, Any]:
    """Tính giờ làm thêm."""
    url = f"{ERP_API_BASE_URL}/attendance/{employee_id}/overtime"
    try:
        resp = requests.get(url, headers=HEADERS, params=date_range, timeout=10)
        resp.raise_for_status()
        return {"success": True, "data": resp.json()}
    except Exception as e:
        return {"success": False, "error": str(e)}

# ===== HR ANALYTICS & REPORTING =====

def generate_hr_dashboard() -> Dict[str, Any]:
    """Tạo dashboard HR tổng quan."""
    url = f"{ERP_API_BASE_URL}/hr/dashboard"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        return {"success": True, "data": resp.json()}
    except Exception as e:
        return {"success": False, "error": str(e)}

def calculate_turnover_rate(date_range: Dict[str, str]) -> Dict[str, Any]:
    """Tính tỷ lệ nghỉ việc."""
    url = f"{ERP_API_BASE_URL}/hr/analytics/turnover"
    try:
        resp = requests.get(url, headers=HEADERS, params=date_range, timeout=10)
        resp.raise_for_status()
        return {"success": True, "data": resp.json()}
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_headcount_analysis(breakdown_by: str = "department") -> Dict[str, Any]:
    """Phân tích nhân sự theo bộ phận/vị trí."""
    url = f"{ERP_API_BASE_URL}/hr/analytics/headcount"
    params = {"breakdown_by": breakdown_by}
    try:
        resp = requests.get(url, headers=HEADERS, params=params, timeout=10)
        resp.raise_for_status()
        return {"success": True, "data": resp.json()}
    except Exception as e:
        return {"success": False, "error": str(e)}

def generate_compliance_report(report_type: str) -> Dict[str, Any]:
    """
    Tạo báo cáo tuân thủ.
    
    Args:
        report_type: "labor_law", "tax", "social_insurance", "safety"
    """
    url = f"{ERP_API_BASE_URL}/hr/compliance/{report_type}"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        return {"success": True, "data": resp.json()}
    except Exception as e:
        return {"success": False, "error": str(e)}