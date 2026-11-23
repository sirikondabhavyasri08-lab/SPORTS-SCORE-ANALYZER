import unittest, tempfile, csv
from validation import validate_match
from analytics import match_result, summary, search_matches
from storage import import_csv

def sample(mid="T1", a=100, b=90):
    return {"match_id":mid,"date":"2026-11-20","tournament":"Test Cup","sport":"Cricket",
            "team_a":"Alpha","team_b":"Beta","score_a":a,"score_b":b,"venue":"Ground","status":"Completed"}

class ProjectTests(unittest.TestCase):
    def test_valid_match(self):
        item, errors = validate_match(sample())
        self.assertFalse(errors); self.assertEqual(item["score_a"],100)
    def test_negative_score_rejected(self):
        item, errors = validate_match(sample(a=-1))
        self.assertIsNone(item); self.assertTrue(errors)
    def test_duplicate_id_rejected(self):
        item, errors = validate_match(sample(), {"T1"})
        self.assertTrue(errors)
    def test_winner_and_draw(self):
        self.assertEqual(match_result(sample()),"Alpha")
        self.assertEqual(match_result(sample(a=90,b=90)),"Draw")
    def test_summary(self):
        s = summary([sample()])
        self.assertEqual(s["completed"],1); self.assertEqual(s["wins"]["Alpha"],1)
    def test_search(self):
        self.assertEqual(len(search_matches([sample()], "alpha")),1)
    def test_csv_import(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", newline="", encoding="utf-8", delete=False) as f:
            writer=csv.DictWriter(f, fieldnames=sample().keys()); writer.writeheader(); writer.writerow(sample("T2"))
            path=f.name
        rows, errors = import_csv(path, [])
        self.assertEqual(len(rows),1); self.assertFalse(errors)

if __name__ == "__main__": unittest.main()
