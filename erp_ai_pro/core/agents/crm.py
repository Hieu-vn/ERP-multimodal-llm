"""
Customer Relationship Management (CRM) Agent for ERP AI Pro Version
Comprehensive CRM including lead management, sales pipeline, customer service, and relationship analytics.
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

class LeadStatus(Enum):
    NEW = "new"
    QUALIFIED = "qualified"
    CONTACTED = "contacted"
    INTERESTED = "interested"
    PROPOSAL_SENT = "proposal_sent"
    NEGOTIATION = "negotiation"
    WON = "won"
    LOST = "lost"

class OpportunityStage(Enum):
    PROSPECTING = "prospecting"
    QUALIFICATION = "qualification"
    PROPOSAL = "proposal"
    NEGOTIATION = "negotiation"
    CLOSING = "closing"
    WON = "won"
    LOST = "lost"

class CustomerTier(Enum):
    PLATINUM = "platinum"
    GOLD = "gold"
    SILVER = "silver"
    BRONZE = "bronze"

class TicketPriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

# ===== LEAD MANAGEMENT =====

# Định nghĩa Input và Output Schema cho CreateLeadTool
class CreateLeadInput(BaseModel):
    lead_data: Dict[str, Any] = Field(description="The data for the new lead, including contact_info, lead_details, assigned_to, and notes.")

class CreateLeadOutput(BaseModel):
    success: bool = Field(description="True if the lead was created successfully, False otherwise.")
    data: Optional[Dict[str, Any]] = Field(None, description="The created lead data if successful.")
    error: Optional[str] = Field(None, description="Error message if the operation failed.")

class CreateLeadTool:
    """Tạo lead mới."""
    input_schema = CreateLeadInput
    output_schema = CreateLeadOutput

    def run(self, lead_data: Dict[str, Any]) -> CreateLeadOutput:
        url = f"{ERP_API_BASE_URL}/crm/leads"
        try:
            resp = requests.post(url, headers=HEADERS, json=lead_data, timeout=15)
            resp.raise_for_status()
            return CreateLeadOutput(success=True, data=resp.json())
        except Exception as e:
            return CreateLeadOutput(success=False, error=str(e))

class QualifyLeadInput(BaseModel):
    lead_id: str = Field(description="The ID of the lead to qualify.")
    qualification_data: Dict[str, Any] = Field(description="The qualification data for the lead.")

class QualifyLeadOutput(BaseModel):
    success: bool = Field(description="True if the lead was qualified successfully, False otherwise.")
    data: Optional[Dict[str, Any]] = Field(None, description="The qualified lead data if successful.")
    error: Optional[str] = Field(None, description="Error message if the operation failed.")

class QualifyLeadTool:
    """Đánh giá chất lượng lead."""
    input_schema = QualifyLeadInput
    output_schema = QualifyLeadOutput

    def run(self, lead_id: str, qualification_data: Dict[str, Any]) -> QualifyLeadOutput:
        url = f"{ERP_API_BASE_URL}/crm/leads/{lead_id}/qualify"
        try:
            resp = requests.put(url, headers=HEADERS, json=qualification_data, timeout=15)
            resp.raise_for_status()
            return QualifyLeadOutput(success=True, data=resp.json())
        except Exception as e:
            return QualifyLeadOutput(success=False, error=str(e))

def convert_lead_to_opportunity(lead_id: str, conversion_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Chuyển lead thành opportunity.
    
    Args:
        conversion_data: {
            "opportunity_name": "ABC Company - ERP Implementation",
            "estimated_value": 250000000,
            "probability": 60,
            "expected_close_date": "2024-06-30",
            "stage": "qualification",
            "products_interested": ["ERP_CORE", "CRM_MODULE"],
            "decision_makers": ["Nguyễn Văn A", "Trần Thị B"],
            "competitors": ["SAP", "Oracle"]
        }
    """
    url = f"{ERP_API_BASE_URL}/crm/leads/{lead_id}/convert"
    try:
        resp = requests.post(url, headers=HEADERS, json=conversion_data, timeout=15)
        resp.raise_for_status()
        return {"success": True, "data": resp.json()}
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_lead_scoring(lead_id: str) -> Dict[str, Any]:
    """Lấy điểm số và phân tích lead."""
    url = f"{ERP_API_BASE_URL}/crm/leads/{lead_id}/scoring"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        return {"success": True, "data": resp.json()}
    except Exception as e:
        return {"success": False, "error": str(e)}

# ===== OPPORTUNITY MANAGEMENT =====

class CreateOpportunityInput(BaseModel):
    opportunity_data: Dict[str, Any] = Field(description="The data for the new opportunity, including name, account_id, contact_id, amount, currency, stage, probability, expected_close_date, lead_source, products, assigned_to, team_members, and description.")

class CreateOpportunityOutput(BaseModel):
    success: bool = Field(description="True if the opportunity was created successfully, False otherwise.")
    data: Optional[Dict[str, Any]] = Field(None, description="The created opportunity data if successful.")
    error: Optional[str] = Field(None, description="Error message if the operation failed.")

class CreateOpportunityTool:
    """Tạo cơ hội bán hàng."""
    input_schema = CreateOpportunityInput
    output_schema = CreateOpportunityOutput

    def run(self, opportunity_data: Dict[str, Any]) -> CreateOpportunityOutput:
        url = f"{ERP_API_BASE_URL}/crm/opportunities"
        try:
            resp = requests.post(url, headers=HEADERS, json=opportunity_data, timeout=15)
            resp.raise_for_status()
            return CreateOpportunityOutput(success=True, data=resp.json())
        except Exception as e:
            return CreateOpportunityOutput(success=False, error=str(e))

def update_opportunity_stage(opportunity_id: str, stage_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Cập nhật giai đoạn opportunity.
    
    Args:
        stage_data: {
            "stage": "proposal",
            "probability": 70,
            "amount": 550000000,
            "expected_close_date": "2024-07-30",
            "stage_notes": "Proposal submitted, positive feedback received",
            "next_steps": "Follow up on technical questions",
            "updated_by": "EMP002"
        }
    """
    url = f"{ERP_API_BASE_URL}/crm/opportunities/{opportunity_id}/stage"
    try:
        resp = requests.put(url, headers=HEADERS, json=stage_data, timeout=15)
        resp.raise_for_status()
        return {"success": True, "data": resp.json()}
    except Exception as e:
        return {"success": False, "error": str(e)}

def create_proposal(proposal_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Tạo đề xuất cho opportunity.
    
    Args:
        proposal_data: {
            "opportunity_id": "OPP001",
            "title": "ERP Implementation Proposal",
            "description": "Comprehensive ERP solution for XYZ Corp",
            "line_items": [
                {
                    "product_service": "ERP Core License",
                    "description": "User licenses for 100 users",
                    "quantity": 100,
                    "unit_price": 2000000,
                    "total": 200000000
                },
                {
                    "product_service": "Implementation Services",
                    "description": "Setup and configuration",
                    "quantity": 1,
                    "unit_price": 300000000,
                    "total": 300000000
                }
            ],
            "subtotal": 500000000,
            "discount": 25000000,
            "tax": 47500000,
            "total": 522500000,
            "valid_until": "2024-04-30",
            "terms_conditions": "Standard terms apply",
            "created_by": "EMP002"
        }
    """
    url = f"{ERP_API_BASE_URL}/crm/proposals"
    try:
        resp = requests.post(url, headers=HEADERS, json=proposal_data, timeout=15)
        resp.raise_for_status()
        return {"success": True, "data": resp.json()}
    except Exception as e:
        return {"success": False, "error": str(e)}

def track_proposal_status(proposal_id: str) -> Dict[str, Any]:
    """Theo dõi trạng thái proposal."""
    url = f"{ERP_API_BASE_URL}/crm/proposals/{proposal_id}/status"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        return {"success": True, "data": resp.json()}
    except Exception as e:
        return {"success": False, "error": str(e)}

# ===== CUSTOMER MANAGEMENT =====

class CreateCustomerAccountInput(BaseModel):
    account_data: Dict[str, Any] = Field(description="The data for the new customer account, including company_info, address, financial_info, assigned_to, tier, and source.")

class CreateCustomerAccountOutput(BaseModel):
    success: bool = Field(description="True if the customer account was created successfully, False otherwise.")
    data: Optional[Dict[str, Any]] = Field(None, description="The created customer account data if successful.")
    error: Optional[str] = Field(None, description="Error message if the operation failed.")

class CreateCustomerAccountTool:
    """Tạo tài khoản khách hàng."""
    input_schema = CreateCustomerAccountInput
    output_schema = CreateCustomerAccountOutput

    def run(self, account_data: Dict[str, Any]) -> CreateCustomerAccountOutput:
        url = f"{ERP_API_BASE_URL}/crm/accounts"
        try:
            resp = requests.post(url, headers=HEADERS, json=account_data, timeout=15)
            resp.raise_for_status()
            return CreateCustomerAccountOutput(success=True, data=resp.json())
        except Exception as e:
            return CreateCustomerAccountOutput(success=False, error=str(e))

def create_contact(contact_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Tạo liên hệ khách hàng.
    
    Args:
        contact_data: {
            "account_id": "ACC001",
            "personal_info": {
                "first_name": "Nguyễn",
                "last_name": "Văn A",
                "email": "nguyenvana@abctech.com",
                "phone": "0901234567",
                "mobile": "0987654321",
                "position": "CTO",
                "department": "Technology"
            },
            "preferences": {
                "preferred_contact_method": "email",
                "language": "Vietnamese",
                "timezone": "Asia/Ho_Chi_Minh",
                "communication_frequency": "weekly"
            },
            "role_in_buying_process": "decision_maker",
            "influence_level": "high",
            "relationship_strength": "strong"
        }
    """
    url = f"{ERP_API_BASE_URL}/crm/contacts"
    try:
        resp = requests.post(url, headers=HEADERS, json=contact_data, timeout=15)
        resp.raise_for_status()
        return {"success": True, "data": resp.json()}
    except Exception as e:
        return {"success": False, "error": str(e)}

def update_customer_tier(account_id: str, tier_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Cập nhật tier khách hàng.
    
    Args:
        tier_data: {
            "new_tier": "platinum",
            "effective_date": "2024-01-01",
            "reason": "Increased annual spend and loyalty",
            "benefits": ["Priority support", "Dedicated account manager"],
            "updated_by": "EMP002"
        }
    """
    url = f"{ERP_API_BASE_URL}/crm/accounts/{account_id}/tier"
    try:
        resp = requests.put(url, headers=HEADERS, json=tier_data, timeout=15)
        resp.raise_for_status()
        return {"success": True, "data": resp.json()}
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_customer_360_view(account_id: str) -> Dict[str, Any]:
    """Lấy view 360 độ của khách hàng."""
    url = f"{ERP_API_BASE_URL}/crm/accounts/{account_id}/360-view"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        return {"success": True, "data": resp.json()}
    except Exception as e:
        return {"success": False, "error": str(e)}

# ===== ACTIVITY MANAGEMENT =====

def log_activity(activity_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Ghi nhận hoạt động.
    
    Args:
        activity_data: {
            "type": "call",
            "subject": "Discovery call with ABC Tech",
            "description": "Discussed current challenges and ERP requirements",
            "related_to": {
                "type": "opportunity",
                "id": "OPP001"
            },
            "participants": [
                {
                    "contact_id": "CON001",
                    "role": "client"
                },
                {
                    "employee_id": "EMP002",
                    "role": "sales_rep"
                }
            ],
            "date_time": "2024-02-15T14:00:00",
            "duration": 60,
            "outcome": "positive",
            "next_steps": "Send product demo link",
            "follow_up_date": "2024-02-20"
        }
    """
    url = f"{ERP_API_BASE_URL}/crm/activities"
    try:
        resp = requests.post(url, headers=HEADERS, json=activity_data, timeout=15)
        resp.raise_for_status()
        return {"success": True, "data": resp.json()}
    except Exception as e:
        return {"success": False, "error": str(e)}

def schedule_activity(schedule_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Lên lịch hoạt động.
    
    Args:
        schedule_data: {
            "type": "meeting",
            "subject": "Product demo for XYZ Corp",
            "description": "Demonstrate key ERP features",
            "related_to": {
                "type": "opportunity",
                "id": "OPP001"
            },
            "scheduled_for": "2024-02-25T10:00:00",
            "duration": 90,
            "location": "Client office",
            "attendees": [
                {
                    "contact_id": "CON001",
                    "required": True
                },
                {
                    "employee_id": "EMP002",
                    "required": True
                }
            ],
            "preparation_notes": "Prepare custom demo focusing on their industry"
        }
    """
    url = f"{ERP_API_BASE_URL}/crm/activities/schedule"
    try:
        resp = requests.post(url, headers=HEADERS, json=schedule_data, timeout=15)
        resp.raise_for_status()
        return {"success": True, "data": resp.json()}
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_activity_timeline(related_id: str, related_type: str) -> Dict[str, Any]:
    """Lấy timeline hoạt động."""
    url = f"{ERP_API_BASE_URL}/crm/activities/timeline"
    params = {"related_id": related_id, "related_type": related_type}
    try:
        resp = requests.get(url, headers=HEADERS, params=params, timeout=10)
        resp.raise_for_status()
        return {"success": True, "data": resp.json()}
    except Exception as e:
        return {"success": False, "error": str(e)}

# ===== CUSTOMER SERVICE =====

class CreateSupportTicketInput(BaseModel):
    ticket_data: Dict[str, Any] = Field(description="The data for the new support ticket, including customer_info, issue_details, environment, assigned_to, and source.")

class CreateSupportTicketOutput(BaseModel):
    success: bool = Field(description="True if the support ticket was created successfully, False otherwise.")
    data: Optional[Dict[str, Any]] = Field(None, description="The created support ticket data if successful.")
    error: Optional[str] = Field(None, description="Error message if the operation failed.")

class CreateSupportTicketTool:
    """Tạo ticket hỗ trợ."""
    input_schema = CreateSupportTicketInput
    output_schema = CreateSupportTicketOutput

    def run(self, ticket_data: Dict[str, Any]) -> CreateSupportTicketOutput:
        url = f"{ERP_API_BASE_URL}/crm/tickets"
        try:
            resp = requests.post(url, headers=HEADERS, json=ticket_data, timeout=15)
            resp.raise_for_status()
            return CreateSupportTicketOutput(success=True, data=resp.json())
        except Exception as e:
            return CreateSupportTicketOutput(success=False, error=str(e))

def update_ticket_status(ticket_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Cập nhật trạng thái ticket.
    
    Args:
        update_data: {
            "status": "in_progress",
            "assignee": "EMP005",
            "priority": "high",
            "notes": "Investigating database connection issues",
            "estimated_resolution": "2024-02-16T16:00:00",
            "internal_notes": "Possible network connectivity issue"
        }
    """
    url = f"{ERP_API_BASE_URL}/crm/tickets/{ticket_id}/update"
    try:
        resp = requests.put(url, headers=HEADERS, json=update_data, timeout=15)
        resp.raise_for_status()
        return {"success": True, "data": resp.json()}
    except Exception as e:
        return {"success": False, "error": str(e)}

def add_ticket_comment(ticket_id: str, comment_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Thêm comment vào ticket.
    
    Args:
        comment_data: {
            "comment": "We've identified the root cause and are applying a fix",
            "comment_type": "public",
            "author": "EMP005",
            "time_spent": 30,
            "attachments": ["screenshot.png", "error_log.txt"]
        }
    """
    url = f"{ERP_API_BASE_URL}/crm/tickets/{ticket_id}/comments"
    try:
        resp = requests.post(url, headers=HEADERS, json=comment_data, timeout=15)
        resp.raise_for_status()
        return {"success": True, "data": resp.json()}
    except Exception as e:
        return {"success": False, "error": str(e)}

def escalate_ticket(ticket_id: str, escalation_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Escalate ticket.
    
    Args:
        escalation_data: {
            "escalation_level": "level_2",
            "escalated_to": "EMP010",
            "reason": "Complex technical issue requiring senior expertise",
            "escalated_by": "EMP005",
            "urgency_increased": True
        }
    """
    url = f"{ERP_API_BASE_URL}/crm/tickets/{ticket_id}/escalate"
    try:
        resp = requests.post(url, headers=HEADERS, json=escalation_data, timeout=15)
        resp.raise_for_status()
        return {"success": True, "data": resp.json()}
    except Exception as e:
        return {"success": False, "error": str(e)}

# ===== CRM ANALYTICS & REPORTING =====

def get_sales_pipeline_report(date_range: Dict[str, str]) -> Dict[str, Any]:
    """Báo cáo sales pipeline."""
    url = f"{ERP_API_BASE_URL}/crm/reports/pipeline"
    try:
        resp = requests.get(url, headers=HEADERS, params=date_range, timeout=10)
        resp.raise_for_status()
        return {"success": True, "data": resp.json()}
    except Exception as e:
        return {"success": False, "error": str(e)}

def calculate_conversion_rates(date_range: Dict[str, str]) -> Dict[str, Any]:
    """Tính tỷ lệ chuyển đổi."""
    url = f"{ERP_API_BASE_URL}/crm/analytics/conversion-rates"
    try:
        resp = requests.get(url, headers=HEADERS, params=date_range, timeout=10)
        resp.raise_for_status()
        return {"success": True, "data": resp.json()}
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_customer_lifetime_value(account_id: str = None) -> Dict[str, Any]:
    """Tính customer lifetime value."""
    url = f"{ERP_API_BASE_URL}/crm/analytics/customer-lifetime-value"
    params = {"account_id": account_id} if account_id else {}
    try:
        resp = requests.get(url, headers=HEADERS, params=params, timeout=10)
        resp.raise_for_status()
        return {"success": True, "data": resp.json()}
    except Exception as e:
        return {"success": False, "error": str(e)}

def analyze_sales_performance(employee_id: str, date_range: Dict[str, str]) -> Dict[str, Any]:
    """Phân tích hiệu suất bán hàng."""
    url = f"{ERP_API_BASE_URL}/crm/analytics/sales-performance/{employee_id}"
    try:
        resp = requests.get(url, headers=HEADERS, params=date_range, timeout=10)
        resp.raise_for_status()
        return {"success": True, "data": resp.json()}
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_customer_satisfaction_metrics() -> Dict[str, Any]:
    """Lấy metrics về customer satisfaction."""
    url = f"{ERP_API_BASE_URL}/crm/analytics/customer-satisfaction"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        return {"success": True, "data": resp.json()}
    except Exception as e:
        return {"success": False, "error": str(e)}

def generate_crm_dashboard() -> Dict[str, Any]:
    """Tạo CRM dashboard tổng quan."""
    url = f"{ERP_API_BASE_URL}/crm/dashboard"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        return {"success": True, "data": resp.json()}
    except Exception as e:
        return {"success": False, "error": str(e)}

# ===== MARKETING AUTOMATION =====

def create_marketing_campaign(campaign_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Tạo chiến dịch marketing.
    
    Args:
        campaign_data: {
            "name": "Q1 2024 Product Launch",
            "description": "Launch campaign for new ERP features",
            "type": "product_launch",
            "channels": ["email", "social_media", "webinar"],
            "target_audience": {
                "industry": ["technology", "manufacturing"],
                "company_size": ["50-200", "200-500"],
                "lead_score_min": 70
            },
            "budget": 50000000,
            "start_date": "2024-03-01",
            "end_date": "2024-04-30",
            "goals": {
                "leads_target": 500,
                "mqls_target": 150,
                "sqls_target": 50
            },
            "owner": "EMP006"
        }
    """
    url = f"{ERP_API_BASE_URL}/crm/campaigns"
    try:
        resp = requests.post(url, headers=HEADERS, json=campaign_data, timeout=15)
        resp.raise_for_status()
        return {"success": True, "data": resp.json()}
    except Exception as e:
        return {"success": False, "error": str(e)}

def track_campaign_performance(campaign_id: str) -> Dict[str, Any]:
    """Theo dõi hiệu suất chiến dịch."""
    url = f"{ERP_API_BASE_URL}/crm/campaigns/{campaign_id}/performance"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        return {"success": True, "data": resp.json()}
    except Exception as e:
        return {"success": False, "error": str(e)}