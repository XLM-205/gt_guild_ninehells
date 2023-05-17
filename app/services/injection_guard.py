from typing import List
from config.app_defaults import app_defaults


class InjectionToken(Exception):
    """ Raised if the Injection Guard function detects an Injection Attempt """
    pass


def injection_guard(queries: List[str]) -> None:
    """
    Analyses all query strings in 'queries' to prevent injection attacks in 3 phases. The last one attempts to fix them
    :param queries: List of query strings
    """
    # These tokens will reject a query if found at any time
    cases = app_defaults["SECURITY"]["INJ_GUARD"]["CASES"]
    # These tokens will reject a query if found in the order provided
    groups = app_defaults["SECURITY"]["INJ_GUARD"]["GROUPS"]
    # This tokens will be replaced to, if found
    replaces = app_defaults["SECURITY"]["INJ_GUARD"]["REPLACES"]
    for query in queries:
        # First pass: Common tokens
        for case in cases:
            if case in query:
                raise InjectionToken("Invalid characters detected on input string!", )
        # Second pass: Following Matching tokens
        for group in groups:
            full_match = True
            continue_from = 0
            for pair in group:
                continue_from = query.find(pair, continue_from)
                if continue_from == -1:
                    full_match = False
                    break
            if full_match:
                raise InjectionToken("Invalid characters detected on input string!", )
        # Third pass: Hard replace tokens if found
        for replace in replaces:
            query.replace(replace[0], replace[1])

