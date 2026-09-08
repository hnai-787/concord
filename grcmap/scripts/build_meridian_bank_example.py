import yaml

BASE = "."

CONTROLS = [
    ("GOV-01", "Security governance program", "CISO Office"),
    ("GOV-02", "Risk management strategy and appetite", "CISO Office"),
    ("IAM-01", "Identity lifecycle management", "IAM Team"),
    ("IAM-02", "Multi-factor authentication", "IAM Team"),
    ("IAM-03", "Privileged access management", "IAM Team"),
    ("NET-01", "Network segmentation", "Network Engineering"),
    ("NET-02", "Network security controls (firewalls/IDS)", "Network Engineering"),
    ("LOG-01", "Centralized logging and monitoring", "SOC"),
    ("LOG-02", "Clock synchronization", "Infrastructure"),
    ("VUL-01", "Vulnerability management", "Security Engineering"),
    ("VUL-02", "Penetration testing program", "Security Engineering"),
    ("SDLC-01", "Secure development lifecycle", "Engineering"),
    ("SDLC-02", "Change management", "Engineering"),
    ("BCP-01", "Business continuity planning", "Operational Resilience"),
    ("DR-01", "Disaster recovery / ICT resilience", "Operational Resilience"),
    ("TPRM-01", "Third-party / supplier risk management", "Procurement"),
    ("IR-01", "Incident response program", "SOC"),
    ("IR-02", "Incident evidence collection and forensics", "SOC"),
    ("DAT-01", "Encryption of data at rest and in transit", "Security Engineering"),
    ("DAT-02", "Data classification and labeling", "Data Governance"),
    ("DAT-03", "Data retention and secure disposal", "Data Governance"),
    ("PHY-01", "Physical access controls", "Facilities"),
    ("PHY-02", "Environmental protection of facilities", "Facilities"),
    ("HR-01", "Personnel screening", "Human Resources"),
    ("HR-02", "Security awareness training", "Human Resources"),
    ("CLD-01", "Cloud service security", "Cloud Platform Team"),
    ("CFG-01", "Secure configuration baseline management", "Infrastructure"),
    ("MAL-01", "Malware protection", "Security Engineering"),
    ("AST-01", "Asset inventory management", "IT Operations"),
    ("AUD-01", "Independent security review / internal audit", "Internal Audit"),
    ("PRIV-01", "Privacy and PII protection", "Data Governance"),
    ("CRY-01", "Cryptographic key management", "Security Engineering"),
    ("WEB-01", "Web / application filtering", "Network Engineering"),
]

IMPLEMENTATION = {
    "GOV-01": ("implemented", ["policy/ISMS-Charter", "policy/InfoSec-Policy-v3"], None),
    "GOV-02": ("partial", ["register/enterprise-risk-register"], "Risk appetite statement approved; quantitative risk scoring model still in pilot."),
    "IAM-01": ("partial", ["procedure/joiner-mover-leaver", "system/identity-governance-tool"], "Joiner/leaver automation complete; contractor offboarding process still manual."),
    "IAM-02": ("implemented", ["config/mfa-enforcement-policy"], None),
    "IAM-03": ("planned", ["project/pam-rollout-2027"], "Privileged access management tool selected; deployment scheduled for next fiscal year."),
    "NET-01": ("implemented", ["diagram/network-segmentation-2026"], None),
    "NET-02": ("implemented", ["config/firewall-ruleset", "config/ids-deployment"], None),
    "LOG-01": ("partial", ["system/siem-deployment"], "Core banking and network devices centrally logged; some legacy branch systems not yet integrated."),
    "LOG-02": ("implemented", ["config/ntp-baseline"], None),
    "VUL-01": ("implemented", ["report/monthly-vuln-scan"], None),
    "VUL-02": ("planned", ["contract/pentest-vendor-2027"], "Annual penetration test scoped; contract execution pending budget approval."),
    "SDLC-01": ("partial", ["procedure/secure-sdlc"], "Security requirements and code review mandatory for new projects; legacy applications not yet retrofitted."),
    "SDLC-02": ("implemented", ["procedure/change-advisory-board"], None),
    "BCP-01": ("implemented", ["plan/business-continuity-plan-2026"], None),
    "DR-01": ("partial", ["plan/dr-runbook", "report/dr-test-2025"], "DR site operational for core banking; last full failover test predates online banking platform migration."),
    "TPRM-01": ("not_implemented", [], None),
    "IR-01": ("implemented", ["plan/incident-response-plan"], None),
    "IR-02": ("alternative", ["procedure/manual-evidence-handling"], "No dedicated forensics tooling; evidence collection follows a documented manual chain-of-custody procedure instead."),
    "DAT-01": ("implemented", ["config/encryption-standards"], None),
    "DAT-02": ("partial", ["policy/data-classification"], "Classification scheme defined and applied to new data stores; historical data inventory tagging in progress."),
    "DAT-03": ("not_implemented", [], None),
    "PHY-01": ("implemented", ["procedure/badge-access-control"], None),
    "PHY-02": ("implemented", ["report/datacenter-environmental-controls"], None),
    "HR-01": ("implemented", ["procedure/pre-employment-screening"], None),
    "HR-02": ("partial", ["report/awareness-training-completion-2026"], "Mandatory annual training deployed; completion rate 78% as of last reporting cycle."),
    "CLD-01": ("partial", ["policy/cloud-security-baseline"], "Baseline security configuration enforced for new cloud workloads; legacy workloads migrated pre-policy not yet reassessed."),
    "CFG-01": ("implemented", ["config/hardening-baseline"], None),
    "MAL-01": ("implemented", ["config/endpoint-protection-deployment"], None),
    "AST-01": ("partial", ["system/cmdb"], "Server and network asset inventory automated; end-user device inventory partially manual."),
    "AUD-01": ("implemented", ["report/internal-audit-plan-2026"], None),
    "PRIV-01": ("implemented", ["policy/data-privacy-policy"], None),
    "CRY-01": ("implemented", ["procedure/key-management-standard"], None),
    # WEB-01 deliberately has NO implementation record -- exercises the
    # "mapped but no recorded implementation" -> GAP path.
}

# (source_control, target_framework, target_control, relationship, rationale, notes)
MAPPINGS = [
    ("GOV-01", "iso27001-2022", "A.5.1", "equal", "semantic", None),
    ("GOV-01", "nist-csf-2.0", "GV.PO-01", "superset", "functional", "Governance program establishes policy beyond the single NIST outcome."),
    ("GOV-01", "sbp-etgrm-2017", "1", "equal", "semantic", None),
    ("GOV-01", "pci-dss-4.0.1", "12", "superset", "functional", None),

    ("GOV-02", "iso27001-2022", "A.5.4", "intersects", "functional", "Management responsibility overlaps but risk appetite setting is broader."),
    ("GOV-02", "nist-csf-2.0", "GV.RM-02", "equal", "semantic", None),
    ("GOV-02", "sbp-etgrm-2017", "1", "subset", "functional", None),

    ("IAM-01", "iso27001-2022", "A.5.16", "superset", "functional", "Covers identity management plus full lifecycle automation."),
    ("IAM-01", "iso27001-2022", "A.5.18", "intersects", "functional", None),
    ("IAM-01", "nist-csf-2.0", "PR.AA-01", "superset", "functional", None),
    ("IAM-01", "pci-dss-4.0.1", "7", "intersects", "functional", "Contributes to need-to-know access restriction, alongside privileged access management."),
    ("IAM-01", "sbp-etgrm-2017", "2", "subset", "functional", None),

    ("IAM-02", "iso27001-2022", "A.8.5", "equal", "semantic", None),
    ("IAM-02", "nist-csf-2.0", "PR.AA-03", "superset", "functional", None),
    ("IAM-02", "pci-dss-4.0.1", "8", "intersects", "functional", "MFA satisfies part of Requirement 8's authentication controls."),

    ("IAM-03", "iso27001-2022", "A.8.2", "equal", "semantic", None),
    ("IAM-03", "nist-csf-2.0", "PR.AA-05", "superset", "functional", None),
    ("IAM-03", "pci-dss-4.0.1", "7", "intersects", "functional", "Contributes to need-to-know access restriction, alongside identity lifecycle management."),

    ("NET-01", "iso27001-2022", "A.8.22", "equal", "semantic", None),
    ("NET-01", "nist-csf-2.0", "PR.IR-01", "intersects", "functional", None),
    ("NET-01", "pci-dss-4.0.1", "1", "intersects", "functional", "Segmentation reduces cardholder data environment scope; does not alone satisfy all of Requirement 1."),

    ("NET-02", "iso27001-2022", "A.8.20", "equal", "semantic", None),
    ("NET-02", "nist-csf-2.0", "PR.IR-01", "intersects", "functional", None),
    ("NET-02", "pci-dss-4.0.1", "1", "superset", "functional", "Firewall/IDS deployment covers the core network security control requirement."),
    ("NET-02", "sbp-etgrm-2017", "2", "subset", "functional", None),

    ("LOG-01", "iso27001-2022", "A.8.15", "equal", "semantic", None),
    ("LOG-01", "iso27001-2022", "A.8.16", "intersects", "functional", None),
    ("LOG-01", "nist-csf-2.0", "DE.CM-01", "superset", "functional", None),
    ("LOG-01", "pci-dss-4.0.1", "10", "subset", "functional", "Centralized logging covers most, but not all, of Requirement 10 without clock sync (see LOG-02) and coverage-assertions.yaml."),

    ("LOG-02", "iso27001-2022", "A.8.17", "equal", "semantic", None),
    ("LOG-02", "pci-dss-4.0.1", "10", "subset", "functional", "Clock synchronization is a distinct sub-element of Requirement 10's log integrity requirements."),

    ("VUL-01", "iso27001-2022", "A.8.8", "equal", "semantic", None),
    ("VUL-01", "nist-csf-2.0", "ID.RA-01", "superset", "functional", None),
    ("VUL-01", "pci-dss-4.0.1", "11", "intersects", "functional", "Vulnerability scanning is part of, not all of, Requirement 11's testing scope."),

    ("VUL-02", "iso27001-2022", "A.8.8", "intersects", "functional", None),
    ("VUL-02", "nist-csf-2.0", "ID.RA-01", "intersects", "functional", None),
    ("VUL-02", "pci-dss-4.0.1", "11", "intersects", "functional", "Penetration testing is part of, not all of, Requirement 11's testing scope."),

    ("SDLC-01", "iso27001-2022", "A.8.25", "equal", "semantic", None),
    ("SDLC-01", "iso27001-2022", "A.8.28", "intersects", "functional", None),
    ("SDLC-01", "nist-csf-2.0", "PR.PS-06", "superset", "functional", None),
    ("SDLC-01", "pci-dss-4.0.1", "6", "subset", "functional", None),

    ("SDLC-02", "iso27001-2022", "A.8.32", "equal", "semantic", None),
    ("SDLC-02", "nist-csf-2.0", "PR.PS-01", "intersects", "functional", None),
    ("SDLC-02", "pci-dss-4.0.1", "6", "subset", "functional", None),

    ("BCP-01", "iso27001-2022", "A.5.29", "superset", "functional", None),
    ("BCP-01", "iso27001-2022", "A.5.30", "intersects", "functional", None),
    ("BCP-01", "nist-csf-2.0", "RC.RP-01", "superset", "functional", None),
    ("BCP-01", "sbp-etgrm-2017", "5", "subset", "functional", "Contributes to, but does not alone satisfy, the full BCP/DR domain -- see DR-01 and coverage-assertions.yaml."),

    ("DR-01", "iso27001-2022", "A.5.30", "superset", "functional", None),
    ("DR-01", "nist-csf-2.0", "RC.RP-01", "intersects", "functional", None),
    ("DR-01", "sbp-etgrm-2017", "5", "subset", "functional", "Contributes to, but does not alone satisfy, the full BCP/DR domain -- see BCP-01 and coverage-assertions.yaml."),

    ("TPRM-01", "iso27001-2022", "A.5.19", "equal", "semantic", None),
    ("TPRM-01", "iso27001-2022", "A.5.20", "intersects", "functional", None),
    ("TPRM-01", "nist-csf-2.0", "GV.SC-01", "superset", "functional", None),
    ("TPRM-01", "sbp-etgrm-2017", "1", "subset", "functional", None),

    ("IR-01", "iso27001-2022", "A.5.24", "equal", "semantic", None),
    ("IR-01", "iso27001-2022", "A.5.26", "intersects", "functional", None),
    ("IR-01", "nist-csf-2.0", "RS.MA-01", "superset", "functional", None),
    ("IR-01", "pci-dss-4.0.1", "12", "intersects", "functional", None),
    ("IR-01", "sbp-etgrm-2017", "2", "subset", "functional", None),

    ("IR-02", "iso27001-2022", "A.5.28", "equal", "semantic", None),
    ("IR-02", "nist-csf-2.0", "RS.AN-03", "intersects", "functional", None),

    ("DAT-01", "iso27001-2022", "A.8.24", "equal", "semantic", None),
    ("DAT-01", "nist-csf-2.0", "PR.DS-01", "superset", "functional", None),
    ("DAT-01", "pci-dss-4.0.1", "3", "intersects", "functional", "Encryption at rest addresses part of Requirement 3's stored-account-data protections."),
    ("DAT-01", "pci-dss-4.0.1", "4", "superset", "functional", "Encryption in transit fully covers Requirement 4's transmission-protection scope."),

    ("DAT-02", "iso27001-2022", "A.5.12", "equal", "semantic", None),
    ("DAT-02", "nist-csf-2.0", "ID.AM-05", "intersects", "functional", None),

    ("DAT-03", "iso27001-2022", "A.8.10", "equal", "semantic", None),
    ("DAT-03", "nist-csf-2.0", "PR.DS-01", "intersects", "functional", None),
    ("DAT-03", "pci-dss-4.0.1", "3", "intersects", "functional", "Secure disposal addresses part of Requirement 3's stored-account-data protections."),

    ("PHY-01", "iso27001-2022", "A.7.2", "equal", "semantic", None),
    ("PHY-01", "pci-dss-4.0.1", "9", "intersects", "functional", None),
    ("PHY-01", "sbp-etgrm-2017", "2", "subset", "functional", None),

    ("PHY-02", "iso27001-2022", "A.7.5", "equal", "semantic", None),
    ("PHY-02", "pci-dss-4.0.1", "9", "intersects", "functional", None),

    ("HR-01", "iso27001-2022", "A.6.1", "equal", "semantic", None),
    ("HR-01", "nist-csf-2.0", "GV.RR-04", "intersects", "functional", None),

    ("HR-02", "iso27001-2022", "A.6.3", "equal", "semantic", None),
    ("HR-02", "nist-csf-2.0", "PR.AT-01", "superset", "functional", None),
    ("HR-02", "pci-dss-4.0.1", "12", "intersects", "functional", None),

    ("CLD-01", "iso27001-2022", "A.5.23", "equal", "semantic", None),
    ("CLD-01", "nist-csf-2.0", "GV.SC-07", "intersects", "functional", None),

    ("CFG-01", "iso27001-2022", "A.8.9", "equal", "semantic", None),
    ("CFG-01", "nist-csf-2.0", "PR.PS-01", "superset", "functional", None),
    ("CFG-01", "pci-dss-4.0.1", "2", "superset", "functional", None),

    ("MAL-01", "iso27001-2022", "A.8.7", "equal", "semantic", None),
    ("MAL-01", "nist-csf-2.0", "DE.CM-09", "intersects", "functional", None),
    ("MAL-01", "pci-dss-4.0.1", "5", "superset", "functional", None),

    ("AST-01", "iso27001-2022", "A.5.9", "equal", "semantic", None),
    ("AST-01", "nist-csf-2.0", "ID.AM-01", "superset", "functional", None),
    ("AST-01", "pci-dss-4.0.1", "2", "intersects", "functional", None),

    ("AUD-01", "iso27001-2022", "A.5.35", "equal", "semantic", None),
    ("AUD-01", "nist-csf-2.0", "GV.OV-01", "intersects", "functional", None),
    ("AUD-01", "sbp-etgrm-2017", "6", "equal", "semantic", None),

    ("PRIV-01", "iso27001-2022", "A.5.34", "equal", "semantic", None),

    ("CRY-01", "iso27001-2022", "A.8.24", "intersects", "functional", "Key management is part of, not all of, cryptography use -- see DAT-01."),
    ("CRY-01", "pci-dss-4.0.1", "3", "intersects", "functional", None),

    ("WEB-01", "iso27001-2022", "A.8.23", "equal", "semantic", None),
    ("WEB-01", "pci-dss-4.0.1", "1", "intersects", "functional", None),
]

FRAMEWORK_FILES = {
    "iso27001-2022": "internal-to-iso.yaml",
    "pci-dss-4.0.1": "internal-to-pci.yaml",
    "nist-csf-2.0": "internal-to-nist.yaml",
    "sbp-etgrm-2017": "internal-to-sbp.yaml",
}

REVIEWER = "compliance-analyst"
REVIEW_DATE = "2026-09-08"


def build():
    # controls.yaml
    organization = {
        "id": "meridian-bank",
        "name": "Meridian Bank",
        "type": "fictional-commercial-bank",
        "jurisdiction": "PK",
        "disclaimer": (
            "Synthetic organization used for academic and software demonstration "
            "purposes. No control status represents any real institution."
        ),
    }
    controls_doc = {
        "organization": organization,
        "controls": [{"id": cid, "title": title, "owner": owner} for cid, title, owner in CONTROLS],
    }
    with open(f"{BASE}/examples/meridian-bank/controls.yaml", "w", encoding="utf-8") as f:
        yaml.dump(controls_doc, f, sort_keys=False, allow_unicode=True, width=100)

    # implementation.yaml
    impl_list = []
    for cid, title, owner in CONTROLS:
        if cid not in IMPLEMENTATION:
            continue
        state, evidence, notes = IMPLEMENTATION[cid]
        entry = {"control": cid, "state": state, "evidence": evidence}
        if notes:
            entry["notes"] = notes
        impl_list.append(entry)
    with open(f"{BASE}/examples/meridian-bank/implementation.yaml", "w", encoding="utf-8") as f:
        yaml.dump({"implementations": impl_list}, f, sort_keys=False, allow_unicode=True, width=100)

    # mappings, split by target framework
    by_framework: dict[str, list[dict]] = {fid: [] for fid in FRAMEWORK_FILES}
    counters: dict[str, int] = {fid: 0 for fid in FRAMEWORK_FILES}
    for source, framework, target, relationship, rationale, notes in MAPPINGS:
        counters[framework] += 1
        entry = {
            "id": f"map-{framework}-{counters[framework]:03d}",
            "source": source,
            "target": {"framework": framework, "control": target},
            "relationship": relationship,
            "rationale": rationale,
            "reviewed_by": REVIEWER,
            "reviewed_at": REVIEW_DATE,
        }
        if notes:
            entry["notes"] = notes
        by_framework[framework].append(entry)

    for framework, filename in FRAMEWORK_FILES.items():
        with open(f"{BASE}/mappings/{filename}", "w", encoding="utf-8") as f:
            yaml.dump({"mappings": by_framework[framework]}, f, sort_keys=False, allow_unicode=True, width=100)

    total_mappings = sum(len(v) for v in by_framework.values())
    print("controls:", len(CONTROLS))
    print("implementations:", len(impl_list))
    print("mappings:", total_mappings, {k: len(v) for k, v in by_framework.items()})


if __name__ == "__main__":
    build()
