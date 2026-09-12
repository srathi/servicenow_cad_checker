"""
Decision Engine Module
Makes accept/reject decisions based on CAD validation
"""

from typing import Dict, Tuple
from .cad_validator import CADValidator
from .logger import DecisionLogger


class DecisionEngine:
    """Makes ticket approval decisions"""
    
    def __init__(self, config: dict, logger: DecisionLogger):
        self.config = config
        self.logger = logger
        self.cad_validator = CADValidator(config)
    
    def make_decision(self, ticket: Dict, asset: Dict) -> Tuple[str, str]:
        """
        Make decision on ticket based on asset CAD compliance
        
        Returns:
            Tuple of (decision: str, reason: str)
            decision is "APPROVED" or "REJECTED"
        """
        # Validate CAD compliance
        is_compliant, validation_reason = self.cad_validator.validate(asset)
        
        if is_compliant:
            decision = "APPROVED"
            reason = f"CAD compliant: {validation_reason}"
        else:
            decision = "REJECTED"
            reason = f"Non-compliant: {validation_reason}"
        
        # Log the decision
        self.logger.log_decision(
            ticket_id=ticket.get('ticket_id', 'UNKNOWN'),
            requestor=ticket.get('requestor', 'UNKNOWN'),
            asset_id=ticket.get('asset_id', 'UNKNOWN'),
            decision=decision,
            reason=reason,
            system_or_user="system"
        )
        
        return decision, reason
    
    def get_comment_for_approval(self, asset: Dict) -> str:
        """Generate comment for approved ticket"""
        return f"Auto-approved: Asset {asset.get('asset_id', 'N/A')} is CAD compliant"
    
    def get_reason_for_rejection(self, asset: Dict, validation_reason: str) -> str:
        """Generate reason for rejected ticket"""
        return f"Auto-rejected: {validation_reason}"
