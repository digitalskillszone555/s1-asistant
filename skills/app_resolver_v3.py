# skills/app_resolver_v3.py
# S1 Assistant - App Resolver V3
# Focus: Unified lookup combining manual rules (V2) and auto-discovery (V3).

from skills.app_resolver_v2 import get_resolver_v2
from system.app_matcher import find_app_path

class AppResolverV3:
    """
    Combines the strengths of the manual V2 resolver and the dynamic V3 discovery.
    """
    def __init__(self):
        self.resolver_v2 = get_resolver_v2()

    def resolve(self, alias: str) -> str:
        """
        1. Try manual V2 resolver (most reliable)
        2. Fallback to V3 dynamic discovery (most comprehensive)
        """
        if not alias:
            return None

        # --- STEP 1: V2 (Manual Map & System PATH) ---
        path = self.resolver_v2.resolve(alias)
        if path:
            print(f"[ResolverV3] Resolved via V2 logic: '{alias}' -> {path}")
            return path

        # --- STEP 2: V3 (Dynamic App Registry) ---
        path = find_app_path(alias)
        if path:
            print(f"[ResolverV3] Resolved via V3 Dynamic Discovery: '{alias}' -> {path}")
            return path

        return None

# Global Access
_resolver_v3_instance = None

def get_resolver_v3():
    global _resolver_v3_instance
    if _resolver_v3_instance is None:
        _resolver_v3_instance = AppResolverV3()
    return _resolver_v3_instance
