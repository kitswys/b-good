# B-good: B-BBEE Procurement Control for Odoo

> A South African Odoo add-on for tracking supplier B-BBEE compliance, calculating recognised procurement spend, identifying evidence gaps, and preparing verification-ready procurement packs.

[![Status](https://img.shields.io/badge/status-planned-blue)](#project-status)
[![Platform](https://img.shields.io/badge/platform-Odoo-purple)](#odoo-integration)
[![Market](https://img.shields.io/badge/market-South%20Africa-green)](#business-context)
[![Domain](https://img.shields.io/badge/domain-B--BBEE%20Procurement-orange)](#domain-model)
[![Architecture](https://img.shields.io/badge/architecture-DDD-informational)](#domain-driven-design)

---

## Table of Contents

- [Overview](#overview)
- [Business Context](#business-context)
- [Important Disclaimer](#important-disclaimer)
- [Core Question](#core-question)
- [Primary Users](#primary-users)
- [MVP Scope](#mvp-scope)
- [Out of Scope for MVP](#out-of-scope-for-mvp)
- [Core Capabilities](#core-capabilities)
- [Odoo Integration](#odoo-integration)
- [Domain-Driven Design](#domain-driven-design)
- [Domain Model](#domain-model)
- [Key Domain Events](#key-domain-events)
- [Suggested Module Structure](#suggested-module-structure)
- [Data and Calculation Principles](#data-and-calculation-principles)
- [User Workflows](#user-workflows)
- [Security and Permissions](#security-and-permissions)
- [Reporting and Exports](#reporting-and-exports)
- [Installation](#installation)
- [Configuration](#configuration)
- [Development Setup](#development-setup)
- [Testing Strategy](#testing-strategy)
- [Roadmap](#roadmap)
- [Commercial Positioning](#commercial-positioning)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

**B-good** is the working name for an Odoo add-on focused on the **Preferential Procurement / Enterprise & Supplier Development** area of South African B-BBEE management.

The product name is:

## B-BBEE Procurement Control for Odoo

The module helps companies monitor whether they are buying from the right suppliers, whether supplier evidence is valid, and how current procurement behaviour affects recognised procurement spend.

It is designed for organisations that want operational visibility before year-end, rather than discovering B-BBEE procurement gaps only during verification.

---

## Business Context

South African companies often need to manage B-BBEE procurement performance across many suppliers, documents, spend categories, and measurement periods.

In practice, this creates recurring operational problems:

- Supplier certificates expire without procurement teams noticing.
- Vendor master data does not clearly show B-BBEE recognition status.
- Spend is recorded in accounting, but not interpreted for procurement scorecard purposes.
- Procurement teams only discover missing evidence when a consultant or verification agency requests proof.
- Buyers may continue using suppliers that weaken recognised procurement performance.
- Reports are often prepared manually in spreadsheets.

This module aims to bring those controls into Odoo.

---

## Important Disclaimer

This module **does not certify B-BBEE status**.

It is not a replacement for an accredited B-BBEE verification agency, legal adviser, transformation consultant, or official regulatory interpretation.

The purpose of this module is to support:

- Operational control
- Internal score visibility
- Supplier evidence management
- Procurement risk detection
- Reporting preparation
- Evidence pack preparation

Final B-BBEE verification and certification remain the responsibility of accredited B-BBEE verification professionals.

---

## Core Question

The product helps a company answer:

> Are we buying enough from the right suppliers, and do we have the evidence to prove it?

---

## Primary Users

| User | Main Need |
| --- | --- |
| Procurement Manager | Understand supplier compliance before buying decisions are made |
| Buyer | Receive warnings when selecting risky or non-compliant suppliers |
| Finance User | Import posted vendor bills and credit notes into procurement spend batches |
| Transformation Officer | Monitor recognised spend, shortfalls, and procurement scorecard risk |
| B-BBEE Consultant | Review data, identify gaps, and prepare supporting evidence |
| Auditor / Verifier Support User | Export schedules, certificates, exception notes, and audit logs |
| System Administrator | Configure rules, permissions, notifications, and measurement periods |

---

## MVP Scope

The first sellable version focuses on **supplier compliance, procurement spend, basic score visibility, missing evidence, and exports**.

| Feature | MVP |
| --- | --- |
| Supplier B-BBEE profile | Yes |
| Certificate / affidavit upload | Yes |
| Certificate expiry tracking | Yes |
| Recognition percentage capture | Yes |
| Vendor bill import from Odoo Accounting | Yes |
| Measurement period setup | Yes |
| Basic recognised spend calculation | Yes |
| Dashboard showing spend, recognised spend, and shortfall | Yes |
| Missing evidence report | Yes |
| Expiring certificate alerts | Yes |
| Excel / PDF export | Yes |
| Buyer warning on RFQ / PO | Yes |

---

## Out of Scope for MVP

The MVP deliberately avoids features that would make the first release too broad or legally sensitive.

| Feature | Reason |
| --- | --- |
| Full B-BBEE scorecard | Too broad for version 1 |
| Automatic legal certification | Out of product scope |
| Automatic certificate verification | Requires trusted external data sources |
| Full Enterprise and Supplier Development contribution management | Phase 2 |
| AI recommendations | Phase 2 or Phase 3 |
| Complex sector-code engine | Phase 2 |
| Final verification outcome | Must remain outside the module |

---

## Core Capabilities

### Supplier B-BBEE Tracking

The module extends Odoo vendor records with B-BBEE procurement fields, including:

- B-BBEE level
- Recognition percentage
- Certificate or affidavit type
- Certificate number
- Issue date
- Expiry date
- Black ownership percentage
- Black women ownership percentage
- Empowering supplier status
- Evidence attachment
- Supplier compliance status

### Certificate Management

The module manages supplier B-BBEE documents throughout their lifecycle:

- Upload certificate or affidavit
- Store document against supplier
- Track expiry date
- Mark documents as valid, expiring soon, expired, missing, or superseded
- Preserve superseded documents for audit history
- Warn users before expiry
- Report missing or invalid evidence

### Procurement Spend Tracking

The module imports posted accounting transactions from Odoo Accounting.

Supported source transactions:

- Posted vendor bills
- Posted vendor credit notes

The module must **not mutate original accounting records**. It imports a snapshot of relevant spend information for B-BBEE reporting and audit traceability.

### Recognised Spend Calculation

Recognised procurement spend is calculated using:

```text
Recognised Spend = Included Spend × Supplier Recognition Percentage
```

Example:

```text
Included Spend: R100,000
Supplier Recognition: 125%
Recognised Spend: R125,000
```

### Measurement Period Control

All calculations are grouped by a configured measurement period.

A measurement period normally maps to a financial year or B-BBEE assessment period.

Each period can have:

- Start date
- End date
- Measured entity
- Active rule set
- Spend batches
- Scorecard assessments
- Evidence packs

### Procurement Dashboard

The dashboard should show:

- Total measured procurement spend
- Recognised procurement spend
- Target percentage
- Achieved percentage
- Available points
- Actual points
- Shortfall
- Suppliers with missing evidence
- Suppliers with expired certificates
- Suppliers with certificates expiring soon
- High-risk procurement spend

### Missing Evidence Reporting

The module must identify spend lines where evidence is not verification-ready.

Examples:

- Supplier has no certificate
- Certificate expired before transaction date
- Affidavit missing
- Document not attached
- Supplier profile incomplete
- Spend marked as requiring review

### Expiry Alerts

The module should alert users before supplier documents expire.

Recommended alert windows:

- 90 days before expiry
- 60 days before expiry
- 30 days before expiry
- On expiry
- After expiry, until replaced or superseded

### Evidence Pack Export

The evidence pack should help users prepare for B-BBEE verification discussions.

A pack may include:

- Supplier certificate list
- Certificate files
- Spend schedule by supplier
- Spend schedule by recognition level
- Missing evidence report
- Exception register
- Manual override list
- Audit log
- Generated PDF summary
- Excel workbook export
- Optional ZIP package of documents

### Buyer Warning

When a buyer selects a supplier on an RFQ or purchase order, the module should warn the buyer if the supplier has procurement risk.

Examples:

- Supplier certificate expired
- Supplier certificate missing
- Supplier marked non-compliant
- Supplier recognition percentage is low
- Supplier profile has incomplete compliance information

The module should warn and inform. It should not automatically change the buyer’s procurement decision.

---

## Odoo Integration

| Odoo App | Integration |
| --- | --- |
| Contacts | Extend vendor records with B-BBEE compliance fields |
| Purchase | Show warnings during RFQ / PO creation |
| Accounting | Import posted vendor bills and credit notes |
| Documents / Attachments | Store certificates, affidavits, and evidence |
| Approvals | Optional approval workflow for overrides and later ESD contributions |
| Reporting | Dashboards, pivot views, Excel exports, PDF exports |
| Email / Discuss | Notifications for expiring certificates and missing evidence |

Optional future integrations:

| Odoo App | Future Use |
| --- | --- |
| Inventory | Link procurement categories to product categories |
| Projects | Track supplier development initiatives |
| CRM | Support supplier onboarding or transformation campaigns |
| Website / Portal | Allow suppliers to upload their own certificates |

---

## Domain-Driven Design

The module is structured using Domain-Driven Design principles.

The goal is to keep B-BBEE procurement logic understandable, testable, and isolated from Odoo implementation complexity.

### Bounded Contexts

| Bounded Context | Responsibility |
| --- | --- |
| Supplier Compliance | Understand each supplier’s B-BBEE status and evidence |
| Procurement Spend | Import and classify procurement spend |
| Scorecard Calculation | Calculate recognised spend, achieved percentage, points, and shortfalls |
| Evidence & Verification | Prepare reports, documents, exception lists, and audit packs |
| Procurement Optimisation | Produce warnings and future recommendations |
| Rules Configuration | Manage versioned scorecard rules and targets |
| Odoo Integration | Protect domain logic from Odoo-specific technical details |

---

## Domain Model

### SupplierComplianceProfile

Owns the supplier’s B-BBEE compliance status.

Important fields:

| Field | Description |
| --- | --- |
| Supplier | Linked Odoo vendor |
| B-BBEE level | Level 1 to 8 or non-compliant |
| Recognition percentage | Example: 135%, 125%, 100%, 80% |
| Certificate type | Certificate, affidavit, or none |
| Certificate number | Optional reference number |
| Issue date | Date document was issued |
| Expiry date | Date document expires |
| Black ownership % | Optional |
| Black women ownership % | Optional |
| Empowering supplier status | Yes, No, or Unknown |
| Document attachment | Certificate or affidavit file |
| Status | Valid, Expiring Soon, Expired, Missing, or Superseded |

Business rules:

- A supplier may not have two active certificates for the same period.
- Expired certificates must not count as valid evidence.
- Superseded certificates must remain available for audit history.
- Missing or expired certificates must trigger procurement risk warnings.

### ProcurementSpendBatch

Owns imported procurement spend snapshots for a measurement period.

Important fields:

| Field | Description |
| --- | --- |
| Measurement period | Period being assessed |
| Supplier | Linked vendor |
| Source transaction | Vendor bill or credit note |
| Invoice date | Accounting date |
| Untaxed amount | Amount excluding VAT |
| Excluded amount | Amount excluded from calculation |
| Included amount | Amount included in calculation |
| Recognition percentage | Pulled from supplier profile |
| Recognised spend | Included amount × recognition percentage |
| Evidence status | Valid, Missing, Expired, or Review Required |

Business rules:

- Only posted accounting entries should be imported.
- Original accounting records must not be changed.
- Imported spend should be snapshotted for audit purposes.
- Users may classify spend as included, excluded, or requiring review.
- Locked spend batches may not be edited; they may only be superseded.

### ScorecardAssessment

Owns the calculated procurement performance for a measured entity and period.

Important fields:

| Field | Description |
| --- | --- |
| Measured entity | Company being assessed |
| Measurement period | Assessment period |
| Rule set | Generic, sector, or custom |
| Total measured procurement spend | All included procurement spend |
| Recognised procurement spend | Spend after recognition percentage is applied |
| Target percentage | Configured target |
| Achieved percentage | Actual recognised spend percentage |
| Available points | Configured points |
| Actual points | Calculated points |
| Shortfall | Gap to target |
| Status | Draft, Calculated, Approved, or Frozen |

Business rules:

- A scorecard assessment must reference one measurement period.
- A scorecard assessment must reference one active rule set.
- Frozen assessments may not be changed.
- Recalculation must be possible while the assessment is still draft.
- Any shortfall must create a warning or recommendation.

### EvidencePack

Owns verification-supporting exports and document collections.

Contents:

| Item | Description |
| --- | --- |
| Supplier certificates | Valid supplier B-BBEE documents |
| Spend schedule | Spend by supplier and recognition level |
| Missing evidence report | Suppliers or spend without valid evidence |
| Exception register | Manual overrides or exclusions |
| Audit log | Who changed what and when |
| Export package | Excel, PDF, or ZIP format |

Business rules:

- A frozen evidence pack may not be edited.
- Evidence packs must be versioned.
- Missing documents must be clearly reported.
- Every exported pack must show the measurement period and generation date.

### ProcurementRecommendation

Owns procurement warnings and optional future supplier recommendations.

Important fields:

| Field | Description |
| --- | --- |
| Current supplier | Supplier currently used |
| Current recognition % | Current supplier recognition |
| Alternative supplier | Optional recommended supplier |
| Alternative recognition % | Better supplier recognition |
| Estimated score impact | Estimated improvement |
| Price impact | Optional cost difference |
| Status | New, Accepted, or Dismissed |

Business rules:

- Recommendations must never automatically change purchase orders.
- Buyer must remain in control.
- Warnings should appear before confirming RFQs or POs.
- Dismissed recommendations must store a reason.

### ScorecardRuleSet

Owns configurable rules and targets.

Important fields:

| Field | Description |
| --- | --- |
| Rule set name | Generic, QSE, sector-specific, or custom |
| Effective date | Start date |
| Expiry date | Optional |
| Procurement targets | Target percentages |
| Available points | Points per indicator |
| Recognition rules | How spend is recognised |
| Status | Draft, Active, or Retired |

Business rules:

- Rules must be versioned.
- Only one rule set may be active for the same company, type, and date range unless explicitly allowed.
- Calculated assessments must remember which rule set was used.

---

## Key Domain Events

| Event | Trigger | Possible Reaction |
| --- | --- | --- |
| SupplierCertificateUploaded | User uploads certificate | Recalculate supplier status |
| SupplierCertificateExpired | Expiry date passes | Warn buyer and compliance users |
| SupplierCertificateExpiringSoon | 30 / 60 / 90 days before expiry | Notify supplier owner or procurement team |
| VendorBillPosted | Vendor bill becomes posted | Make spend available for import |
| SpendImported | Spend enters assessment batch | Recalculate recognised spend |
| SpendBatchLocked | Batch is finalised | Prevent further edits |
| ScorecardCalculated | Assessment is recalculated | Update dashboard |
| ScorecardShortfallDetected | Score is below target | Create warning or recommendation |
| EvidenceMissingDetected | Spend lacks valid documentation | Add to missing evidence report |
| EvidencePackGenerated | Evidence pack is created | Record export history |
| EvidencePackFrozen | Evidence pack is locked | Prevent changes |
| HighRiskSupplierSelected | Buyer selects expired or missing supplier | Show warning on RFQ / PO |

---

## Suggested Module Structure

The internal structure should keep domain concerns separate, even though Odoo models may still be implemented in standard Odoo style.

```text
bbbbee_procurement/
  __init__.py
  __manifest__.py

  models/
    supplier_compliance/
      supplier_profile.py
      supplier_certificate.py
      supplier_status_policy.py

    procurement_spend/
      spend_batch.py
      spend_line.py
      spend_classifier.py

    scorecard/
      scorecard_assessment.py
      scorecard_indicator.py
      scorecard_rule_set.py
      scorecard_calculator.py

    evidence/
      evidence_pack.py
      evidence_item.py
      evidence_exporter.py
      evidence_completeness_checker.py

    optimisation/
      procurement_recommendation.py
      supplier_risk_service.py

    integration/
      odoo_vendor_adapter.py
      odoo_purchase_adapter.py
      odoo_accounting_adapter.py

  security/
    ir.model.access.csv
    security_groups.xml
    record_rules.xml

  views/
    supplier_profile_views.xml
    supplier_certificate_views.xml
    spend_batch_views.xml
    spend_line_views.xml
    scorecard_assessment_views.xml
    evidence_pack_views.xml
    dashboard_views.xml
    purchase_order_views.xml
    menu_views.xml

  data/
    scheduled_actions.xml
    mail_templates.xml
    default_rule_sets.xml

  reports/
    evidence_pack_report.xml
    missing_evidence_report.xml
    spend_schedule_report.xml

  wizards/
    import_spend_wizard.py
    generate_evidence_pack_wizard.py
    recalculate_scorecard_wizard.py

  tests/
    test_supplier_compliance.py
    test_certificate_expiry.py
    test_spend_import.py
    test_recognised_spend.py
    test_scorecard_calculation.py
    test_evidence_pack.py
```

---

## Data and Calculation Principles

### Accounting Data Must Not Be Mutated

The module imports a snapshot from Odoo Accounting.

It must not change:

- Posted vendor bills
- Posted credit notes
- Journal entries
- Accounting balances
- Tax records

### Spend Must Be Traceable

Every calculated recognised spend value must trace back to:

- Measurement period
- Supplier
- Source accounting transaction
- Included / excluded amount
- Recognition percentage used
- Supplier evidence status
- Rule set used
- User who imported or recalculated
- Timestamp

### Calculations Must Be Reproducible

Frozen or approved assessments should retain the rule set and recognition data used at the time of calculation.

Later supplier certificate changes should not silently rewrite old frozen results.

### Missing Evidence Must Be Visible

The system should never hide missing evidence.

If spend exists without valid supporting documents, the dashboard and reports must make this clear.

---

## User Workflows

### 1. Capture Supplier B-BBEE Profile

1. Open vendor record.
2. Add B-BBEE level and recognition percentage.
3. Upload certificate or affidavit.
4. Capture issue and expiry dates.
5. Save profile.
6. System calculates status: Valid, Expiring Soon, Expired, Missing, or Superseded.

### 2. Import Procurement Spend

1. Select measurement period.
2. Run vendor bill import.
3. System imports posted vendor bills and credit notes.
4. System links spend to suppliers.
5. System snapshots recognition percentage.
6. User reviews included, excluded, and review-required spend.

### 3. Calculate Recognised Spend

1. Select measurement period or assessment.
2. Click Recalculate.
3. System applies supplier recognition percentages.
4. System calculates total included spend.
5. System calculates recognised procurement spend.
6. System identifies shortfalls.

### 4. Review Missing Evidence

1. Open Missing Evidence report.
2. Review suppliers with missing or expired evidence.
3. Upload missing documents.
4. Mark exceptions where needed.
5. Recalculate dashboard.

### 5. Warn Buyer During RFQ / PO

1. Buyer creates RFQ or purchase order.
2. Buyer selects supplier.
3. System checks supplier compliance status.
4. If risky, system shows warning.
5. Buyer may continue if permitted by policy.
6. Override reason may be captured.

### 6. Generate Evidence Pack

1. Select measurement period.
2. Generate evidence pack.
3. System collects certificates, spend schedules, missing evidence, exceptions, and audit logs.
4. User exports Excel, PDF, or ZIP.
5. Pack may be frozen for audit traceability.

---

## Security and Permissions

Suggested Odoo security groups:

| Group | Access |
| --- | --- |
| B-BBEE User | Read dashboards and supplier compliance status |
| B-BBEE Procurement User | View supplier warnings and procurement risk |
| B-BBEE Compliance Officer | Manage supplier certificates and evidence |
| B-BBEE Finance User | Import and review procurement spend |
| B-BBEE Manager | Approve assessments, freeze batches, export evidence packs |
| B-BBEE Administrator | Configure rule sets, periods, thresholds, and security |

Security expectations:

- Only authorised users may change recognition percentages.
- Only authorised users may upload or supersede certificates.
- Spend imported from Accounting should be visible according to finance permissions.
- Frozen assessments and evidence packs should be locked.
- Manual overrides must be audited.

---

## Reporting and Exports

Recommended reports:

| Report | Purpose |
| --- | --- |
| Supplier Compliance Register | List supplier B-BBEE status and certificate expiry |
| Expiring Certificates Report | Show certificates expiring in selected time window |
| Missing Evidence Report | Show suppliers and spend lines without valid evidence |
| Procurement Spend Schedule | List included, excluded, and recognised spend |
| Recognition Level Summary | Summarise spend by supplier B-BBEE level |
| Scorecard Dashboard | Show achieved percentage, target, points, and shortfall |
| Exception Register | Show overrides, exclusions, and reasons |
| Evidence Pack Export | Package documents and schedules for verification support |

Suggested export formats:

- XLSX
- PDF
- ZIP
- CSV, optional

---

## Installation

> Exact installation may vary depending on your Odoo deployment method.

### 1. Copy the Add-on

Copy the module into your Odoo custom add-ons directory.

```bash
cp -R bbbbee_procurement /path/to/odoo/custom_addons/
```

### 2. Update Odoo Add-ons Path

Ensure your Odoo configuration includes the custom add-ons path.

```ini
addons_path = /path/to/odoo/addons,/path/to/odoo/custom_addons
```

### 3. Restart Odoo

```bash
sudo systemctl restart odoo
```

For Docker-based environments:

```bash
docker compose restart odoo
```

### 4. Update App List

In Odoo:

```text
Apps → Update Apps List
```

### 5. Install the Module

Search for:

```text
B-BBEE Procurement Control
```

Then click **Install**.

---

## Configuration

After installation, configure the module in this order:

### 1. Security Groups

Assign users to the correct B-BBEE groups.

### 2. Measurement Period

Create a measurement period.

Example:

```text
Name: FY2026 B-BBEE Measurement Period
Start Date: 2025-07-01
End Date: 2026-06-30
Measured Entity: Your Company
Status: Draft
```

### 3. Rule Set

Create or activate a scorecard rule set.

Example:

```text
Rule Set: Generic Procurement MVP
Target Percentage: configurable
Available Points: configurable
Status: Active
```

### 4. Alert Thresholds

Configure expiry warning thresholds.

Recommended defaults:

```text
90 days
60 days
30 days
0 days
```

### 5. Supplier Profiles

Update vendor records with B-BBEE data and upload supporting evidence.

### 6. Scheduled Jobs

Enable scheduled actions for:

- Certificate expiry checks
- Expiring certificate notifications
- Missing evidence scans
- Optional automatic spend availability checks

---

## Development Setup

### Requirements

Recommended baseline:

- Odoo Community or Enterprise
- PostgreSQL
- Python version compatible with your Odoo version
- Access to Odoo Accounting and Purchase modules
- Custom add-ons directory
- Git

Optional Python dependencies for exports:

```bash
pip install xlsxwriter openpyxl
```

### Clone Repository

```bash
git clone https://github.com/your-org/b-good.git
cd b-good
```

### Example Development Layout

```text
b-good/
  addons/
    bbbbee_procurement/
  docker-compose.yml
  README.md
```

### Run Odoo in Development

Example Docker command:

```bash
docker compose up -d
```

Then open:

```text
http://localhost:8069
```

---

## Testing Strategy

### Unit Tests

Test domain rules independently where possible.

Recommended tests:

- Supplier cannot have two active certificates for same period.
- Expired certificate is not treated as valid evidence.
- Superseded certificate remains available for audit.
- Recognition spend calculation works correctly.
- Locked spend batch cannot be edited.
- Frozen evidence pack cannot be changed.
- Missing evidence is detected correctly.

### Integration Tests

Test Odoo workflows:

- Vendor profile extension
- Certificate upload
- Posted vendor bill import
- Credit note handling
- RFQ / PO supplier warning
- Excel export generation
- PDF report generation
- Scheduled expiry alerts

### Acceptance Test Demo

The first usable demo should show:

1. A vendor with a B-BBEE certificate.
2. Imported spend from posted vendor bills.
3. Calculated recognised spend.
4. Missing evidence warnings.
5. Expiring certificate warning.
6. Simple score dashboard.
7. Evidence pack export.

---

## Project Status

Current status:

```text
Planning / Specification / Early Build Preparation
```

The preferred first build order is:

1. Supplier B-BBEE Profile
2. Certificate upload and expiry logic
3. Measurement period setup
4. Vendor bill spend import
5. Recognised spend calculation
6. Dashboard and shortfall reporting
7. Missing evidence report
8. RFQ / PO supplier warnings
9. Evidence pack export

---

## Roadmap

### Version 1: MVP

Focus:

- Supplier profile
- Certificates
- Expiry tracking
- Spend import
- Recognised spend calculation
- Dashboard
- Missing evidence report
- Buyer warning
- Evidence pack export

### Version 2: Extended B-BBEE Procurement Control

Possible additions:

- More advanced rule sets
- Sector code configuration
- ESD contribution tracking
- Supplier override approval workflow
- Supplier portal upload
- More detailed audit trails
- Better exception management

### Version 3: Optimisation and Intelligence

Possible additions:

- Supplier alternatives
- Procurement scenario modelling
- AI-supported recommendations
- Risk scoring
- External certificate data integrations, if trusted sources are available
- Forecasting before measurement period end

---

## Commercial Positioning

Recommended positioning:

> B-BBEE Procurement Control for Odoo helps South African companies track supplier B-BBEE evidence, calculate recognised procurement spend, identify procurement scorecard risk, and prepare verification-ready evidence packs.

Recommended sales promise:

> Know your procurement score before year-end and fix supplier gaps early.

Recommended boundary:

> This module supports B-BBEE procurement control and evidence preparation. It does not certify B-BBEE status.

---

## Contributing

Contributions should follow the project’s domain boundaries.

Before adding a feature, consider:

- Which bounded context owns this behaviour?
- Does this mutate Odoo accounting data? If yes, reconsider.
- Is this feature part of MVP or a later phase?
- Is the calculation auditable?
- Can a future verifier trace the result back to source documents?
- Does the change preserve frozen assessments and evidence packs?
- Does the feature accidentally imply legal certification?

### Suggested Branch Naming

```text
feature/supplier-profile
feature/certificate-expiry
feature/spend-import
feature/evidence-pack
fix/recognised-spend-calculation
docs/readme-update
```

### Suggested Commit Style

```text
feat: add supplier compliance profile
feat: import posted vendor bills into spend batch
fix: prevent expired certificates from counting as valid evidence
docs: update README with MVP scope
test: add recognised spend calculation tests
```

---

## License

License to be decided.

Suggested options:

- Proprietary commercial license
- Odoo-compatible open-source license
- Dual license model

Update this section before public release.

---

## Final Product Boundary

This repository should remain focused on:

```text
Supplier certificates
Procurement spend
Recognition percentages
Score visibility
Missing evidence
Buyer warnings
Evidence packs
```

It should not expand into a full B-BBEE certification platform unless that becomes an explicit future product with proper legal, regulatory, and verification-agency alignment.
