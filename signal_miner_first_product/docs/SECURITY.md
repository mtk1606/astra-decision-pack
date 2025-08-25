# GrowthSignal MVP - Security & Compliance Guide

## Overview

This document outlines the security measures, compliance policies, and data handling practices implemented in the GrowthSignal MVP. It covers web scraping compliance, data privacy, API security, and operational security.

## Web Scraping Compliance

### Robots.txt Policy

**Current Implementation**: Respect and logging only
**Planned Enforcement**: Automatic compliance checking and enforcement

**Policy Details**:
- **Pre-flight Check**: Verify robots.txt before any data collection
- **Rate Limiting**: Respect crawl-delay directives (planned)
- **Path Restrictions**: Honor Disallow directives (planned)
- **User-Agent**: Identifiable, respectful headers

**Current Status**:
```python
# In signal_miner.py - logging only
def check_robots_txt(url):
    """Check robots.txt but don't enforce yet"""
    try:
        robots_url = f"{url}/robots.txt"
        response = requests.get(robots_url, timeout=5)
        if response.status_code == 200:
            # Log robots.txt content for compliance tracking
            log_robots_compliance(url, response.text)
        return True  # Currently allow all requests
    except Exception:
        return True  # Fail open for now
```

**Planned Enforcement**:
```python
# Future implementation
def enforce_robots_txt(url, path):
    """Enforce robots.txt compliance"""
    robots_rules = get_robots_rules(url)
    if robots_rules.is_disallowed(path):
        raise ComplianceViolation(f"Path {path} disallowed by robots.txt")
    
    # Respect crawl delay
    time.sleep(robots_rules.get_crawl_delay())
```

### Allowlist Enforcement

**Current Status**: Manual review process documented
**Implementation**: Pilot program requirement

**Allowlist Format**:
```json
{
  "company_name": "Example Corp",
  "domain": "example.com",
  "business_justification": "Direct competitor in SaaS analytics space",
  "monitoring_frequency": "daily",
  "approved_date": "2024-01-15",
  "approved_by": "pilot_coordinator"
}
```

**Enforcement Points**:
1. **Pre-pilot**: Domain approval required
2. **During mining**: URL validation against allowlist
3. **Post-mining**: Compliance audit and reporting

### Rate Limiting

**Current Status**: No automatic rate limiting
**Planned Implementation**: Configurable delays and throttling

**Proposed Configuration**:
```python
# Future rate limiting configuration
RATE_LIMITS = {
    "default": {"requests_per_minute": 10, "delay_between": 6.0},
    "news.ycombinator.com": {"requests_per_minute": 5, "delay_between": 12.0},
    "techcrunch.com": {"requests_per_minute": 3, "delay_between": 20.0}
}
```

**Implementation Strategy**:
1. **Phase 1**: Basic delays between requests
2. **Phase 2**: Per-domain rate limiting
3. **Phase 3**: Adaptive rate limiting based on response codes

## Data Privacy & PII Handling

### Personal Data Policy

**Core Principle**: GrowthSignal does not intentionally collect personal identifiable information (PII)

**Data Focus**: Public business information only
- Company announcements and press releases
- Product features and pricing
- Marketing messaging and positioning
- Public financial information

**Excluded Data**:
- Personal email addresses
- Individual phone numbers
- Personal names and profiles
- Social media personal content
- Private user data

### PII Detection & Redaction

**Automatic Detection**:
```python
def redact_pii(text):
    """Automatic PII detection and redaction"""
    # Email addresses
    text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', text)
    
    # Phone numbers (US format)
    text = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '[PHONE]', text)
    
    # Names (basic pattern)
    text = re.sub(r'\b[A-Z][a-z]+ [A-Z][a-z]+\b', '[NAME]', text)
    
    # Social security numbers
    text = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '[SSN]', text)
    
    # Credit card numbers (basic pattern)
    text = re.sub(r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b', '[CARD]', text)
    
    return text
```

**Redaction Logging**:
```json
{
  "timestamp": "2024-01-15T14:30:22.123456Z",
  "domain": "example.com",
  "pii_detected": {
    "emails": 3,
    "phones": 1,
    "names": 2
  },
  "redaction_applied": true,
  "file_path": "snapshots/example.com_20240115T143022Z.html"
}
```

**Reporting Requirements**:
- **Immediate**: Alert pilot coordinator within 24 hours
- **Weekly**: PII detection summary review
- **Monthly**: Pattern analysis and rule updates

### Data Minimization

**Collection Principles**:
- **Business Focus**: Only publicly available business information
- **No User Tracking**: No cookies, tracking pixels, or behavior monitoring
- **No Social Media**: No collection from social media platforms
- **No Personal Profiles**: No monitoring of individual user accounts

**Storage Limitations**:
- **HTML Snapshots**: Raw content with PII redaction
- **Signals**: Extracted business information only
- **Decision Packs**: Generated hypotheses and plans
- **Metadata**: Technical generation details only

## API Security

### OpenAI API Security

**Key Management**:
- **Storage**: Environment variables only
- **Rotation**: Quarterly key rotation recommended
- **Scope**: Minimal required permissions
- **Monitoring**: API usage tracking and alerting

**Security Measures**:
```python
# Secure API key handling
import os
from openai import OpenAI

# Never hardcode keys
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Validate key presence
if not os.environ.get("OPENAI_API_KEY"):
    raise SecurityError("OpenAI API key not configured")
```

**Rate Limiting**:
- **OpenAI Limits**: Respect API quotas and rate limits
- **Application Limits**: Implement request throttling
- **Error Handling**: Graceful degradation on rate limit exceeded

### GitHub API Security

**Token Management**:
- **Scope**: Minimal required permissions (repo access only)
- **Storage**: Environment variables
- **Rotation**: Personal access token rotation
- **Audit**: Regular access review

**Security Configuration**:
```python
# GitHub API security
from github import Github

# Validate token presence
if not os.environ.get("GITHUB_TOKEN"):
    # Fall back to preview mode
    return create_preview_only(pack, domain)

# Use minimal scope token
g = Github(os.environ.get("GITHUB_TOKEN"))
repo = g.get_repo(os.environ.get("GITHUB_REPO"))
```

**Fallback Security**:
- **No Token**: Preview mode only
- **Invalid Token**: Clear error messages
- **Rate Limited**: Exponential backoff
- **Access Denied**: Detailed logging for investigation

### Pinecone API Security

**Key Management**:
- **Storage**: Environment variables
- **Scope**: Index-specific access
- **Rotation**: API key rotation support
- **Monitoring**: Usage tracking and alerting

**Fallback Security**:
```python
# Secure fallback to FAISS
def get_secure_store(embed_dim, index_name):
    """Get vector store with security fallback"""
    if os.environ.get("PINECONE_API_KEY"):
        try:
            return get_pinecone_store(embed_dim, index_name)
        except Exception as e:
            log_security_event("pinecone_fallback", str(e))
            return get_faiss_store(embed_dim)
    else:
        return get_faiss_store(embed_dim)
```

## Operational Security

### Environment Variable Security

**Required Variables**:
```bash
# Required for RAG functionality
OPENAI_API_KEY=sk-your-openai-api-key

# Optional for production vector storage
PINECONE_API_KEY=your-pinecone-api-key
PINECONE_ENV=your-pinecone-environment

# Optional for GitHub integration
GITHUB_TOKEN=your-github-personal-access-token
GITHUB_REPO=owner/repo-name
```

**Security Best Practices**:
- **Never commit** API keys to version control
- **Use .env files** for local development (not committed)
- **Rotate keys regularly** for production use
- **Monitor usage** for unusual patterns
- **Limit scope** of API permissions

### File System Security

**Output Directory Security**:
```python
# Secure output directory creation
def create_secure_output_dirs():
    """Create output directories with proper permissions"""
    output_dirs = [
        "output/decision_packs",
        "output/previews", 
        "output/snapshots",
        "output/signals"
    ]
    
    for dir_path in output_dirs:
        os.makedirs(dir_path, exist_ok=True)
        # Set restrictive permissions on Windows
        if os.name == 'nt':
            import stat
            os.chmod(dir_path, stat.S_IREAD | stat.S_IWRITE | stat.S_IEXEC)
```

**File Permission Guidelines**:
- **Output Directories**: Read/write for application only
- **HTML Snapshots**: Read-only after creation
- **Decision Packs**: Read/write for application
- **Configuration Files**: Read-only for application

### Logging & Monitoring

**Security Event Logging**:
```python
# Security event logging
def log_security_event(event_type, details, severity="info"):
    """Log security-related events"""
    event = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "event_type": event_type,
        "details": details,
        "severity": severity,
        "user_ip": get_client_ip(),
        "user_agent": get_user_agent()
    }
    
    # Log to security log file
    with open("logs/security.log", "a") as f:
        json.dump(event, f)
        f.write("\n")
    
    # Alert on high severity events
    if severity == "high":
        alert_security_team(event)
```

**Event Types**:
- `api_key_exposure`: Potential API key compromise
- `compliance_violation`: Robots.txt or rate limit violations
- `pii_detection`: Personal data found and redacted
- `access_denied`: Unauthorized access attempts
- `rate_limit_exceeded`: API rate limit violations

## Compliance Monitoring

### Regular Audits

**Audit Schedule**:
- **Daily**: PII detection and redaction logs
- **Weekly**: Robots.txt compliance review
- **Monthly**: Full compliance audit
- **Quarterly**: External compliance review

**Audit Checklist**:
- [ ] Robots.txt compliance verified
- [ ] PII detection logs reviewed
- [ ] Rate limiting parameters checked
- [ ] API key rotation status
- [ ] Access control validation
- [ ] Data retention compliance
- [ ] Security event review

### Incident Response

**Response Process**:
1. **Detection**: Identify security or compliance incident
2. **Assessment**: Determine severity and impact
3. **Containment**: Stop affected operations
4. **Investigation**: Document root cause
5. **Remediation**: Implement fixes
6. **Notification**: Alert stakeholders
7. **Review**: Update policies and procedures

**Severity Levels**:
- **Low**: Minor policy violations, no data exposure
- **Medium**: Compliance violations, potential data exposure
- **High**: Security breach, confirmed data exposure
- **Critical**: System compromise, widespread impact

### Reporting & Documentation

**Compliance Reports**:
- **Weekly Summary**: PII detection, compliance status
- **Monthly Report**: Full compliance audit results
- **Quarterly Review**: Policy updates and improvements
- **Annual Assessment**: External compliance validation

**Documentation Requirements**:
- **Incident Reports**: Detailed documentation of all incidents
- **Policy Updates**: Changes to compliance policies
- **Training Materials**: Security and compliance training
- **Audit Trails**: Complete audit trail for all operations

## Legal Considerations

### Web Scraping Legal Status

**Current Position**: Educational/research use with compliance measures
**Legal Risks**: Potential terms of service violations
**Mitigation**: Strict compliance with robots.txt and rate limiting

**Legal Recommendations**:
- **Consult Counsel**: Legal review for production use
- **Terms Review**: Review website terms of service
- **Compliance**: Implement all compliance measures
- **Documentation**: Maintain compliance audit trails

### Data Protection

**GDPR Considerations**:
- **Data Minimization**: Only collect necessary business information
- **Right to Erasure**: Implement data deletion procedures
- **Data Portability**: Export capabilities for user data
- **Consent Management**: Clear data usage policies

**CCPA Considerations**:
- **Data Categories**: Clear categorization of collected data
- **Opt-out Rights**: User control over data collection
- **Disclosure Requirements**: Transparent data practices
- **Deletion Rights**: User data deletion capabilities

### Compliance Improvements

**Immediate Actions**:
1. **Robots.txt Enforcement**: Implement automatic compliance checking
2. **Rate Limiting**: Add configurable crawl delays
3. **PII Monitoring**: Enhanced detection and reporting
4. **Access Control**: Implement proper authentication

**Short-term Goals**:
1. **Compliance Dashboard**: Real-time compliance monitoring
2. **Automated Auditing**: Regular compliance checks
3. **Incident Response**: Automated alerting and response
4. **Policy Management**: Centralized compliance policy management

**Long-term Vision**:
1. **SOC 2 Compliance**: Security and availability controls
2. **ISO 27001**: Information security management
3. **GDPR Compliance**: Full data protection compliance
4. **Industry Standards**: Adherence to industry best practices

## Security Checklist

### Pre-Production Security

- [ ] API keys stored in environment variables only
- [ ] Output directories have proper permissions
- [ ] PII detection and redaction enabled
- [ ] Compliance monitoring configured
- [ ] Security event logging active
- [ ] Incident response procedures documented
- [ ] Legal review completed

### Ongoing Security

- [ ] Daily PII detection review
- [ ] Weekly compliance audit
- [ ] Monthly security assessment
- [ ] Quarterly policy review
- [ ] Annual external audit
- [ ] Regular key rotation
- [ ] Continuous monitoring

### Emergency Procedures

- [ ] Security incident response plan
- [ ] Compliance violation procedures
- [ ] Data breach notification process
- [ ] System shutdown procedures
- [ ] Communication protocols
- [ ] Recovery procedures
- [ ] Post-incident review process

## Resources & References

### Security Tools

- **Static Analysis**: Bandit for Python security scanning
- **Dependency Scanning**: Safety for package vulnerability checking
- **Code Quality**: Flake8 for style and security checks
- **Testing**: Pytest with security-focused test cases

### Compliance Resources

- **Robots.txt**: https://www.robotstxt.org/
- **GDPR Guidelines**: https://gdpr.eu/
- **CCPA Information**: https://oag.ca.gov/privacy/ccpa
- **Web Scraping Ethics**: https://www.scrapingbee.com/blog/web-scraping-ethics/

### Security Standards

- **OWASP Top 10**: Web application security risks
- **NIST Cybersecurity Framework**: Security best practices
- **ISO 27001**: Information security management
- **SOC 2**: Security and availability controls

## Contact Information

### Security Team

- **Security Officer**: security@growthsignal.ai
- **Compliance Officer**: compliance@growthsignal.ai
- **Emergency Contact**: +1 (555) 123-4567

### Response Times

- **Critical Issues**: 1 hour
- **High Severity**: 4 hours
- **Medium Severity**: 24 hours
- **Low Severity**: 72 hours

### Reporting Channels

- **Security Issues**: security@growthsignal.ai
- **Compliance Violations**: compliance@growthsignal.ai
- **Emergency Incidents**: +1 (555) 123-4567
- **Anonymous Reports**: https://growthsignal.ai/security/report
