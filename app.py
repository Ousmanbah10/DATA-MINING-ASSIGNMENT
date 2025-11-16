from flask import Flask, render_template, request, jsonify
import json
import csv
import os
from src.preprocessing.cleaner import DataCleaner
from src.algorithms.apriori import AprioriMiner
from src.algorithms.eclat import EclatMiner

app = Flask(__name__)

transactions_data = []
cleaned_transactions = []
preprocessing_report = {}
apriori_miner = None
eclat_miner = None
products_list = []


def load_products():
    global products_list
    products_list = []
    try:
        with open('data/products.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                products_list.append({
                    'id': row['product_id'],
                    'name': row['product_name'],
                    'category': row['category']
                })
    except FileNotFoundError:
        print("Products file not found")
    return products_list


@app.route('/')
def index():
    load_products()
    return render_template('index.html', products=products_list)


@app.route('/api/products', methods=['GET'])
def get_products():
    return jsonify(products_list)


@app.route('/api/transactions/create', methods=['POST'])
def create_transaction():
    global transactions_data
    data = request.json
    items = data.get('items', [])

    if items:
        transactions_data.append(items)
        return jsonify({
            'success': True,
            'message': f'Transaction created with {len(items)} items',
            'transaction_id': len(transactions_data),
            'total_transactions': len(transactions_data)
        })
    return jsonify({'success': False, 'message': 'No items provided'}), 400


@app.route('/api/transactions/import', methods=['POST'])
def import_transactions():
    global transactions_data

    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'No file provided'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No file selected'}), 400

    try:
        content = file.read().decode('utf-8').splitlines()
        reader = csv.DictReader(content)

        transactions_data = []
        for row in reader:
            items_str = row.get('items', '').strip()
            if items_str:
                items = [item.strip() for item in items_str.split(',')]
                transactions_data.append(items)
            else:
                transactions_data.append([])

        return jsonify({
            'success': True,
            'message': f'Successfully imported {len(transactions_data)} transactions',
            'total_transactions': len(transactions_data)
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error importing file: {str(e)}'}), 500


@app.route('/api/transactions/load-sample', methods=['POST'])
def load_sample():
    global transactions_data

    try:
        cleaner = DataCleaner('data/products.csv')
        transactions_data = cleaner.load_transactions('data/sample_transactions.csv')

        return jsonify({
            'success': True,
            'message': f'Successfully loaded {len(transactions_data)} sample transactions',
            'total_transactions': len(transactions_data)
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error loading sample: {str(e)}'}), 500


@app.route('/api/transactions', methods=['GET'])
def get_transactions():
    return jsonify({
        'raw_transactions': transactions_data,
        'cleaned_transactions': cleaned_transactions,
        'total_raw': len(transactions_data),
        'total_cleaned': len(cleaned_transactions)
    })


@app.route('/api/preprocess', methods=['POST'])
def preprocess_data():
    global cleaned_transactions, preprocessing_report

    if not transactions_data:
        return jsonify({'success': False, 'message': 'No transactions to preprocess'}), 400

    try:
        cleaner = DataCleaner('data/products.csv')
        cleaned_transactions, preprocessing_report = cleaner.preprocess(transactions_data)
        report_string = cleaner.get_report_string()

        return jsonify({
            'success': True,
            'message': 'Preprocessing completed',
            'report': preprocessing_report,
            'report_string': report_string,
            'cleaned_count': len(cleaned_transactions)
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error during preprocessing: {str(e)}'}), 500


@app.route('/api/mine', methods=['POST'])
def run_mining():
    global apriori_miner, eclat_miner

    if not cleaned_transactions:
        return jsonify({'success': False, 'message': 'No cleaned transactions. Please preprocess first.'}), 400

    data = request.json
    min_support = float(data.get('min_support', 0.2))
    min_confidence = float(data.get('min_confidence', 0.5))

    try:
        apriori_miner = AprioriMiner(min_support, min_confidence)
        apriori_metrics = apriori_miner.fit(cleaned_transactions)

        eclat_miner = EclatMiner(min_support, min_confidence)
        eclat_metrics = eclat_miner.fit(cleaned_transactions)

        return jsonify({
            'success': True,
            'message': 'Mining completed',
            'apriori': apriori_metrics,
            'eclat': eclat_metrics,
            'parameters': {
                'min_support': min_support,
                'min_confidence': min_confidence
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error during mining: {str(e)}'}), 500


@app.route('/api/recommendations/<item>', methods=['GET'])
def get_recommendations(item):
    if not apriori_miner or not eclat_miner:
        return jsonify({'success': False, 'message': 'Please run mining first'}), 400

    try:
        item = item.lower()

        apriori_recs = apriori_miner.get_recommendations(item)
        eclat_recs = eclat_miner.get_recommendations(item)

        combined_recs = {}
        for rec in apriori_recs + eclat_recs:
            rec_item = rec['item']
            if rec_item not in combined_recs:
                combined_recs[rec_item] = {
                    'item': rec_item,
                    'confidence': [],
                    'support': [],
                    'lift': []
                }
            combined_recs[rec_item]['confidence'].append(rec['confidence'])
            combined_recs[rec_item]['support'].append(rec['support'])
            combined_recs[rec_item]['lift'].append(rec['lift'])

        final_recs = []
        for rec_item, data in combined_recs.items():
            final_recs.append({
                'item': rec_item,
                'confidence': sum(data['confidence']) / len(data['confidence']),
                'support': sum(data['support']) / len(data['support']),
                'lift': sum(data['lift']) / len(data['lift'])
            })

        final_recs.sort(key=lambda x: x['confidence'], reverse=True)

        return jsonify({
            'success': True,
            'item': item,
            'recommendations': final_recs[:10]
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error getting recommendations: {str(e)}'}), 500


@app.route('/api/rules', methods=['GET'])
def get_rules():
    if not apriori_miner or not eclat_miner:
        return jsonify({'success': False, 'message': 'Please run mining first'}), 400

    try:
        apriori_rules = apriori_miner.get_rules()
        eclat_rules = eclat_miner.get_rules()

        def serialize_rule(rule):
            return {
                'antecedent': list(rule['antecedent']),
                'consequent': list(rule['consequent']),
                'support': rule['support'],
                'confidence': rule['confidence'],
                'lift': rule['lift']
            }

        return jsonify({
            'success': True,
            'apriori_rules': [serialize_rule(r) for r in apriori_rules],
            'eclat_rules': [serialize_rule(r) for r in eclat_rules]
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error getting rules: {str(e)}'}), 500


@app.route('/api/stats', methods=['GET'])
def get_stats():
    unique_items = set()
    for transaction in cleaned_transactions:
        unique_items.update(transaction)

    return jsonify({
        'total_raw_transactions': len(transactions_data),
        'total_cleaned_transactions': len(cleaned_transactions),
        'unique_items': len(unique_items),
        'preprocessing_done': len(cleaned_transactions) > 0,
        'mining_done': apriori_miner is not None and eclat_miner is not None
    })


if __name__ == '__main__':
    os.makedirs('data', exist_ok=True)
    app.run(debug=True, port=5001)
