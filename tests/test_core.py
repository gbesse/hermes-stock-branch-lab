import unittest,copy,json
from hermes_stock_branch_lab import run
DEMO={'stock': [{'sku': 'part', 'on_hand': 10, 'reserved': 8}], 'candidates': [{'id': 'promise-five', 'reserve': [{'sku': 'part', 'quantity': 5}]}, {'id': 'promise-two', 'reserve': [{'sku': 'part', 'quantity': 2}]}]}
class DomainTests(unittest.TestCase):
 def test_existing_reservations_protected(self):
  x=run(DEMO);self.assertEqual(x['eligible_candidate_ids'],['promise-two']);self.assertEqual(x['candidates'][0]['findings'][0]['available'],2)
 def test_stale_snapshot_blocks_even_feasible_plan(self):
  x=copy.deepcopy(DEMO);x['current_stock']=[{'sku':'part','on_hand':10,'reserved':9}];y=run(x);self.assertFalse(y['snapshot_matches']);self.assertEqual(y['eligible_candidate_ids'],[])
 def test_branches_rollback(self):
  x=copy.deepcopy(DEMO);x['candidates']=[{'id':'a','reserve':[{'sku':'part','quantity':2}]},{'id':'b','reserve':[{'sku':'part','quantity':2}]}];self.assertEqual(run(x)['eligible_candidate_ids'],['a','b'])
