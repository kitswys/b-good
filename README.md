# B-good (`bbbbee_procurement`)

**B-good** is a B-BBEE preferential procurement control center for Odoo 18.
It turns supplier compliance, recognised spend, and scorecard movement into one
operational workflow so teams can see risk, protect spend, and prepare for
verification without spreadsheet chaos.

## What this repo is

This repository contains the B-good MVP addon for Odoo:
- dashboard and scorecard experience
- supplier profiles and evidence tracking
- spend batch and spend line analysis
- evidence packs and printable outputs
- documentation and demo data for a guided first run

## Who it is for

- Procurement teams managing supplier risk
- Finance leaders tracking recognised spend exposure
- Compliance and B-BBEE officers preparing for verification
- Odoo implementation partners delivering a controlled MVP

## Why it exists

Most procurement compliance workflows still depend on spreadsheets, manual
evidence chasing, and end-of-period surprises. B-good gives teams a live view
of supplier compliance status, spend at risk, and the current scorecard story.

## MVP scope

Included in this MVP:
- dashboard with drill-down actions
- supplier compliance profiles
- certificate and affidavit register
- measurement periods and rule sets
- spend batches and spend lines
- scorecard assessments
- evidence packs
- printable compliance reports
- documentation tab and demo dataset

Not fully included yet:
- advanced automation beyond the current workflows
- every jurisdiction-specific scorecard edge case
- deep role-based permissions beyond the current module model

## Screens you can show in a demo

- Dashboard
- Supplier Profiles
- Certificates and Affidavits
- Spend Batches
- Spend Lines
- Scorecard Assessments
- Evidence Packs
- Documentation

## Requirements

- Odoo 18
- `account`
- `base`
- `mail`
- `purchase`
- Python dependency: `xlsxwriter` for Excel exports

## Installation

1. Copy `bbbbee_procurement` into your Odoo addons path.
2. Update the Apps list.
3. Install **B-good**.
4. Load the demo data if you want the repo to open with sample records.

## Demo flow

1. Open **B-good**.
2. Review the dashboard and scorecard story.
3. Open supplier profiles and certificates.
4. Inspect spend batches and spend lines.
5. Recalculate the scorecard.
6. Generate an evidence pack.
7. Use the documentation tab for product guidance.

## Screenshots to include on GitHub

Use real captures from the demo database for:
- Dashboard hero and forecast cards
- Supplier Profiles
- Certificates and Affidavits
- Spend Batches and Spend Lines
- Evidence Packs

These are the screens that most quickly prove the product is real and usable.

## Repository notes

- `overview.md` is the commercial one-pager.
- `static/description/index.html` is the Odoo app-store style description.
- `demo/demo_data.xml` seeds a guided demo scenario.
- `CHANGELOG.md` tracks the MVP release status.

## License

This project is declared as LGPL-3 compatible in the manifest and is packaged
for public MVP distribution.
