import time
from typing import List, Dict, Set, Tuple
from collections import defaultdict
from itertools import combinations


class EclatMiner:

    def __init__(self, min_support: float = 0.2, min_confidence: float = 0.5):
        self.min_support = min_support
        self.min_confidence = min_confidence
        self.transactions = []
        self.tid_sets = {}
        self.frequent_itemsets = {}
        self.rules = []
        self.execution_time = 0

    def fit(self, transactions: List[List[str]]) -> Dict:
        start_time = time.time()
        self.transactions = transactions
        n_transactions = len(transactions)
        min_support_count = self.min_support * n_transactions

        self._build_tid_sets()
        self.frequent_itemsets = self._find_frequent_itemsets(min_support_count, n_transactions)
        self.rules = self._generate_rules()

        self.execution_time = (time.time() - start_time) * 1000

        return {
            'execution_time': self.execution_time,
            'num_rules': len(self.rules),
            'num_frequent_itemsets': sum(len(itemsets) for itemsets in self.frequent_itemsets.values())
        }

    def _build_tid_sets(self):
        self.tid_sets = defaultdict(set)

        for tid, transaction in enumerate(self.transactions):
            for item in transaction:
                self.tid_sets[item].add(tid)

    def _find_frequent_itemsets(self, min_support_count: int, n_transactions: int) -> Dict:
        frequent_itemsets = {}

        frequent_1 = {}
        items_list = []

        for item, tid_set in self.tid_sets.items():
            support_count = len(tid_set)
            if support_count >= min_support_count:
                itemset = frozenset([item])
                frequent_1[itemset] = support_count / n_transactions
                items_list.append((item, tid_set))

        frequent_itemsets[1] = frequent_1

        self._eclat_recursive(items_list, min_support_count, n_transactions, frequent_itemsets, 2)

        return frequent_itemsets

    def _eclat_recursive(self, prefix_items: List[Tuple[str, Set[int]]],
                        min_support_count: int,
                        n_transactions: int,
                        frequent_itemsets: Dict,
                        k: int):
        if len(prefix_items) < 2:
            return

        for i in range(len(prefix_items)):
            item_i, tid_i = prefix_items[i]

            new_prefix_items = []

            for j in range(i + 1, len(prefix_items)):
                item_j, tid_j = prefix_items[j]

                tid_intersection = tid_i & tid_j
                support_count = len(tid_intersection)

                if support_count >= min_support_count:
                    if isinstance(item_i, frozenset):
                        new_itemset = item_i | frozenset([item_j])
                    elif isinstance(item_i, str):
                        if isinstance(item_j, frozenset):
                            new_itemset = frozenset([item_i]) | item_j
                        else:
                            new_itemset = frozenset([item_i, item_j])
                    else:
                        new_itemset = item_i | item_j

                    if k not in frequent_itemsets:
                        frequent_itemsets[k] = {}

                    frequent_itemsets[k][new_itemset] = support_count / n_transactions

                    new_prefix_items.append((new_itemset, tid_intersection))

            if new_prefix_items:
                self._eclat_recursive(new_prefix_items, min_support_count, n_transactions,
                                     frequent_itemsets, k + 1)

    def _generate_rules(self) -> List[Dict]:
        rules = []

        for k in range(2, len(self.frequent_itemsets) + 1):
            if k not in self.frequent_itemsets:
                continue

            for itemset, support in self.frequent_itemsets[k].items():
                items = list(itemset)

                for i in range(1, len(items)):
                    for antecedent in combinations(items, i):
                        antecedent = frozenset(antecedent)
                        consequent = itemset - antecedent

                        if not consequent:
                            continue

                        antecedent_support = self._get_support(antecedent)
                        if antecedent_support == 0:
                            continue

                        confidence = support / antecedent_support

                        if confidence >= self.min_confidence:
                            consequent_support = self._get_support(consequent)
                            lift = confidence / consequent_support if consequent_support > 0 else 0

                            rules.append({
                                'antecedent': set(antecedent),
                                'consequent': set(consequent),
                                'support': support,
                                'confidence': confidence,
                                'lift': lift
                            })

        return rules

    def _get_support(self, itemset: frozenset) -> float:
        k = len(itemset)
        if k in self.frequent_itemsets and itemset in self.frequent_itemsets[k]:
            return self.frequent_itemsets[k][itemset]

        if k == 1:
            item = list(itemset)[0]
            if item in self.tid_sets:
                return len(self.tid_sets[item]) / len(self.transactions)

        tid_intersection = None
        for item in itemset:
            if item not in self.tid_sets:
                return 0.0
            if tid_intersection is None:
                tid_intersection = self.tid_sets[item].copy()
            else:
                tid_intersection &= self.tid_sets[item]

        return len(tid_intersection) / len(self.transactions) if self.transactions else 0

    def get_rules(self) -> List[Dict]:
        return self.rules

    def get_recommendations(self, item: str) -> List[Dict]:
        recommendations = []

        for rule in self.rules:
            if item in rule['antecedent']:
                for rec_item in rule['consequent']:
                    recommendations.append({
                        'item': rec_item,
                        'confidence': rule['confidence'],
                        'support': rule['support'],
                        'lift': rule['lift']
                    })

        recommendations.sort(key=lambda x: x['confidence'], reverse=True)

        seen = set()
        unique_recommendations = []
        for rec in recommendations:
            if rec['item'] not in seen:
                seen.add(rec['item'])
                unique_recommendations.append(rec)

        return unique_recommendations
