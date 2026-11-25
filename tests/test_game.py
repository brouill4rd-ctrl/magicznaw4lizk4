import unittest

from game import matches_guess, normalize_name, roll_threshold, weighted_creature


class GameRulesTests(unittest.TestCase):
    def test_polish_diacritics_and_case(self):
        self.assertEqual(normalize_name("  ŻÓŁĆ  "), "zolc")
        self.assertTrue(matches_guess(" NIUCHACZ ", ["Niuchacz"]))

    def test_aliases_and_short_answers(self):
        self.assertTrue(matches_guess("niffler", ["Niuchacz", "Niffler"]))
        self.assertFalse(matches_guess("kot", ["Kot"]))

    def test_threshold_bounds_and_validation(self):
        self.assertIn(roll_threshold(20, 50), range(20, 51))
        with self.assertRaises(ValueError):
            roll_threshold(5, 2)

    def test_weighted_selection_respects_rarity_weights(self):
        creatures = [{"id":1,"rarity":"common","enabled":1},{"id":2,"rarity":"mythical","enabled":1}]
        selected = weighted_creature(creatures, {"common":0,"mythical":1})
        self.assertEqual(selected["id"], 2)


if __name__ == "__main__":
    unittest.main()
