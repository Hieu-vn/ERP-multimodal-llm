"""
Project Management Agent for ERP AI Pro Version
Handles comprehensive project management operations including tasks, milestones, resources, and reporting.
"""

import os
import requests
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from enum import Enum
from pydantic import BaseModel, Field

# Configuration
ERP_API_BASE_URL = os.getenv("ERP_API_BASE_URL", "http://localhost:9000/api")
ERP_API_TOKEN = os.getenv("ERP_API_TOKEN", "demo-token")

HEADERS = {
    "Authorization": f"Bearer {ERP_API_TOKEN}",
    "Content-Type": "application/json"
}

class ProjectStatus(Enum):
    PLANNING = "planning"
    ACTIVE = "active"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class TaskStatus(Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    COMPLETED = "completed"
    BLOCKED = "blocked"

class Priority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

# ===== PROJECT MANAGEMENT FUNCTIONS =====

# Định nghĩa Input và Output Schema cho CreateProjectTool
class CreateProjectInput(BaseModel):
    project_data: Dict[str, Any] = Field(description="The data for the new project, including name, description, dates, budget, manager_id, team_members, priority, and client_id.")

class CreateProjectOutput(BaseModel):
    success: bool = Field(description="True if the project was created successfully, False otherwise.")
    data: Optional[Dict[str, Any]] = Field(None, description="The created project data if successful.")
    error: Optional[str] = Field(None, description="Error message if the operation failed.")

class CreateProjectTool:
    """Tạo dự án mới với đầy đủ thông tin."""
    input_schema = CreateProjectInput
    output_schema = CreateProjectOutput

    def run(self, project_data: Dict[str, Any]) -> CreateProjectOutput:
        url = f"{ERP_API_BASE_URL}/projects"
        try:
            resp = requests.post(url, headers=HEADERS, json=project_data, timeout=15)
            resp.raise_for_status()
            return CreateProjectOutput(success=True, data=resp.json())
        except Exception as e:
            return CreateProjectOutput(success=False, error=str(e))

class GetProjectDetailsInput(BaseModel):
    project_id: str = Field(description="The ID of the project to get details for.")

class GetProjectDetailsOutput(BaseModel):
    success: bool = Field(description="True if the operation was successful, False otherwise.")
    data: Optional[Dict[str, Any]] = Field(None, description="The project details data if successful.")
    error: Optional[str] = Field(None, description="Error message if the operation failed.")

class GetProjectDetailsTool:
    """Lấy chi tiết dự án theo ID."""
    input_schema = GetProjectDetailsInput
    output_schema = GetProjectDetailsOutput

    def run(self, project_id: str) -> GetProjectDetailsOutput:
        url = f"{ERP_API_BASE_URL}/projects/{project_id}"
        try:
            resp = requests.get(url, headers=HEADERS, timeout=10)
            resp.raise_for_status()
            return GetProjectDetailsOutput(success=True, data=resp.json())
        except Exception as e:
            return GetProjectDetailsOutput(success=False, error=str(e))

class UpdateProjectStatusInput(BaseModel):
    project_id: str = Field(description="The ID of the project to update.")
    status: str = Field(description="The new status of the project (e.g., 'active', 'completed').")
    notes: str = Field(default="", description="Optional notes about the status update.")

class UpdateProjectStatusOutput(BaseModel):
    success: bool = Field(description="True if the operation was successful, False otherwise.")
    data: Optional[Dict[str, Any]] = Field(None, description="The updated project data if successful.")
    error: Optional[str] = Field(None, description="Error message if the operation failed.")

class UpdateProjectStatusTool:
    """Cập nhật trạng thái dự án."""
    input_schema = UpdateProjectStatusInput
    output_schema = UpdateProjectStatusOutput

    def run(self, project_id: str, status: str, notes: str = "") -> UpdateProjectStatusOutput:
        url = f"{ERP_API_BASE_URL}/projects/{project_id}/status"
        data = {"status": status, "notes": notes, "updated_at": datetime.now().isoformat()}
        try:
            resp = requests.put(url, headers=HEADERS, json=data, timeout=15)
            resp.raise_for_status()
            return UpdateProjectStatusOutput(success=True, data=resp.json())
        except Exception as e:
            return UpdateProjectStatusOutput(success=False, error=str(e))

def get_project_timeline(project_id: str) -> Dict[str, Any]:
    """Lấy timeline và milestone của dự án."""
    url = f"{ERP_API_BASE_URL}/projects/{project_id}/timeline"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        return {"success": True, "data": resp.json()}
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_project_budget_tracking(project_id: str) -> Dict[str, Any]:
    """Theo dõi ngân sách dự án."""
    url = f"{ERP_API_BASE_URL}/projects/{project_id}/budget"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        return {"success": True, "data": resp.json()}
    except Exception as e:
        return {"success": False, "error": str(e)}

# ===== TASK MANAGEMENT FUNCTIONS =====

class CreateTaskInput(BaseModel):
    task_data: Dict[str, Any] = Field(description="The data for the new task, including project_id, title, description, assignee_id, priority, due_date, estimated_hours, dependencies, and tags.")

class CreateTaskOutput(BaseModel):
    success: bool = Field(description="True if the task was created successfully, False otherwise.")
    data: Optional[Dict[str, Any]] = Field(None, description="The created task data if successful.")
    error: Optional[str] = Field(None, description="Error message if the operation failed.")

class CreateTaskTool:
    """Tạo công việc mới trong dự án."""
    input_schema = CreateTaskInput
    output_schema = CreateTaskOutput

    def run(self, task_data: Dict[str, Any]) -> CreateTaskOutput:
        url = f"{ERP_API_BASE_URL}/tasks"
        try:
            resp = requests.post(url, headers=HEADERS, json=task_data, timeout=15)
            resp.raise_for_status()
            return CreateTaskOutput(success=True, data=resp.json())
        except Exception as e:
            return CreateTaskOutput(success=False, error=str(e))

def update_task_status(task_id: str, status: str, progress: int = 0) -> Dict[str, Any]:
    """Cập nhật trạng thái và tiến độ công việc."""
    url = f"{ERP_API_BASE_URL}/tasks/{task_id}/status"
    data = {
        "status": status,
        "progress": progress,
        "updated_at": datetime.now().isoformat()
    }
    try:
        resp = requests.put(url, headers=HEADERS, json=data, timeout=15)
        resp.raise_for_status()
        return {"success": True, "data": resp.json()}
    except Exception as e:
        return {"success": False, "error": str(e)}

class AssignTaskInput(BaseModel):
    task_id: str = Field(description="The ID of the task to assign.")
    assignee_id: str = Field(description="The ID of the employee to assign the task to.")
    notes: str = Field(default="", description="Optional notes about the assignment.")

class AssignTaskOutput(BaseModel):
    success: bool = Field(description="True if the task was assigned successfully, False otherwise.")
    data: Optional[Dict[str, Any]] = Field(None, description="The updated task data if successful.")
    error: Optional[str] = Field(None, description="Error message if the operation failed.")

class AssignTaskTool:
    """Gán công việc cho nhân viên."""
    input_schema = AssignTaskInput
    output_schema = AssignTaskOutput

    def run(self, task_id: str, assignee_id: str, notes: str = "") -> AssignTaskOutput:
        url = f"{ERP_API_BASE_URL}/tasks/{task_id}/assign"
        data = {
            "assignee_id": assignee_id,
            "notes": notes,
            "assigned_at": datetime.now().isoformat()
        }
        try:
            resp = requests.put(url, headers=HEADERS, json=data, timeout=15)
            resp.raise_for_status()
            return AssignTaskOutput(success=True, data=resp.json())
        except Exception as e:
            return AssignTaskOutput(success=False, error=str(e))

def get_task_dependencies(task_id: str) -> Dict[str, Any]:
    """Lấy danh sách dependencies của task."""
    url = f"{ERP_API_BASE_URL}/tasks/{task_id}/dependencies"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        return {"success": True, "data": resp.json()}
    except Exception as e:
        return {"success": False, "error": str(e)}

def log_time_entry(task_id: str, employee_id: str, hours: float, description: str) -> Dict[str, Any]:
    """Ghi nhận thời gian làm việc cho task."""
    url = f"{ERP_API_BASE_URL}/tasks/{task_id}/time-entries"
    data = {
        "employee_id": employee_id,
        "hours": hours,
        "description": description,
        "date": datetime.now().isoformat(),
    }
    try:
        resp = requests.post(url, headers=HEADERS, json=data, timeout=15)
        resp.raise_for_status()
        return {"success": True, "data": resp.json()}
    except Exception as e:
        return {"success": False, "error": str(e)}

# ===== MILESTONE MANAGEMENT =====

def create_milestone(milestone_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Tạo milestone cho dự án.
    
    Args:
        milestone_data: {
            "project_id": "PROJ001",
            "title": "MVP Release",
            "description": "Phát hành phiên bản MVP",
            "due_date": "2024-03-15",
            "criteria": ["Complete core features", "Pass QA testing"],
            "weight": 25  # % of project completion
        }
    """
    url = f"{ERP_API_BASE_URL}/milestones"
    try:
        resp = requests.post(url, headers=HEADERS, json=milestone_data, timeout=15)
        resp.raise_for_status()
        return {"success": True, "data": resp.json()}
    except Exception as e:
        return {"success": False, "error": str(e)}

def complete_milestone(milestone_id: str, completion_notes: str) -> Dict[str, Any]:
    """Đánh dấu milestone hoàn thành."""
    url = f"{ERP_API_BASE_URL}/milestones/{milestone_id}/complete"
    data = {
        "completion_notes": completion_notes,
        "completed_at": datetime.now().isoformat()
    }
    try:
        resp = requests.put(url, headers=HEADERS, json=data, timeout=15)
        resp.raise_for_status()
        return {"success": True, "data": resp.json()}
    except Exception as e:
        return {"success": False, "error": str(e)}

# ===== RESOURCE MANAGEMENT =====

def allocate_resources(allocation_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Phân bổ tài nguyên cho dự án.
    
    Args:
        allocation_data: {
            "project_id": "PROJ001",
            "resource_type": "human|equipment|material",
            "resource_id": "EMP001",
            "allocation_percentage": 80,
            "start_date": "2024-01-15",
            "end_date": "2024-03-15"
        }
    """
    url = f"{ERP_API_BASE_URL}/projects/resources/allocate"
    try:
        resp = requests.post(url, headers=HEADERS, json=allocation_data, timeout=15)
        resp.raise_for_status()
        return {"success": True, "data": resp.json()}
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_resource_utilization(resource_id: str, date_range: Dict[str, str]) -> Dict[str, Any]:
    """Kiểm tra mức độ sử dụng tài nguyên."""
    url = f"{ERP_API_BASE_URL}/resources/{resource_id}/utilization"
    try:
        resp = requests.get(url, headers=HEADERS, params=date_range, timeout=10)
        resp.raise_for_status()
        return {"success": True, "data": resp.json()}
    except Exception as e:
        return {"success": False, "error": str(e)}

def check_resource_conflicts(project_id: str) -> Dict[str, Any]:
    """Kiểm tra xung đột tài nguyên trong dự án."""
    url = f"{ERP_API_BASE_URL}/projects/{project_id}/resource-conflicts"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        return {"success": True, "data": resp.json()}
    except Exception as e:
        return {"success": False, "error": str(e)}

# ===== REPORTING & ANALYTICS =====

def generate_project_report(project_id: str, report_type: str) -> Dict[str, Any]:
    """
    Tạo báo cáo dự án.
    
    Args:
        report_type: "progress|budget|timeline|resource|risk"
    """
    url = f"{ERP_API_BASE_URL}/projects/{project_id}/reports/{report_type}"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        return {"success": True, "data": resp.json()}
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_project_kpis(project_id: str) -> Dict[str, Any]:
    """Lấy các KPIs của dự án."""
    url = f"{ERP_API_BASE_URL}/projects/{project_id}/kpis"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        return {"success": True, "data": resp.json()}
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_team_productivity(team_id: str, date_range: Dict[str, str]) -> Dict[str, Any]:
    """Phân tích năng suất team."""
    url = f"{ERP_API_BASE_URL}/teams/{team_id}/productivity"
    try:
        resp = requests.get(url, headers=HEADERS, params=date_range, timeout=10)
        resp.raise_for_status()
        return {"success": True, "data": resp.json()}
    except Exception as e:
        return {"success": False, "error": str(e)}

# ===== RISK MANAGEMENT =====

def create_risk_assessment(risk_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Tạo đánh giá rủi ro cho dự án.
    
    Args:
        risk_data: {
            "project_id": "PROJ001",
            "risk_type": "technical|financial|resource|timeline",
            "description": "Delay in API development",
            "probability": "medium",
            "impact": "high",
            "mitigation_plan": "Allocate additional developers"
        }
    """
    url = f"{ERP_API_BASE_URL}/projects/risks"
    try:
        resp = requests.post(url, headers=HEADERS, json=risk_data, timeout=15)
        resp.raise_for_status()
        return {"success": True, "data": resp.json()}
    except Exception as e:
        return {"success": False, "error": str(e)}

def update_risk_status(risk_id: str, status: str, notes: str) -> Dict[str, Any]:
    """Cập nhật trạng thái rủi ro."""
    url = f"{ERP_API_BASE_URL}/risks/{risk_id}/status"
    data = {
        "status": status,
        "notes": notes,
        "updated_at": datetime.now().isoformat()
    }
    try:
        resp = requests.put(url, headers=HEADERS, json=data, timeout=15)
        resp.raise_for_status()
        return {"success": True, "data": resp.json()}
    except Exception as e:
        return {"success": False, "error": str(e)}

# ===== COLLABORATION FUNCTIONS =====

def add_project_comment(project_id: str, comment_data: Dict[str, Any]) -> Dict[str, Any]:
    """Thêm comment vào dự án."""
    url = f"{ERP_API_BASE_URL}/projects/{project_id}/comments"
    try:
        resp = requests.post(url, headers=HEADERS, json=comment_data, timeout=15)
        resp.raise_for_status()
        return {"success": True, "data": resp.json()}
    except Exception as e:
        return {"success": False, "error": str(e)}

def create_project_meeting(meeting_data: Dict[str, Any]) -> Dict[str, Any]:
    """Tạo cuộc họp dự án."""
    url = f"{ERP_API_BASE_URL}/projects/meetings"
    try:
        resp = requests.post(url, headers=HEADERS, json=meeting_data, timeout=15)
        resp.raise_for_status()
        return {"success": True, "data": resp.json()}
    except Exception as e:
        return {"success": False, "error": str(e)}

def share_project_document(project_id: str, document_data: Dict[str, Any]) -> Dict[str, Any]:
    """Chia sẻ tài liệu dự án."""
    url = f"{ERP_API_BASE_URL}/projects/{project_id}/documents"
    try:
        resp = requests.post(url, headers=HEADERS, json=document_data, timeout=15)
        resp.raise_for_status()
        return {"success": True, "data": resp.json()}
    except Exception as e:
        return {"success": False, "error": str(e)}