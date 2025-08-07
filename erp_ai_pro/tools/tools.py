from pydantic import BaseModel, Field
import datetime
from .graph_management import neo4j_connection, get_cypher_generation_chain, GRAPH_SCHEMA
from .erp_client import ERPClient
import numexpr as ne

# Initialize the ERP Client
erp_client = ERPClient()

# --- Base Tool Schemas ---

class GetCurrentDateInput(BaseModel):
    query: str = Field(description="Any string, will be ignored. Use this tool when the user asks for the current date.")

class GetCurrentDateTool:
    """
    Returns the current date. Use this tool when the user asks for the current date.
    """
    def run(self, query: str) -> str:
        return f"Today's date is {datetime.date.today().strftime('%Y-%m-%d')}."

# --- Task Management Tools ---

class CreateTaskInput(BaseModel):
    title: str = Field(description="The title of the task.")
    description: str = Field(description="A detailed description of the task.")
    assignee_id: str = Field(description="The ID of the user to whom the task is assigned.")

class CreateTaskTool:
    """
    Creates a new task with a title, description, and assigns it to a user.
    Use this when a user wants to create or assign a new task.
    """
    def run(self, title: str, description: str, assignee_id: str, reporter_id: str = "system") -> str:
        # In a real system, reporter_id would come from the authenticated user
        result = erp_client.create_task(title, description, assignee_id, reporter_id)
        if "error" in result:
            return f"Error creating task: {result['error']}"
        return f"Successfully created task '{result['task_id']}: {result['title']}' and assigned it to {result['assignee_id']}."

class GetTasksByAssigneeInput(BaseModel):
    assignee_id: str = Field(description="The ID of the user whose tasks are to be retrieved.")

class GetTasksByAssigneeTool:
    """
    Retrieves a list of all tasks assigned to a specific user.
    Use this when a user asks to see their tasks or someone else's tasks.
    """
    def run(self, assignee_id: str) -> str:
        tasks = erp_client.get_tasks_by_assignee(assignee_id)
        if not tasks:
            return f"No tasks found for user '{assignee_id}'."
        
        task_list_str = "\n".join([f"- {t['task_id']}: {t['title']} (Project: {t.get('project_id', 'N/A')}, Status: {t['status']})") for t in tasks])
        return f"Tasks for {assignee_id}:\n{task_list_str}"

class GetTasksByProjectInput(BaseModel):
    project_id: str = Field(description="The ID of the project whose tasks are to be retrieved.")

class GetTasksByProjectTool:
    """
    Retrieves a list of all tasks for a specific project.
    Use this when a user asks for all tasks related to a project.
    """
    def run(self, project_id: str) -> str:
        tasks = erp_client.get_tasks_by_project(project_id)
        if not tasks:
            return f"No tasks found for project '{project_id}'."
        
        task_list_str = "\n".join([f"- {t['task_id']}: {t['title']} (Assignee: {t['assignee_id']}, Status: {t['status']})") for t in tasks])
        return f"Tasks for project {project_id}:\n{task_list_str}"

class UpdateTaskStatusInput(BaseModel):
    task_id: str = Field(description="The ID of the task to update (e.g., 'T-1').")
    new_status: str = Field(description="The new status for the task (e.g., 'Đang làm', 'Hoàn thành').")

class UpdateTaskStatusTool:
    """
    Updates the status of a specific task.
    Use this when a user wants to change the state of a task.
    """
    def run(self, task_id: str, new_status: str) -> str:
        result = erp_client.update_task_status(task_id, new_status)
        if "error" in result:
            return f"Error updating task {task_id}: {result['error']}"
        return f"Successfully updated status for task {task_id} to '{new_status}'."

# --- Other Tools (Placeholder) ---

class GraphERPLookupTool:
    """
    (Placeholder) Generates and executes a Cypher query against the ERP Knowledge Graph.
    """
    def run(self, question: str, role: str) -> str:
        return "GraphERPLookupTool is not yet implemented."

class VectorSearchTool:
    """
    (Placeholder) Searches the knowledge base for relevant documents.
    """
    def run(self, query: str, role: str) -> str:
        return "VectorSearchTool is not yet implemented."

class PerformCalculationTool:
    """
    Performs a safe mathematical calculation.
    """
    def run(self, expression: str) -> str:
        try:
            result = ne.evaluate(expression)
            return f"Result of '{expression}': {result}"
        except Exception as e:
            return f"Error performing calculation '{expression}': Invalid expression."
