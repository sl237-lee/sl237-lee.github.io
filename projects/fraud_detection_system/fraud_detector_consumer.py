"""
Kafka consumer that processes transactions and makes fraud predictions
"""
import json
import time
import pickle
import numpy as np
from kafka import KafkaConsumer, KafkaProducer
from datetime import datetime
import os
from dotenv import load_dotenv
import redis

load_dotenv()

class FraudDetector:
    def __init__(self):
        # Kafka setup
        self.consumer = KafkaConsumer(
            os.getenv('KAFKA_TOPIC_TRANSACTIONS'),
            bootstrap_servers=os.getenv('KAFKA_BOOTSTRAP_SERVERS'),
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            auto_offset_reset='latest',
            enable_auto_commit=True
        )
        
        self.producer = KafkaProducer(
            bootstrap_servers=os.getenv('KAFKA_BOOTSTRAP_SERVERS'),
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        
        # Redis for caching user features
        self.redis_client = redis.Redis(
            host=os.getenv('REDIS_HOST'),
            port=int(os.getenv('REDIS_PORT')),
            decode_responses=True
        )
        
        # Load model
        self.load_model()
        
        # Metrics
        self.total_processed = 0
        self.fraud_detected = 0
        self.latencies = []
    
    def load_model(self):
        """Load trained model and artifacts"""
        try:
            with open('models/fraud_detector.pkl', 'rb') as f:
                self.model = pickle.load(f)
            
            with open('models/label_encoder.pkl', 'rb') as f:
                self.label_encoder = pickle.load(f)
            
            print("✅ Model loaded successfully")
        except FileNotFoundError:
            print("⚠️  Model not found. Train the model first!")
            self.model = None
    
    def extract_features(self, transaction):
        """Extract features from transaction"""
        # Parse timestamp
        ts = datetime.fromisoformat(transaction['timestamp'])
        hour = ts.hour
        day_of_week = ts.weekday()
        
        # Encode category
        category_encoded = self.label_encoder.transform([transaction['category']])[0]
        
        # Feature engineering
        is_night = (hour >= 22) or (hour <= 5)
        is_weekend = day_of_week in [5, 6]
        amount_log = np.log1p(transaction['amount'])
        
        features = np.array([[
            transaction['amount'],
            amount_log,
            category_encoded,
            hour,
            day_of_week,
            is_night,
            is_weekend,
            transaction['latitude'],
            transaction['longitude']
        ]])
        
        return features
    
    def predict(self, transaction):
        """Make fraud prediction"""
        if self.model is None:
            return None, None, None
        
        start_time = time.time()
        
        # Extract features
        features = self.extract_features(transaction)
        
        # Make prediction
        fraud_prob = self.model.predict_proba(features)[0][1]
        is_fraud = bool(fraud_prob > 0.5)
        
        # Calculate latency
        latency_ms = (time.time() - start_time) * 1000
        
        return fraud_prob, is_fraud, latency_ms
    
    def cache_user_features(self, user_id, transaction):
        """Cache user transaction history in Redis"""
        key = f"user:{user_id}:transactions"
        
        # Store last 10 transactions
        self.redis_client.lpush(key, json.dumps({
            'amount': transaction['amount'],
            'timestamp': transaction['timestamp'],
            'category': transaction['category']
        }))
        self.redis_client.ltrim(key, 0, 9)  # Keep only last 10
        self.redis_client.expire(key, 86400)  # Expire in 24 hours
    
    def process_transaction(self, transaction):
        """Process a single transaction"""
        # Make prediction
        fraud_prob, is_fraud, latency_ms = self.predict(transaction)
        
        if fraud_prob is None:
            return
        
        # Cache user features
        self.cache_user_features(transaction['user_id'], transaction)
        
        # Create prediction result
        prediction = {
            'transaction_id': transaction['transaction_id'],
            'user_id': transaction['user_id'],
            'amount': transaction['amount'],
            'fraud_probability': float(fraud_prob),
            'is_fraud_predicted': is_fraud,
            'actual_fraud': transaction.get('is_fraud', None),
            'inference_time_ms': float(latency_ms),
            'timestamp': datetime.now().isoformat()
        }
        
        # Send to predictions topic
        self.producer.send(os.getenv('KAFKA_TOPIC_PREDICTIONS'), prediction)
        self.producer.flush()
        
        # Update metrics
        self.total_processed += 1
        if is_fraud:
            self.fraud_detected += 1
        self.latencies.append(latency_ms)
        
        # Log prediction
        match_indicator = "✅" if is_fraud == transaction.get('is_fraud') else "❌"
        fraud_indicator = "🚨 FRAUD" if is_fraud else "✅ LEGIT"
        print(f"{match_indicator} {fraud_indicator} | {transaction['transaction_id']} | "
              f"Prob: {fraud_prob:.3f} | Latency: {latency_ms:.2f}ms")
        
        # Print metrics every 10 transactions
        if self.total_processed % 10 == 0:
            avg_latency = np.mean(self.latencies[-100:]) if self.latencies else 0
            fraud_rate = (self.fraud_detected / self.total_processed) * 100
            print(f"\n📊 Metrics: Processed={self.total_processed} | "
                  f"Fraud Rate={fraud_rate:.1f}% | Avg Latency={avg_latency:.2f}ms\n")
    
    def run(self):
        """Start consuming and processing transactions"""
        print("🚀 Fraud Detector started")
        print(f"📥 Consuming from: {os.getenv('KAFKA_TOPIC_TRANSACTIONS')}")
        print(f"📤 Publishing to: {os.getenv('KAFKA_TOPIC_PREDICTIONS')}\n")
        
        try:
            for message in self.consumer:
                transaction = message.value
                self.process_transaction(transaction)
                
        except KeyboardInterrupt:
            print(f"\n⏹️  Stopped. Processed {self.total_processed} transactions")
        finally:
            self.consumer.close()
            self.producer.close()
            self.redis_client.close()

if __name__ == "__main__":
    detector = FraudDetector()
    
    # Wait for services to be ready
    print("⏳ Waiting for Kafka to be ready...")
    time.sleep(5)
    
    detector.run()
