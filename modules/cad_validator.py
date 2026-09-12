"""
CAD Validator Module
Checks if assets are CAD compliant based on rules
"""

from typing import Dict, Tuple, List


class CADValidator:
    """Validates CAD compliance for assets"""
    
    def __init__(self, config: dict):
        self.config = config
        self.rules = config.get('cad_rules', {}).get('rules', [])
        self.enabled = config.get('cad_rules', {}).get('enabled', False)
    
    def validate(self, asset: Dict) -> Tuple[bool, str]:
        """
        Validate if asset is CAD compliant
        
        Returns:
            Tuple of (is_compliant: bool, reason: str)
        """
        # If CAD rules are not enabled, approve by default
        if not self.enabled:
            return True, "CAD rules not configured - auto approved"
        
        # If no rules defined, approve by default
        if not self.rules:
            return True, "No CAD rules defined - auto approved"
        
        # Check each rule
        failures = []
        for rule in self.rules:
            is_valid = self._check_rule(asset, rule)
            if not is_valid:
                failures.append(f"{rule['name']}: {rule.get('failure_message', 'Failed')}")
        
        if failures:
            return False, "; ".join(failures)
        
        return True, "All CAD rules passed"
    
    def _check_rule(self, asset: Dict, rule: Dict) -> bool:
        """Check a single rule against asset"""
        rule_name = rule.get('name', '')
        field = rule.get('field', '')
        condition = rule.get('condition', '')
        expected = rule.get('expected', None)
        
        # Get asset field value
        asset_value = asset.get(field, '')
        
        # Rule checking logic (customize based on your rules)
        if rule_name == "license_check":
            return asset_value.lower() in ['valid', 'active', 'licensed']
        
        elif rule_name == "version_check":
            # Example: Check if version >= 2.0
            try:
                return float(asset_value) >= float(expected)
            except:
                return False
        
        elif rule_name == "expiry_check":
            # Example: Check if not expired
            from datetime import datetime
            try:
                expiry = datetime.strptime(asset_value, "%Y-%m-%d")
                return expiry > datetime.now()
            except:
                return False
        
        elif rule_name == "department_check":
            # Example: Check if department is allowed
            allowed = rule.get('allowed_values', [])
            return asset_value in allowed
        
        elif rule_name == "status_check":
            # Example: Check if status is compliant
            return asset_value.lower() in ['active', 'in-use', 'compliant']
        
        elif rule_name == "custom":
            # Example: Custom rule with custom logic
            # Add your custom validation logic here
            pass
        
        # Default: approve if rule not recognized
        return True
    
    def get_rule_summary(self) -> str:
        """Get summary of configured rules"""
        if not self.enabled:
            return "CAD rules are DISABLED"
        
        if not self.rules:
            return "CAD rules are ENABLED but no rules configured"
        
        summary = f"CAD rules: {len(self.rules)} rules configured\n"
        for rule in self.rules:
            summary += f"  - {rule.get('name', 'unnamed')}: {rule.get('field')} {rule.get('condition')}\n"
        
        return summary
