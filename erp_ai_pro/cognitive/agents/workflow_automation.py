"""
Workflow Automation Agent for ERP AI Pro Version
Handles business process automation, workflow triggers, and task orchestration.
Supports onboarding, approvals, notifications, and back-office operations.
"""

import os
import json
import asyncio
import requests
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from enum import Enum
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configuration
ERP_API_BASE_URL = os.getenv("ERP_API_BASE_URL", "http://localhost:9000/api")
ERP_API_TOKEN = os.getenv("ERP_API_TOKEN", "demo-token")
NOTIFICATION_EMAIL = os.getenv("NOTIFICATION_EMAIL", "notifications@company.com")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))

HEADERS = {
    "Authorization": f"Bearer {ERP_API_TOKEN}",
    "Content-Type": "application/json"
}

class WorkflowStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    WAITING_APPROVAL = "waiting_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"
    FAILED = "failed"

class TriggerType(Enum):
    SCHEDULE = "schedule"
    EVENT = "event"
    API_CALL = "api_call"
    USER_ACTION = "user_action"
    CONDITIONAL = "conditional"

# ===== WORKFLOW CORE FUNCTIONS =====

class WorkflowEngine:
    """Core workflow automation engine."""
    
    def __init__(self):
        self.workflows = {}
        self.active_instances = {}
        self.triggers = {}
    
    def register_workflow(self, workflow_id: str, workflow_config: Dict[str, Any]) -> bool:
        """Đăng ký workflow mới vào hệ thống."""
        try:
            self.workflows[workflow_id] = {
                "config": workflow_config,
                "created_at": datetime.now().isoformat(),
                "status": "active"
            }
            return True
        except Exception as e:
            print(f"Error registering workflow {workflow_id}: {e}")
            return False
    
    async def execute_workflow(self, workflow_id: str, trigger_data: Dict[str, Any]) -> Dict[str, Any]:
        """Thực thi workflow với dữ liệu trigger."""
        if workflow_id not in self.workflows:
            return {"success": False, "error": "Workflow not found"}
        
        instance_id = f"{workflow_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        workflow_config = self.workflows[workflow_id]["config"]
        
        try:
            # Initialize workflow instance
            self.active_instances[instance_id] = {
                "workflow_id": workflow_id,
                "status": WorkflowStatus.IN_PROGRESS.value,
                "start_time": datetime.now().isoformat(),
                "trigger_data": trigger_data,
                "current_step": 0,
                "execution_log": []
            }
            
            # Execute workflow steps
            result = await self._execute_steps(instance_id, workflow_config["steps"])
            
            # Update final status
            self.active_instances[instance_id]["status"] = (
                WorkflowStatus.COMPLETED.value if result["success"] 
                else WorkflowStatus.FAILED.value
            )
            self.active_instances[instance_id]["end_time"] = datetime.now().isoformat()
            
            return {"success": True, "instance_id": instance_id, "result": result}
            
        except Exception as e:
            if instance_id in self.active_instances:
                self.active_instances[instance_id]["status"] = WorkflowStatus.FAILED.value
                self.active_instances[instance_id]["error"] = str(e)
            return {"success": False, "error": str(e)}
    
    async def _execute_steps(self, instance_id: str, steps: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Thực thi các bước trong workflow."""
        results = []
        context = self.active_instances[instance_id]["trigger_data"].copy()
        
        for i, step in enumerate(steps):
            self.active_instances[instance_id]["current_step"] = i
            
            try:
                # Execute step based on type
                step_result = await self._execute_step(step, context)
                results.append(step_result)
                
                # Update context with step results
                if "output" in step_result:
                    context.update(step_result["output"])
                
                # Log execution
                self.active_instances[instance_id]["execution_log"].append({
                    "step": i,
                    "name": step.get("name", f"Step {i}"),
                    "result": step_result,
                    "timestamp": datetime.now().isoformat()
                })
                
                # Check for errors
                if not step_result.get("success", False):
                    return {"success": False, "error": step_result.get("error"), "results": results}
                
                # Handle conditional logic
                if step.get("type") == "condition" and not step_result.get("condition_met", False):
                    break
                    
            except Exception as e:
                return {"success": False, "error": f"Step {i} failed: {str(e)}", "results": results}
        
        return {"success": True, "results": results, "context": context}
    
    async def _execute_step(self, step: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Thực thi một bước cụ thể trong workflow."""
        step_type = step.get("type")
        step_config = step.get("config", {})
        
        if step_type == "api_call":
            return await self._execute_api_call(step_config, context)
        elif step_type == "email":
            return await self._send_email(step_config, context)
        elif step_type == "approval":
            return await self._request_approval(step_config, context)
        elif step_type == "data_transform":
            return await self._transform_data(step_config, context)
        elif step_type == "condition":
            return await self._evaluate_condition(step_config, context)
        elif step_type == "delay":
            return await self._execute_delay(step_config, context)
        elif step_type == "notification":
            return await self._send_notification(step_config, context)
        else:
            return {"success": False, "error": f"Unknown step type: {step_type}"}

# ===== STEP EXECUTION FUNCTIONS =====

    async def _execute_api_call(self, config: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Thực hiện API call."""
        try:
            url = config["url"].format(**context)
            method = config.get("method", "GET").upper()
            headers = config.get("headers", {})
            data = config.get("data", {})
            
            if method == "GET":
                response = requests.get(url, headers=headers, timeout=30)
            elif method == "POST":
                response = requests.post(url, headers=headers, json=data, timeout=30)
            elif method == "PUT":
                response = requests.put(url, headers=headers, json=data, timeout=30)
            elif method == "DELETE":
                response = requests.delete(url, headers=headers, timeout=30)
            else:
                return {"success": False, "error": f"Unsupported HTTP method: {method}"}
            
            response.raise_for_status()
            return {
                "success": True,
                "output": {"api_response": response.json() if response.text else None}
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _send_email(self, config: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Gửi email notification."""
        try:
            to_email = config["to"].format(**context)
            subject = config["subject"].format(**context)
            body = config["body"].format(**context)
            
            msg = MIMEMultipart()
            msg['From'] = NOTIFICATION_EMAIL
            msg['To'] = to_email
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'html'))
            
            # Note: In production, implement proper SMTP authentication
            # server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            # server.starttls()
            # server.login(email_user, email_password)
            # server.send_message(msg)
            # server.quit()
            
            print(f"Email sent to {to_email}: {subject}")
            return {"success": True, "output": {"email_sent": to_email}}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _request_approval(self, config: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Yêu cầu phê duyệt từ người có thẩm quyền."""
        try:
            approver_id = config["approver_id"]
            approval_data = {
                "type": config.get("type", "general"),
                "description": config["description"].format(**context),
                "data": context,
                "requested_at": datetime.now().isoformat(),
                "status": "pending"
            }
            
            # Submit approval request
            url = f"{ERP_API_BASE_URL}/approvals"
            response = requests.post(url, headers=HEADERS, json=approval_data, timeout=15)
            response.raise_for_status()
            
            approval_id = response.json().get("approval_id")
            
            # Send notification to approver
            await self._send_approval_notification(approver_id, approval_id, approval_data)
            
            return {
                "success": True,
                "output": {"approval_id": approval_id, "status": "waiting_approval"}
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _transform_data(self, config: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Biến đổi dữ liệu theo rules được định nghĩa."""
        try:
            transformations = config.get("rules", [])
            result = context.copy()
            
            for rule in transformations:
                rule_type = rule["type"]
                
                if rule_type == "map":
                    source_field = rule["source"]
                    target_field = rule["target"]
                    if source_field in result:
                        result[target_field] = result[source_field]
                
                elif rule_type == "calculate":
                    target_field = rule["target"]
                    expression = rule["expression"]
                    # Safe evaluation (in production, use a proper expression evaluator)
                    try:
                        result[target_field] = eval(expression, {"__builtins__": {}}, result)
                    except:
                        pass
                
                elif rule_type == "format":
                    target_field = rule["target"]
                    template = rule["template"]
                    result[target_field] = template.format(**result)
            
            return {"success": True, "output": result}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _evaluate_condition(self, config: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Đánh giá điều kiện logic."""
        try:
            condition = config["condition"]
            # Safe evaluation (in production, use a proper condition evaluator)
            condition_met = eval(condition, {"__builtins__": {}}, context)
            
            return {
                "success": True,
                "condition_met": condition_met,
                "output": {"condition_result": condition_met}
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _execute_delay(self, config: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Thực hiện delay trong workflow."""
        try:
            delay_seconds = config.get("seconds", 0)
            delay_minutes = config.get("minutes", 0)
            delay_hours = config.get("hours", 0)
            
            total_delay = delay_seconds + (delay_minutes * 60) + (delay_hours * 3600)
            
            if total_delay > 0:
                await asyncio.sleep(total_delay)
            
            return {"success": True, "output": {"delayed_seconds": total_delay}}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _send_notification(self, config: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Gửi notification đến user hoặc system."""
        try:
            notification_type = config.get("type", "email")
            recipients = config.get("recipients", [])
            message = config["message"].format(**context)
            
            if notification_type == "email":
                for recipient in recipients:
                    await self._send_email({
                        "to": recipient,
                        "subject": config.get("subject", "Notification"),
                        "body": message
                    }, context)
            
            elif notification_type == "system":
                # Send system notification
                notification_data = {
                    "type": "system",
                    "message": message,
                    "recipients": recipients,
                    "timestamp": datetime.now().isoformat()
                }
                
                url = f"{ERP_API_BASE_URL}/notifications"
                requests.post(url, headers=HEADERS, json=notification_data, timeout=15)
            
            return {"success": True, "output": {"notification_sent": len(recipients)}}
            
        except Exception as e:
            return {"success": False, "error": str(e)}

# ===== PREDEFINED WORKFLOWS =====

# Global workflow engine instance
workflow_engine = WorkflowEngine()

def setup_default_workflows():
    """Thiết lập các workflows mặc định."""
    
    # Employee Onboarding Workflow
    onboarding_workflow = {
        "name": "Employee Onboarding",
        "description": "Automated new employee onboarding process",
        "trigger": {"type": "event", "event": "employee_hired"},
        "steps": [
            {
                "name": "Create Employee Record",
                "type": "api_call",
                "config": {
                    "url": f"{ERP_API_BASE_URL}/employees",
                    "method": "POST",
                    "data": {
                        "name": "{employee_name}",
                        "email": "{employee_email}",
                        "department": "{department}",
                        "position": "{position}",
                        "start_date": "{start_date}"
                    }
                }
            },
            {
                "name": "Send Welcome Email",
                "type": "email",
                "config": {
                    "to": "{employee_email}",
                    "subject": "Welcome to {company_name}!",
                    "body": """
                    <h2>Welcome {employee_name}!</h2>
                    <p>We're excited to have you join our team.</p>
                    <p>Your first day is {start_date}.</p>
                    <p>Please contact HR if you have any questions.</p>
                    """
                }
            },
            {
                "name": "Create IT Account",
                "type": "api_call",
                "config": {
                    "url": f"{ERP_API_BASE_URL}/it/accounts",
                    "method": "POST",
                    "data": {
                        "employee_id": "{employee_id}",
                        "email": "{employee_email}",
                        "department": "{department}"
                    }
                }
            },
            {
                "name": "Schedule Orientation",
                "type": "api_call",
                "config": {
                    "url": f"{ERP_API_BASE_URL}/events",
                    "method": "POST",
                    "data": {
                        "type": "orientation",
                        "employee_id": "{employee_id}",
                        "date": "{start_date}",
                        "duration": 4
                    }
                }
            }
        ]
    }
    
    # Expense Approval Workflow
    expense_approval_workflow = {
        "name": "Expense Approval",
        "description": "Automated expense report approval process",
        "trigger": {"type": "event", "event": "expense_submitted"},
        "steps": [
            {
                "name": "Validate Expense Amount",
                "type": "condition",
                "config": {
                    "condition": "amount <= 1000"
                }
            },
            {
                "name": "Auto Approve Small Expenses",
                "type": "api_call",
                "config": {
                    "url": f"{ERP_API_BASE_URL}/expenses/{'{expense_id}'}/approve",
                    "method": "PUT",
                    "data": {"auto_approved": True}
                }
            },
            {
                "name": "Request Manager Approval",
                "type": "approval",
                "config": {
                    "approver_id": "{manager_id}",
                    "type": "expense_approval",
                    "description": "Expense report approval needed for {employee_name}: ${amount}"
                }
            }
        ]
    }
    
    # Purchase Order Workflow
    purchase_order_workflow = {
        "name": "Purchase Order Processing",
        "description": "Automated purchase order processing and approval",
        "trigger": {"type": "event", "event": "purchase_order_created"},
        "steps": [
            {
                "name": "Check Budget Availability",
                "type": "api_call",
                "config": {
                    "url": f"{ERP_API_BASE_URL}/budgets/check",
                    "method": "POST",
                    "data": {
                        "department": "{department}",
                        "amount": "{total_amount}",
                        "category": "{category}"
                    }
                }
            },
            {
                "name": "Request Approval if Over Limit",
                "type": "condition",
                "config": {
                    "condition": "total_amount > 5000"
                }
            },
            {
                "name": "Get Department Head Approval",
                "type": "approval",
                "config": {
                    "approver_id": "{department_head_id}",
                    "type": "purchase_approval",
                    "description": "Purchase order approval needed: ${total_amount}"
                }
            },
            {
                "name": "Send to Vendor",
                "type": "email",
                "config": {
                    "to": "{vendor_email}",
                    "subject": "Purchase Order #{po_number}",
                    "body": "Please find attached purchase order #{po_number} for ${total_amount}."
                }
            },
            {
                "name": "Update Inventory Expectations",
                "type": "api_call",
                "config": {
                    "url": f"{ERP_API_BASE_URL}/inventory/expected",
                    "method": "POST",
                    "data": {
                        "po_number": "{po_number}",
                        "items": "{items}",
                        "expected_date": "{delivery_date}"
                    }
                }
            }
        ]
    }
    
    # Register workflows
    workflow_engine.register_workflow("employee_onboarding", onboarding_workflow)
    workflow_engine.register_workflow("expense_approval", expense_approval_workflow)
    workflow_engine.register_workflow("purchase_order", purchase_order_workflow)

# ===== PUBLIC API FUNCTIONS =====

class TriggerWorkflowInput(BaseModel):
    workflow_id: str = Field(description="The ID of the workflow to trigger.")
    trigger_data: Dict[str, Any] = Field(description="The input data for the workflow.")

class TriggerWorkflowOutput(BaseModel):
    success: bool = Field(description="True if the workflow was triggered successfully, False otherwise.")
    instance_id: Optional[str] = Field(None, description="The ID of the triggered workflow instance if successful.")
    error: Optional[str] = Field(None, description="Error message if the operation failed.")

class TriggerWorkflowTool:
    """Trigger một workflow với dữ liệu đầu vào."""
    input_schema = TriggerWorkflowInput
    output_schema = TriggerWorkflowOutput

    async def run(self, workflow_id: str, trigger_data: Dict[str, Any]) -> TriggerWorkflowOutput:
        result = await workflow_engine.execute_workflow(workflow_id, trigger_data)
        if result.get("success"):
            return TriggerWorkflowOutput(success=True, instance_id=result.get("instance_id"))
        else:
            return TriggerWorkflowOutput(success=False, error=result.get("error"))

# Định nghĩa Input và Output Schema cho GetWorkflowStatusTool
class GetWorkflowStatusInput(BaseModel):
    instance_id: str = Field(description="The ID of the workflow instance to get status for.")

class GetWorkflowStatusOutput(BaseModel):
    success: bool = Field(description="True if the operation was successful, False otherwise.")
    data: Optional[Dict[str, Any]] = Field(None, description="The workflow instance status data if successful.")
    error: Optional[str] = Field(None, description="Error message if the operation failed.")

class GetWorkflowStatusTool:
    """Lấy trạng thái của workflow instance."""
    input_schema = GetWorkflowStatusInput
    output_schema = GetWorkflowStatusOutput

    def run(self, instance_id: str) -> GetWorkflowStatusOutput:
        if instance_id in workflow_engine.active_instances:
            return GetWorkflowStatusOutput(success=True, data=workflow_engine.active_instances[instance_id])
        else:
            return GetWorkflowStatusOutput(success=False, error="Workflow instance not found")

def list_active_workflows() -> Dict[str, Any]:
    """Liệt kê tất cả workflows đang chạy."""
    return {
        "success": True,
        "data": {
            "total": len(workflow_engine.active_instances),
            "instances": list(workflow_engine.active_instances.keys())
        }
    }

class ApproveWorkflowStepInput(BaseModel):
    approval_id: str = Field(description="The ID of the approval request.")
    decision: str = Field(description="The decision ('approve' or 'reject').")
    notes: str = Field(default="", description="Optional notes about the decision.")

class ApproveWorkflowStepOutput(BaseModel):
    success: bool = Field(description="True if the operation was successful, False otherwise.")
    data: Optional[Dict[str, Any]] = Field(None, description="The approval response data if successful.")
    error: Optional[str] = Field(None, description="Error message if the operation failed.")

class ApproveWorkflowStepTool:
    """Phê duyệt hoặc từ chối workflow step."""
    input_schema = ApproveWorkflowStepInput
    output_schema = ApproveWorkflowStepOutput

    async def run(self, approval_id: str, decision: str, notes: str = "") -> ApproveWorkflowStepOutput:
        try:
            url = f"{ERP_API_BASE_URL}/approvals/{approval_id}"
            data = {
                "decision": decision,  # "approve" or "reject"
                "notes": notes,
                "decided_at": datetime.now().isoformat()
            }

            response = requests.put(url, headers=HEADERS, json=data, timeout=15)
            response.raise_for_status()

            return ApproveWorkflowStepOutput(success=True, data=response.json())

        except Exception as e:
            return ApproveWorkflowStepOutput(success=False, error=str(e))

# ===== WORKFLOW MONITORING =====

def get_workflow_analytics(date_range: Dict[str, str]) -> Dict[str, Any]:
    """Lấy analytics về workflow execution."""
    try:
        url = f"{ERP_API_BASE_URL}/workflows/analytics"
        response = requests.get(url, headers=HEADERS, params=date_range, timeout=15)
        response.raise_for_status()
        
        return {"success": True, "data": response.json()}
        
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_failed_workflows(limit: int = 10) -> Dict[str, Any]:
    """Lấy danh sách workflows bị lỗi."""
    failed_instances = {
        k: v for k, v in workflow_engine.active_instances.items()
        if v["status"] == WorkflowStatus.FAILED.value
    }
    
    return {
        "success": True,
        "data": {
            "total_failed": len(failed_instances),
            "instances": list(failed_instances.items())[:limit]
        }
    }

# Initialize default workflows
setup_default_workflows()