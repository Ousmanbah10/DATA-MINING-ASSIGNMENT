import time
from itertools import combinations
from typing import List, Dict, Set, Tuple
from collections import defaultdict


class AprioriMiner:

    def __init__(self, min_support: float = 0.2, min_confidence: float = 0.5):
        self.min_support = min_support
        self.min_confidence = min_confidence
        self.transactions = []
        self.frequent_itemsets = {}
        self.rules = []
        self.execution_time = 0

    def fit(self, transactions: List[List[str]]) -> Dict:
        start_time = time.time()
        self.transactions = transactions
        n_transactions = len(transactions)

        self.frequent_itemsets = self._find_frequent_itemsets(n_transactions)
        self.rules = self._generate_rules()

        self.execution_time = (time.time() - start_time) * 1000

        return {
            'execution_time': self.execution_time,
            'num_rules': len(self.rules),
            'num_frequent_itemsets': sum(len(itemsets) for itemsets in self.frequent_itemsets.values())
        }

    def _find_frequent_itemsets(self, n_transactions: int) -> Dict:
        frequent_itemsets = {}
        min_support_count = self.min_support * n_transactions

        item_counts = defaultdict(int)
        for transaction in self.transactions:
            for item in transaction:
                item_counts[frozenset([item])] += 1

        frequent_itemsets[1] = {
            itemset: count / n_transactions
            for itemset, count in item_counts.items()
            if count >= min_support_count
        }

        k = 2
        while frequent_itemsets.get(k - 1):
            candidates = self._generate_candidates(frequent_itemsets[k - 1], k)

            candidate_counts = defaultdict(int)
            for transaction in self.transactions:
                transaction_set = set(transaction)
                for candidate in candidates:
                    if candidate.issubset(transaction_set):
                        candidate_counts[frozenset(candidate)] += 1

            frequent_k = {
                itemset: count / n_transactions
                for itemset, count in candidate_counts.items()
                if count >= min_support_count
            }

            if frequent_k:
                frequent_itemsets[k] = frequent_k
                k += 1
            else:
                break

        return frequent_itemsets

    def _generate_candidates(self, prev_frequent: Dict, k: int) -> Set[frozenset]:
        items = set()
        for itemset in prev_frequent.keys():
            items.update(itemset)

        candidates = set()
        for candidate in combinations(sorted(items), k):
            candidate_set = frozenset(candidate)

            is_valid = True
            for subset in combinations(candidate, k - 1):
                if frozenset(subset) not in prev_frequent:
                    is_valid = False
                    break

            if is_valid:
                candidates.add(candidate_set)

        return candidates

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

        count = sum(1 for transaction in self.transactions if itemset.issubset(set(transaction)))
        return count / len(self.transactions) if self.transactions else 0

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
