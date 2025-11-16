# Supermarket Association Rule Mining - Project Report

## 1. Introduction

This project implements a web-based association rule mining system for supermarket transaction data. The application allows users to create shopping transactions, preprocess the data, and discover patterns using two popular algorithms: **Apriori** and **Eclat**.

### Objectives
- Implement Apriori and Eclat algorithms from scratch
- Build an interactive web interface for transaction management
- Compare algorithm performance and results
- Generate product recommendations based on discovered patterns

---

## 2. System Architecture

### 2.1 Technology Stack
- **Backend**: Flask (Python 3.x)
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Data Processing**: Python (no external mining libraries)

### 2.2 Components

#### Backend (app.py)
- Flask web server running on port 5001
- RESTful API endpoints for data operations
- Transaction management and storage
- Integration with mining algorithms

#### Frontend (templates/index.html)
- Interactive product selection interface
- Real-time statistics display
- Mining parameter controls
- Visualization of results and recommendations

#### Data Processing (src/preprocessing/cleaner.py)
- Validates transactions against product catalog
- Removes duplicates and empty transactions
- Standardizes item names (lowercase, trimmed)
- Filters single-item transactions
- Generates preprocessing reports

#### Mining Algorithms
- **Apriori** (src/algorithms/apriori.py)
- **Eclat** (src/algorithms/eclat.py)

---

## 3. Algorithm Implementations

### 3.1 Apriori Algorithm

**Approach**: Bottom-up, breadth-first search

**Key Steps**:
1. Find frequent 1-itemsets by scanning the database
2. Generate candidate k-itemsets from frequent (k-1)-itemsets
3. Prune candidates that don't meet minimum support
4. Repeat until no new frequent itemsets are found
5. Generate association rules from frequent itemsets

**Time Complexity**: O(2^n) worst case, where n is the number of unique items

**Implementation Highlights**:
- Uses `frozenset` for efficient itemset representation
- Candidate generation with pruning based on subset frequency
- Support counting via database scans
- Rule generation with confidence and lift calculations

### 3.2 Eclat Algorithm

**Approach**: Depth-first search with vertical data format

**Key Steps**:
1. Convert horizontal transaction format to vertical TID-sets (Transaction ID sets)
2. Find frequent 1-itemsets
3. Recursively generate k-itemsets by intersecting TID-sets
4. Calculate support based on TID-set sizes
5. Generate association rules from frequent itemsets

**Time Complexity**: O(n × m × 2^k) where n = transactions, m = items, k = max itemset size

**Implementation Highlights**:
- Vertical database format for efficient support counting
- Set intersection for fast frequency calculation
- Recursive depth-first search strategy
- Memory-efficient TID-set storage

### 3.3 Performance Comparison

| Aspect | Apriori | Eclat |
|--------|---------|-------|
| Data Format | Horizontal | Vertical (TID-sets) |
| Search Strategy | Breadth-first | Depth-first |
| Support Counting | Database scans | TID-set intersection |
| Memory Usage | Lower | Higher (stores TID-sets) |
| Best For | Large databases | Dense datasets |

---

## 4. Data Preprocessing

The preprocessing module ensures data quality through:

### 4.1 Cleaning Operations
- **Whitespace removal**: Trims leading/trailing spaces
- **Case normalization**: Converts all items to lowercase
- **Duplicate removal**: Eliminates duplicate items within transactions
- **Validation**: Checks items against product catalog
- **Filtering**: Removes empty and single-item transactions

### 4.2 Preprocessing Report
The system generates a detailed report showing:
- Total transactions before cleaning
- Number of empty transactions removed
- Number of single-item transactions removed
- Duplicate items found and removed
- Invalid items detected
- Final count of valid transactions
- Total items and unique products

---

## 5. Association Rules

### 5.1 Rule Metrics

**Support**: Frequency of itemset in database
```
Support(X) = Count(X) / Total_Transactions
```

**Confidence**: Conditional probability
```
Confidence(X → Y) = Support(X ∪ Y) / Support(X)
```

**Lift**: Correlation measure
```
Lift(X → Y) = Confidence(X → Y) / Support(Y)
```

### 5.2 Rule Interpretation

- **Lift > 1**: Positive correlation (items occur together more often than expected)
- **Lift = 1**: Independence (no correlation)
- **Lift < 1**: Negative correlation (items occur together less often than expected)

---

## 6. Web Interface Features

### 6.1 Step 1: Create Transactions
- Visual product grid with 30 products across multiple categories
- Interactive cart system
- Real-time transaction creation
- Transaction counter

### 6.2 Step 2: Preprocess Data
- One-click preprocessing
- Detailed cleaning report
- Statistics update

### 6.3 Step 3: Run Mining
- Adjustable minimum support (0.0 - 1.0)
- Adjustable minimum confidence (0.0 - 1.0)
- Performance comparison table
- Execution time measurement
- Rule and itemset counts

### 6.4 Step 4: Get Recommendations
- Product selection dropdown
- Top 10 recommendations
- Confidence visualization with progress bars
- Strength indicators (Strong/Moderate/Weak)
- Support and lift metrics

---

## 7. API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | Serve main page |
| `/api/products` | GET | Get product catalog |
| `/api/transactions/create` | POST | Create new transaction |
| `/api/transactions` | GET | Get all transactions |
| `/api/preprocess` | POST | Run data preprocessing |
| `/api/mine` | POST | Execute mining algorithms |
| `/api/recommendations/<item>` | GET | Get recommendations for item |
| `/api/rules` | GET | Get all association rules |
| `/api/stats` | GET | Get current statistics |

---

## 8. Usage Example

### Sample Workflow:

1. **Create Transactions**: Add 10+ transactions with various product combinations
2. **Preprocess**: Clean and validate data (expect ~90-100% retention for valid data)
3. **Mine**: Use min_support=0.2, min_confidence=0.5
4. **Analyze**: Compare Apriori vs Eclat execution times
5. **Recommend**: Select "milk" to see commonly purchased items

### Expected Results:
- Apriori typically finds 20-50 frequent itemsets
- Eclat produces similar results with different execution time
- Common patterns: dairy products, bakery items, produce bundles
- Strong rules often have confidence > 0.7 and lift > 1.5

---

## 9. Limitations and Future Work

### Current Limitations:
- In-memory storage (data lost on restart)
- No database persistence
- Limited to manual transaction creation
- No user authentication
- Single-user system

### Future Enhancements:
- Database integration (PostgreSQL/MongoDB)
- CSV import/export functionality
- User accounts and session management
- Visualization charts (support/confidence scatter plots)
- Additional metrics (conviction, leverage)
- Multiple dataset support
- Real-time mining updates
- Mobile-responsive design improvements

---

## 10. Conclusion

This project successfully implements a complete association rule mining system with:
- Two algorithms implemented from scratch
- Clean, maintainable code structure
- User-friendly web interface
- Comprehensive data preprocessing
- Performance comparison capabilities
- Practical product recommendation system

The application demonstrates the practical value of association rule mining in retail analytics and provides a solid foundation for further development and experimentation with different mining parameters and datasets.

---

## References

1. Agrawal, R., & Srikant, R. (1994). Fast algorithms for mining association rules.
2. Zaki, M. J. (2000). Scalable algorithms for association mining.
3. Han, J., Pei, J., & Kamber, M. (2011). Data Mining: Concepts and Techniques.
