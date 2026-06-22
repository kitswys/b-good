# Bug Log

Use this file as the running backlog for bugs, regressions, and hardening tasks.

## Format
- Date:
- Area:
- Symptom:
- Root cause:
- Fix applied:
- Status:
- Notes:

## 2026-06-02

- Date: 2026-06-02
- Area: Access control / module loading
- Symptom: Module upgrade failed because access rules referenced models that were not registered yet.
- Root cause: New model files were not safely wired into the addon load path before ACL rows were added.
- Fix applied: Removed the new ACL rows temporarily so the registry could build; later fixes should reintroduce them only after model registration is verified.
- Status: Resolved for now
- Notes: Re-check ACL coverage before production release.

- Date: 2026-06-02
- Area: Odoo transient model table naming
- Symptom: Bulk upload wizard failed with "table name is too long".
- Root cause: Odoo auto-generated a table name from a long transient model name.
- Fix applied: Added explicit short `_table` names for the wizard and wizard line models.
- Status: Resolved
- Notes: Keep transient model names short or set `_table` explicitly.

- Date: 2026-06-02
- Area: View validation
- Symptom: Inline one2many view in supplier profile failed validation because child fields were treated as parent-model fields.
- Root cause: Embedded subviews used outdated structure and Odoo 18 validation was stricter.
- Fix applied: Switched embedded child tables from `tree` to `list` and added explicit `mode="list,form"` where needed.
- Status: Resolved
- Notes: Reuse `list` for inline child rows in this module.

- Date: 2026-06-02
- Area: Dashboard level gap text
- Symptom: Dashboard showed `0 points before Level X` when the score was close to the threshold.
- Root cause: Gap text was using rounded-down math instead of ceiling logic.
- Fix applied: Added threshold helpers and rounded the gap up with `ceil`.
- Status: Resolved
- Notes: Regression test added for the boundary case.

- Date: 2026-06-02
- Area: Multi-company hardening
- Symptom: Some dashboard/model queries still use broad searches and may cross company boundaries.
- Root cause: The module is not fully company-scoped in all computations and record rules.
- Fix applied: Not fully fixed yet.
- Status: Open
- Notes: Needs a careful pass through supplier profiles, certificates, spend batches, assessments, dashboard queries, and access rules.

- Date: 2026-06-02
- Area: Dashboard guidance / forecast window / level gap text
- Symptom: The dashboard repeated "what to do next" guidance in multiple places, the forecast window control lived away from the forecast block, and the level gap label was easy to misread.
- Root cause: Guidance was split across the startup block, hero summary, and forecast area; the expiry window field was placed in the top form group; the level gap text used "before" wording even when the score was being compared against the next threshold.
- Fix applied: Removed the duplicated in-data next-actions block from the main form, reduced the hero summary to status-focused content, moved the expiry window control beside the forecast section, and changed the gap label to "X points to Level Y".
- Status: Resolved
- Notes: If the gap still looks off in a live database, inspect the underlying assessment score versus the B-BBEE composite score because they are intentionally different metrics.

- Date: 2026-06-02
- Area: Dashboard expiring-documents duplication
- Symptom: The forecast already showed upcoming expiry items, and the separate "Expiring Documents" block below repeated the same list.
- Root cause: The dashboard rendered the same expiry data in two different places.
- Fix applied: Removed the duplicate lower expiring-documents block from the form view and kept the forecast panel as the single expiry source of truth.
- Status: Resolved
- Notes: The expiry window now behaves like a forecast control rather than a second summary section.

- Date: 2026-06-02
- Area: Forecast window placement
- Symptom: The expiry window dropdown was too low on the page to feel attached to the forecast panel.
- Root cause: The real Odoo field had to sit outside the computed HTML, so it was rendered below the scorecard instead of above it.
- Fix applied: Moved the dropdown to the top of the dashboard so it appears before the main dashboard blocks and is visually closer to the forecast area.
- Status: Resolved
- Notes: If you want it literally inside the forecast card, that would require custom JS or a larger structural refactor.

- Date: 2026-06-02
- Area: Dashboard refactor regression
- Symptom: Opening the dashboard raised a `NameError` for `business_impact_icon`.
- Root cause: The right-side panel was split into separate computed HTML sections, but the icon helper variables were referenced before being bound.
- Fix applied: Bound the icon helpers after the `_info_icon` function definition and revalidated the dashboard compute.
- Status: Resolved
- Notes: This came from the right-panel split needed to place the forecast dropdown above `Next Expiries`.
