{
    "name": "B-good",
    "summary": "B-BBEE procurement compliance, supplier evidence, and recognised spend control for Odoo.",
    "version": "18.0.1.0.0",
    "category": "Accounting/Accounting",
    "author": "B-good",
    "maintainer": "B-good",
    "web_icon": "bbbbee_procurement,static/description/icon.svg",
    "license": "LGPL-3",
    "description": """
B-good is a B-BBEE procurement compliance module for Odoo that turns supplier evidence, recognised spend,
and scorecard tracking into one operational workflow.

What it helps teams do:
- Maintain supplier B-BBEE profiles, certificates, affidavits, and ownership data.
- Import spend from posted vendor bills and credit notes into measurement periods.
- Track recognised procurement spend, scorecard progress, and compliance risk in real time.
- Generate evidence packs and printable reports for audit and verification review.
- Give managers and compliance officers a visual dashboard with drill-down actions and forecasts.

Ideal for:
- Procurement teams
- Compliance officers and B-BBEE consultants
- Finance leaders who need visibility into recognised spend and evidence risk
""",
    "depends": [
        "account",
        "base",
        "mail",
        "purchase",
    ],
    "data": [
        "security/security_groups.xml",
        "security/ir.model.access.csv",
        "security/record_rules.xml",
        "data/default_rule_sets.xml",
        "data/scheduled_actions.xml",
        "data/mail_templates.xml",
        "views/module_card_views.xml",
        "views/documentation_views.xml",
        "views/wizard_views.xml",
        "views/supplier_profile_views.xml",
        "views/supplier_certificate_views.xml",
        "views/document_tag_views.xml",
        "views/compliance_alert_policy_views.xml",
        "views/certificate_bulk_upload_views.xml",
        "views/spend_batch_views.xml",
        "views/spend_line_views.xml",
        "views/scorecard_assessment_views.xml",
        "views/evidence_pack_views.xml",
        "views/dashboard_views.xml",
        "views/dashboard_chart_views.xml",
        "views/purchase_order_views.xml",
        "views/account_move_views.xml",
        "views/menu_views.xml",
        "reports/evidence_pack_report.xml",
        "reports/missing_evidence_report.xml",
        "reports/spend_schedule_report.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "bbbbee_procurement/static/src/scss/bbbbee_backend.scss",
            "bbbbee_procurement/static/src/js/dashboard_jump_links.js",
        ],
    },
    "application": True,
    "installable": True,
    "demo": [
        "demo/demo_data.xml",
    ],
}
