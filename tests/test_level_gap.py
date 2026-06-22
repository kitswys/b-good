from odoo.tests.common import TransactionCase


class TestLevelGap(TransactionCase):
    def test_level_gap_rounds_up(self):
        dashboard = self.env["bbbbee.dashboard.wizard"].create({})

        self.assertEqual(dashboard._bee_level_for_score(49.6), "Level 6")
        threshold, points, label = dashboard._next_level_gap(49.6)
        self.assertEqual(threshold, 50.0)
        self.assertEqual(points, 1)
        self.assertEqual(label, "point")

    def test_level_transition_uses_next_better_level(self):
        dashboard = self.env["bbbbee.dashboard.wizard"].create({})

        current_level, next_level, points, label = dashboard._next_level_transition(49.6)
        self.assertEqual(current_level, "Level 6")
        self.assertEqual(next_level, "Level 5")
        self.assertEqual(points, 1)
        self.assertEqual(label, "point")

    def test_level_transition_handles_exact_threshold(self):
        dashboard = self.env["bbbbee.dashboard.wizard"].create({})

        current_level, next_level, points, label = dashboard._next_level_transition(50.0)
        self.assertEqual(current_level, "Level 5")
        self.assertEqual(next_level, "Level 4")
        self.assertEqual(points, 10)
        self.assertEqual(label, "points")
