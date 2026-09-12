"""
Decision Logger Module
Logs all ticket decisions for audit trail
"""

import csv
import os
from datetime import datetime
from pathlib import Path


class DecisionLogger:
    """Logs ticket decisions to CSV file"""
    
    def __init__(self, log_dir: str = "./logs", log_file: str = "decisions.csv"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        self.log_file = self.log_dir / log_file
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        """Create CSV file with headers if it doesn't exist"""
        if not self.log_file.exists():
            headers = [
                "timestamp",
                "ticket_id",
                "requestor",
                "asset_id",
                "decision",
                "reason",
                "system_or_user",
                "execution_time_sec",
                "details"
            ]
            with open(self.log_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(headers)
    
    def log_decision(
        self,
        ticket_id: str,
        requestor: str,
        asset_id: str,
        decision: str,  # "APPROVED" or "REJECTED"
        reason: str,
        system_or_user: str = "system",  # "system" or "user"
        execution_time: float = 0.0,
        details: str = ""
    ):
        """Log a single decision"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        row = [
            timestamp,
            ticket_id,
            requestor,
            asset_id,
            decision.upper(),
            reason,
            system_or_user,
            f"{execution_time:.1f}",
            details
        ]
        
        with open(self.log_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(row)
        
        return timestamp
    
    def get_recent_decisions(self, limit: int = 10) -> list:
        """Get recent decisions from log"""
        if not self.log_file.exists():
            return []
        
        decisions = []
        with open(self.log_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                decisions.append(row)
        
        return decisions[-limit:]
    
    def get_stats(self) -> dict:
        """Get decision statistics"""
        if not self.log_file.exists():
            return {"total": 0, "approved": 0, "rejected": 0}
        
        total = 0
        approved = 0
        rejected = 0
        
        with open(self.log_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                total += 1
                if row.get("decision") == "APPROVED":
                    approved += 1
                elif row.get("decision") == "REJECTED":
                    rejected += 1
        
        return {
            "total": total,
            "approved": approved,
            "rejected": rejected,
            "approval_rate": f"{(approved/total*100):.1f}%" if total > 0 else "0%"
        }
