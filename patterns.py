import re

class Pattern:
    def __init__(self, name, regex, context_required=False):
        self.name = name
        self.regex = re.compile(regex)
        self.context_required = context_required

# common patterns sourced from security research and public regex lists
PATTERNS = [
    Pattern("AWS Access Key ID", r"(A3T[A-Z0-9]|AKIA|AGPA|AIDA|AROA|AIPA|ANPA|ANVA|ASIA)[A-Z0-9]{16}"),
    # FIX: Python re module doesn't support (?-i). Using [aA][wW][sS] instead.
    Pattern("AWS Secret Access Key", r"(?:[aA][wW][sS])(.{0,20})?['\"][0-9a-zA-Z\/+]{40}['\"]"),
    Pattern("Google API Key", r"AIza[0-9A-Za-z\\_-]{35}"),
    Pattern("Google OAuth", r"[0-9]+-[0-9A-Za-z_]{32}\.apps\.googleusercontent\.com"),
    Pattern("Stripe Live Key", r"sk_live_[0-9a-zA-Z]{24}"),
    Pattern("Stripe Restricted Key", r"rk_live_[0-9a-zA-Z]{24}"),
    Pattern("OpenAI API Key", r"sk-proj-[a-zA-Z0-9]{20,}|sk-[a-zA-Z0-9]{20,}"), # Updated for new and old formats
    Pattern("Slack Token", r"xox[baprs]-([0-9a-zA-Z]{10,48})?"),
    Pattern("GitHub Personal Access Token", r"ghp_[0-9a-zA-Z]{36}"),
    Pattern("Facebook Access Token", r"EAACEdEose0cBA[0-9A-Za-z]+"),
    Pattern("Twilio API Key", r"SK[0-9a-fA-F]{32}"),
    Pattern("SendGrid API Key", r"SG\.[0-9A-Za-z_\-]{22}\.[0-9A-Za-z_\-]{43}"),
    Pattern("Mailgun API Key", r"key-[0-9a-zA-Z]{32}"),
    Pattern("Heroku API Key", r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"),
    Pattern("Generic Private Key", r"-----BEGIN [A-Z ]+ PRIVATE KEY-----"),
    Pattern("Generic High Entropy", r"['\"](?!.*[ ])(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])[a-zA-Z0-9_\-]{20,}['\"]"), # Aggressive generic check
]

def scan_text(text):
    """
    Scans a block of text for all defined patterns.
    Returns a list of dicts: {name, value, match_index}
    """
    findings = []
    # Quick optimization: don't scan if line is too long (minified code)
    if len(text) > 10000: 
        return findings

    for pattern in PATTERNS:
        matches = pattern.regex.findall(text)
        for match in matches:
            if isinstance(match, tuple):
                match = match[0] # Handle groups if present
            
            # Simple heuristic to avoid false positives on the Generic pattern
            if pattern.name == "Generic High Entropy":
                if "EXAMPLE" in match or "TEST" in match:
                    continue
            
            findings.append({
                "type": pattern.name,
                "value": match,
                # We don't store index here for simplicity, but could later
            })
    return findings
