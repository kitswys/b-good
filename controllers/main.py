from odoo import fields, http
from odoo.http import request


class BbbbeeCertificateBannerController(http.Controller):
    def _html_response(self, html):
        return request.make_response(html, headers=[("Content-Type", "text/html; charset=utf-8")])

    def _render_metric_card(self, title, value, note, tone="#2f5be3"):
        return """
            <div style="padding:12px 14px;border:1px solid #dbe2ee;border-radius:10px;background:#fff;min-width:0;">
                <div style="font-size:11px;font-weight:800;letter-spacing:0.03em;text-transform:uppercase;color:%s;margin-bottom:4px;">%s</div>
                <div style="font-size:26px;font-weight:900;color:#1f2d3d;line-height:1.1;">%s</div>
                <div style="font-size:12px;color:#64748b;line-height:1.4;margin-top:4px;">%s</div>
            </div>
        """ % (tone, title, value, note)

    @http.route("/bbbbee/supplier/certificate/banner", type="http", auth="user", website=False)
    def certificate_banner(self, **kwargs):
        Certificate = request.env["bbbbee.supplier.certificate"].sudo()
        today = fields.Date.context_today(request.env.user)

        active_count = Certificate.search_count([("active", "=", True), ("state", "!=", "superseded")])
        expired_count = Certificate.search_count([("active", "=", True), ("state", "=", "expired")])
        expiring_count = Certificate.search_count([("active", "=", True), ("state", "=", "expiring_soon")])

        upcoming = Certificate.search(
            [("active", "=", True), ("state", "in", ("valid", "expiring_soon")), ("expiry_date", "!=", False)],
            order="expiry_date asc, id asc",
            limit=2,
        )
        upcoming_rows = []
        for cert in upcoming:
            days = (cert.expiry_date - today).days if cert.expiry_date else 0
            upcoming_rows.append(
                """
                <div style="display:flex;justify-content:space-between;gap:10px;padding:8px 10px;border-radius:8px;background:#f8fafc;font-size:12px;color:#52627c;">
                    <span style="min-width:0;"><strong style="color:#1f2d3d;">{partner}</strong><br/>{expiry}</span>
                    <strong style="color:#1f2d3d;white-space:nowrap;">{days} days</strong>
                </div>
                """.format(
                    partner=cert.partner_id.display_name or "Unknown supplier",
                    expiry=cert.expiry_date.strftime("%d %b %Y"),
                    days=days,
                )
            )
        if not upcoming_rows:
            upcoming_rows.append(
                '<div style="padding:8px 10px;border-radius:8px;background:#f8fafc;font-size:12px;color:#64748b;">No upcoming expiries in the current set.</div>'
            )

        html = """
            <div class="row mb-4 p-3 bg-white shadow-sm rounded border-0" style="margin-left:0;margin-right:0;">
                <div class="col-md-3 col-12 mb-2 mb-md-0">%s</div>
                <div class="col-md-3 col-12 mb-2 mb-md-0">%s</div>
                <div class="col-md-3 col-12 mb-2 mb-md-0">%s</div>
                <div class="col-md-3 col-12">
                    <div style="padding:12px 14px;border:1px solid #dbe2ee;border-radius:10px;background:linear-gradient(180deg,#f8fafc 0%%,#eef4ff 100%%);">
                        <div style="font-size:11px;font-weight:800;letter-spacing:0.03em;text-transform:uppercase;color:#2f5be3;margin-bottom:8px;">Upcoming Expiries</div>
                        <div style="display:grid;gap:8px;">%s</div>
                    </div>
                </div>
            </div>
        """ % (
            self._render_metric_card("Total Active Documents", active_count, "Documents currently in scope.", "#2f5be3"),
            self._render_metric_card("Total Expired Files", expired_count, "Documents that require immediate replacement.", "#d94b4b"),
            self._render_metric_card("Review Note", expiring_count, "Expiry watchlist for the next sync window.", "#f0a21a"),
            "".join(upcoming_rows),
        )
        return self._html_response(html)

    @http.route("/bbbbee/banner/supplier-profiles", type="http", auth="user", website=False)
    def supplier_profiles_banner(self, **kwargs):
        Profile = request.env["bbbbee.supplier.profile"].sudo()
        profiles = Profile.search([])
        active_profiles = profiles.filtered(lambda p: p.active)
        avg_level = 0.0
        levels = [int(p.bbbbee_level) for p in profiles if str(p.bbbbee_level).isdigit()]
        if levels:
            avg_level = sum(levels) / len(levels)
        html = """
            <div class="row mb-4 p-3 bg-white shadow-sm rounded border-0" style="margin-left:0;margin-right:0;">
                <div class="col-md-4 col-12 mb-2 mb-md-0">%s</div>
                <div class="col-md-4 col-12 mb-2 mb-md-0">%s</div>
                <div class="col-md-4 col-12">
                    <div style="padding:12px 14px;border:1px solid #dbe2ee;border-radius:10px;background:linear-gradient(180deg,#f8fafc 0%%,#eef4ff 100%%);">
                        <div style="font-size:11px;font-weight:800;letter-spacing:0.03em;text-transform:uppercase;color:#2f5be3;margin-bottom:8px;">Insight</div>
                        <div style="font-size:13px;color:#52627c;line-height:1.5;">ℹ️ High recognition levels directly offset procurement points risk.</div>
                    </div>
                </div>
            </div>
        """ % (
            self._render_metric_card("Total Active Vendors", len(active_profiles), "Vendors currently active in the compliance register.", "#2f5be3"),
            self._render_metric_card("Average Supplier Level", "%0.1f" % avg_level if avg_level else "N/A", "Higher recognition reduces risk across procurement.", "#1f2d3d"),
        )
        return self._html_response(html)
