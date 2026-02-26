"""
Generate synthetic transaction data with fraud patterns
"""
import json
import random
import time
from datetime import datetime, timedelta
from kafka import KafkaProducer
from faker import Faker
import os
from dotenv import load_dotenv

load_dotenv()
fake = Faker()

# Merchant categories
CATEGORIES = [
    'grocery', 'restaurant', 'gas_station', 'online_retail', 
    'entertainment', 'travel', 'healthcare', 'utilities'
]

# Known fraud patterns
FRAUD_PATTERNS = {
    'high_amount': {'threshold': 1000, 'fraud_rate': 0.4},
    'foreign_transaction': {'fraud_rate': 0.3},
    'multiple_transactions': {'count': 5, 'timeframe': 3600, 'fraud_rate': 0.5},
    'unusual_hours': {'hours': [0, 1, 2, 3, 4, 5], 'fraud_rate': 0.25}
}

class TransactionGenerator:
    def __init__(self):
        self.producer = KafkaProducer(
            bootstrap_servers=os.getenv('KAFKA_BOOTSTRAP_SERVERS'),
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        self.topic = os.getenv('KAFKA_TOPIC_TRANSACTIONS')
        self.user_history = {}  # Track user transaction history
        
    def generate_transaction(self, force_fraud=False):
        """Generate a single transaction"""
        user_id = f"USER_{random.randint(1, 1000):04d}"
        
        # Determine if transaction is fraud
        is_fraud = force_fraud or random.random() < 0.05  # 5% base fraud rate
        
        if is_fraud:
            amount = random.uniform(500, 5000)  # Higher amounts for fraud
            category = random.choice(['online_retail', 'entertainment'])
        else:
            amount = random.uniform(5, 500)  # Normal transaction amounts
            category = random.choice(CATEGORIES)
        
        transaction = {
            'transaction_id': f"TXN_{datetime.now().strftime('%Y%m%d%H%M%S')}_{random.randint(1000, 9999)}",
            'user_id': user_id,
            'amount': round(amount, 2),
            'merchant': fake.company(),
            'category': category,
            'timestamp': datetime.now().isoformat(),
            'latitude': float(fake.latitude()),
            'longitude': float(fake.longitude()),
            'device_id': f"DEV_{random.randint(1, 100):03d}",
            'ip_address': fake.ipv4(),
            'is_fraud': is_fraud  # Ground truth (in production, this would be unknown)
        }
        
        # Apply fraud patterns
        if is_fraud:
            # High amount pattern
            if random.random() < 0.5:
                transaction['amount'] = random.uniform(1000, 5000)
            
            # Unusual hours pattern
            if random.random() < 0.3:
                hour = random.choice(FRAUD_PATTERNS['unusual_hours']['hours'])
                transaction['timestamp'] = datetime.now().replace(hour=hour).isoformat()
        
        return transaction
    
    def send_transaction(self, transaction):
        """Send transaction to Kafka"""
        try:
            self.producer.send(self.topic, transaction)
            self.producer.flush()
            return True
        except Exception as e:
            print(f"Error sending transaction: {e}")
            return False
    
    def generate_stream(self, transactions_per_second=2, duration_seconds=None):
        """Generate continuous stream of transactions"""
        print(f"🚀 Starting transaction stream to topic '{self.topic}'")
        print(f"📊 Rate: {transactions_per_second} transactions/second")
        
        count = 0
        start_time = time.time()
        
        try:
            while True:
                # Generate transaction
                transaction = self.generate_transaction()
                
                # Send to Kafka
                if self.send_transaction(transaction):
                    count += 1
                    fraud_indicator = "🚨 FRAUD" if transaction['is_fraud'] else "✅ LEGIT"
                    print(f"{fraud_indicator} | TXN #{count} | ${transaction['amount']:.2f} | {transaction['category']}")
                
                # Rate limiting
                time.sleep(1 / transactions_per_second)
                
                # Check duration
                if duration_seconds and (time.time() - start_time) > duration_seconds:
                    break
                    
        except KeyboardInterrupt:
            print(f"\n⏹️  Stopped. Generated {count} transactions")
        finally:
            self.producer.close()

if __name__ == "__main__":
    generator = TransactionGenerator()
    
    # Wait for Kafka to be ready
    print("⏳ Waiting for Kafka to be ready...")
    time.sleep(10)
    
    # Start generating transactions
    generator.generate_stream(transactions_per_second=2)
