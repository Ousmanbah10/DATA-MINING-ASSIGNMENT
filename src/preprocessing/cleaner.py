import csv
from typing import List, Dict, Set, Tuple


class DataCleaner:

    def __init__(self, products_file: str = 'data/products.csv'):
        self.valid_products = self._load_valid_products(products_file)
        self.report = {
            'total_transactions': 0,
            'empty_transactions': 0,
            'single_item_transactions': 0,
            'duplicate_items': 0,
            'invalid_items': 0,
            'case_standardized': 0,
            'whitespace_cleaned': 0,
            'valid_transactions': 0,
            'total_items': 0,
            'unique_products': 0
        }

    def _load_valid_products(self, filepath: str) -> Set[str]:
        products = set()
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    products.add(row['product_name'].strip().lower())
        except FileNotFoundError:
            print(f"Warning: Product file {filepath} not found. Using empty product list.")
        return products

    def load_transactions(self, filepath: str) -> List[List[str]]:
        transactions = []
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    items_str = row.get('items', '').strip()
                    if items_str:
                        items = [item.strip() for item in items_str.split(',')]
                        transactions.append(items)
                    else:
                        transactions.append([])
        except FileNotFoundError:
            print(f"Error: Transaction file {filepath} not found.")
        return transactions

    def preprocess(self, transactions: List[List[str]]) -> Tuple[List[List[str]], Dict]:
        self.report['total_transactions'] = len(transactions)
        cleaned_transactions = []

        for transaction in transactions:
            if not transaction or len(transaction) == 0:
                self.report['empty_transactions'] += 1
                continue

            cleaned_items = []
            seen_items = set()

            for item in transaction:
                item = item.strip()
                if item != transaction[transaction.index(item)].strip():
                    self.report['whitespace_cleaned'] += 1

                original_item = item
                item = item.lower()
                if original_item != item:
                    self.report['case_standardized'] += 1

                if self.valid_products and item not in self.valid_products:
                    self.report['invalid_items'] += 1
                    continue

                if item in seen_items:
                    self.report['duplicate_items'] += 1
                    continue

                seen_items.add(item)
                cleaned_items.append(item)

            if len(cleaned_items) == 1:
                self.report['single_item_transactions'] += 1
                continue

            if len(cleaned_items) >= 2:
                cleaned_transactions.append(cleaned_items)

        self.report['valid_transactions'] = len(cleaned_transactions)
        self.report['total_items'] = sum(len(t) for t in cleaned_transactions)

        unique = set()
        for transaction in cleaned_transactions:
            unique.update(transaction)
        self.report['unique_products'] = len(unique)

        return cleaned_transactions, self.report

    def get_report_string(self) -> str:
        report_lines = [
            "Preprocessing Report:",
            "-------------------",
            "Before Cleaning:",
            f"- Total transactions: {self.report['total_transactions']}",
            f"- Empty transactions: {self.report['empty_transactions']}",
            f"- Single-item transactions: {self.report['single_item_transactions']}",
            f"- Duplicate items found: {self.report['duplicate_items']} instances",
            f"- Invalid items found: {self.report['invalid_items']} instances",
            "",
            "After Cleaning:",
            f"- Valid transactions: {self.report['valid_transactions']}",
            f"- Total items: {self.report['total_items']}",
            f"- Unique products: {self.report['unique_products']}"
        ]
        return "\n".join(report_lines)


def clean_data(transactions_file: str, products_file: str = 'data/products.csv'):
    cleaner = DataCleaner(products_file)
    transactions = cleaner.load_transactions(transactions_file)
    cleaned_transactions, report = cleaner.preprocess(transactions)
    return cleaned_transactions, report, cleaner.get_report_string()
