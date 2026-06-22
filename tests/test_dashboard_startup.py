from odoo.tests.common import TransactionCase


class TestDashboardStartup(TransactionCase):
    def test_empty_dashboard_shows_startup_guidance(self):
        dashboard = self.env["bbbbee.dashboard.wizard"].create({})

        self.assertFalse(dashboard.has_data)
        self.assertTrue(dashboard.starter_html)
        self.assertFalse(dashboard.next_actions_html)

    def test_load_starter_demo_creates_sample_data(self):
        dashboard = self.env["bbbbee.dashboard.wizard"].create({})
        action = dashboard.action_load_starter_demo()

        self.assertEqual(action["res_model"], "bbbbee.dashboard.wizard")
        self.assertTrue(self.env["bbbbee.measurement.period"].search([("name", "like", "Starter FY")], limit=1))
        self.assertTrue(self.env["bbbbee.supplier.profile"].search([("partner_id.name", "=", "B-good Starter Supplier")], limit=1))
