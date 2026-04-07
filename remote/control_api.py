# remote/control_api.py
import http.server
import json
import os
import sys
from system.ai_mode_manager import get_ai_mode_manager
from memory.memory_manager import get_memory_manager
from user.user_manager import get_user_manager
from security.permissions import ADMIN_ROLE
from main import shutdown_event
from utils.logging_utils import log_event # Centralized logging

LOG_FILE = os.path.join("logs", "security.log")

class ControlAPIHandler(http.server.BaseHTTPRequestHandler):
    """
    Handles incoming HTTP requests for the S1 remote control system.
    Includes token authentication and role-based authorization.
    """
    auth_token: str = "" # This will be set by the factory in the server

    def _send_error(self, code: int, message: str):
        self.send_response(code)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"error": message}).encode('utf-8'))

    def _handle_auth(self) -> bool:
        """Checks for a valid Bearer token in the Authorization header."""
        auth_header = self.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            log_event("SECURITY", f"AUTH FAILED: Missing or malformed Authorization header from {self.client_address[0]}.", level="WARNING", log_file="security.log")
            self._send_error(401, "Unauthorized: Missing or malformed 'Authorization: Bearer <token>' header.")
            return False
        
        provided_token = auth_header.split(" ")[1]
        if provided_token != self.auth_token:
            log_event("SECURITY", f"AUTH FAILED: Invalid token received from {self.client_address[0]}.", level="WARNING", log_file="security.log")
            self._send_error(401, "Unauthorized: Invalid token.")
            return False
            
        return True

    def _is_admin(self) -> bool:
        """Checks if the current S1 user has the ADMIN role."""
        user_info = get_user_manager().get_current_user_info()
        if user_info and user_info.get("role") == ADMIN_ROLE:
            return True
        
        user_role = user_info.get("role", "N/A") if user_info else "N/A"
        log_event("SECURITY", f"ACCESS DENIED: Non-admin user '{get_user_manager().current_user}' (Role: {user_role}) from {self.client_address[0]} attempted to access admin-only endpoint '{self.path}'.", level="WARNING", log_file="security.log")
        self._send_error(403, "Forbidden: Administrator access required.")
        return False

    def do_GET(self):

        """Handles GET requests with authentication and authorization."""
        if not self._handle_auth():
            return

        if self.path == '/status':
            ai_mode = get_ai_mode_manager().get_ai_mode()
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "running", "ai_mode": ai_mode}).encode('utf-8'))
        
        elif self.path == '/skills':
            # This endpoint is not deemed sensitive in the requirements.
            from skills.router import get_skills_router
            router = get_skills_router()
            modular_skills = [skill.name for skill in router.skills]
            legacy_skills = list(router.legacy_skills.keys())
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"skills": modular_skills + legacy_skills}).encode('utf-8'))

        elif self.path == '/memory':
            if not self._is_admin(): return
            memory_manager = get_memory_manager()
            memory_summary = {
                "profile": memory_manager.list_memory("profile"),
                "habits": memory_manager.list_memory("habits"),
                "facts": memory_manager.list_memory("facts")
            }
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"memory": memory_summary}).encode('utf-8'))

        elif self.path == '/logs':
            if not self._is_admin(): return
            try:
                # A safer implementation that reads the last N lines could be better
                with open(LOG_FILE, 'r') as f:
                    logs = f.readlines()
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"security_log": logs[-100:]}).encode('utf-8')) # Return last 100 lines
            except FileNotFoundError:
                self._send_error(404, "Log file not found.")
            
        else:
            self._send_error(404, "Not Found")

    def do_POST(self):
        """Handles POST requests with authentication and authorization."""
        if not self._handle_auth():
            return

        if self.path == '/toggle_ai':
            if not self._is_admin(): return
            ai_mode_manager = get_ai_mode_manager()
            current_mode = ai_mode_manager.get_ai_mode()
            ai_mode_manager.toggle_ai_mode()
            new_mode = ai_mode_manager.get_ai_mode()
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"message": f"AI mode toggled from {current_mode} to {new_mode}"}).encode('utf-8'))

        elif self.path == '/shutdown':
            if not self._is_admin(): return
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"message": "Shutdown signal sent. The system will now begin shutting down."}).encode('utf-8'))
            
            print("[Control Server] Received authorized shutdown command. Signaling main thread.")
            shutdown_event.set() # Signal the main thread to shut down gracefully

        else:
            self._send_error(404, "Not Found")
