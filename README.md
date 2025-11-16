# Ousman Bah

# PID 6378860

Supermarket Association Rule Mining

An interactive web application for mining association rules from supermarket transaction data using Apriori and Eclat algorithms.

## Features

- **Manual Transaction Creation**: Create shopping transactions by selecting products
- **Data Preprocessing**: Clean and validate transaction data
- **Association Rule Mining**: Implements both Apriori and Eclat algorithms
- **Product Recommendations**: Get product recommendations based on discovered patterns
- **Performance Comparison**: Compare execution time and results between algorithms

## Project Structure

```
DATA MINING ASSIGNMENT/
├── app.py                      # Flask web application
├── requirements.txt            # Python dependencies
├── data/
│   ├── products.csv           # Product catalog
│   └── sample_transactions.csv # Sample transaction data
├── src/
│   ├── algorithms/
│   │   ├── apriori.py        # Apriori algorithm implementation
│   │   └── eclat.py          # Eclat algorithm implementation
│   └── preprocessing/
│       └── cleaner.py        # Data cleaning and validation
└── templates/
    └── index.html            # Web interface
```

## Installation

1. Install Python dependencies:

```bash
pip install -r requirements.txt
```

## Usage

1. Start the Flask server:

```bash
python app.py
```

2. Open your browser and navigate to:

```
http://localhost:5001
```

3. Follow the steps in the web interface:
   - **Step 1**: Create transactions by selecting products and adding them to cart
   - **Step 2**: Run preprocessing to clean and validate the data
   - **Step 3**: Run association rule mining with custom support and confidence thresholds
   - **Step 4**: Get product recommendations based on discovered patterns

## Algorithms

### Apriori Algorithm

- Discovers frequent itemsets using a bottom-up approach
- Generates association rules with support, confidence, and lift metrics

### Eclat Algorithm

- Uses vertical data format and depth-first search
- More efficient for certain datasets compared to Apriori

## Configuration

Default mining parameters:

- Minimum Support: 0.2 (20%)
- Minimum Confidence: 0.5 (50%)

These can be adjusted in the web interface before running the mining algorithms.
