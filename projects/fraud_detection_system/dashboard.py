"""
Real-time monitoring dashboard for fraud detection system
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from kafka import KafkaConsumer
import json
import time
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from collections import deque

load_dotenv()

# Page config
st.set_page_config(
    page_title="Fraud Detection Monitor",
    page_icon="🚨",
    layout="wide"
)

# Initialize session state
if 'predictions' not in st.session_state:
    st.session_state.predictions = deque(maxlen=100)
if 'metrics' not in st.session_state:
    st.session_state.metrics = {
        'total': 0,
        'fraud': 0,
        'legitimate': 0,
        'avg_latency': 0,
        'latencies': deque(maxlen=50)
    }

def create_consumer():
    """Create Kafka consumer for predictions"""
    try:
        consumer = KafkaConsumer(
            os.getenv('KAFKA_TOPIC_PREDICTIONS'),
            bootstrap_servers=os.getenv('KAFKA_BOOTSTRAP_SERVERS'),
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            auto_offset_reset='latest',
            enable_auto_commit=True,
            consumer_timeout_ms=1000
        )
        return consumer
    except Exception as e:
        st.error(f"Failed to connect to Kafka: {e}")
        return None

def update_metrics(prediction):
    """Update metrics with new prediction"""
    st.session_state.metrics['total'] += 1
    
    if prediction['is_fraud_predicted']:
        st.session_state.metrics['fraud'] += 1
    else:
        st.session_state.metrics['legitimate'] += 1
    
    st.session_state.metrics['latencies'].append(prediction['inference_time_ms'])
    st.session_state.metrics['avg_latency'] = sum(st.session_state.metrics['latencies']) / len(st.session_state.metrics['latencies'])

def main():
    st.title("Real-Time Fraud Detection Monitor")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")
        auto_refresh = st.checkbox("Auto-refresh", value=True)
        refresh_interval = st.slider("Refresh interval (seconds)", 1, 10, 2)
        
        st.markdown("---")
        st.markdown("### 📊 System Info")
        st.info(f"**Kafka Topic:** {os.getenv('KAFKA_TOPIC_PREDICTIONS')}")
        st.info(f"**Bootstrap Server:** {os.getenv('KAFKA_BOOTSTRAP_SERVERS')}")
    
    # Create consumer
    consumer = create_consumer()
    
    if consumer is None:
        st.error("Unable to connect to Kafka. Make sure Kafka is running.")
        return
    
    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    metric1 = col1.empty()
    metric2 = col2.empty()
    metric3 = col3.empty()
    metric4 = col4.empty()
    
    # Charts
    chart_col1, chart_col2 = st.columns(2)
    
    fraud_chart = chart_col1.empty()
    latency_chart = chart_col2.empty()
    
    # Recent transactions table
    st.subheader("📋 Recent Transactions")
    table_placeholder = st.empty()
    
    # Main loop
    while True:
        # Consume new messages
        messages_consumed = 0
        for message in consumer:
            prediction = message.value
            st.session_state.predictions.append(prediction)
            update_metrics(prediction)
            messages_consumed += 1
            
            if messages_consumed >= 10:  # Process max 10 messages per iteration
                break
        
        # Update metrics
        metrics = st.session_state.metrics
        
        metric1.metric(
            "Total Transactions",
            f"{metrics['total']:,}",
            delta=f"+{messages_consumed}" if messages_consumed > 0 else None
        )
        
        fraud_rate = (metrics['fraud'] / metrics['total'] * 100) if metrics['total'] > 0 else 0
        metric2.metric(
            "Fraud Detected",
            f"{metrics['fraud']:,}",
            delta=f"{fraud_rate:.1f}%"
        )
        
        metric3.metric(
            "Legitimate",
            f"{metrics['legitimate']:,}"
        )
        
        metric4.metric(
            "Avg Latency",
            f"{metrics['avg_latency']:.2f} ms",
            delta="🎯 Target: <100ms" if metrics['avg_latency'] < 100 else "⚠️ Above target"
        )
        
        # Fraud distribution pie chart
        if metrics['total'] > 0:
            fraud_data = pd.DataFrame({
                'Type': ['Fraud', 'Legitimate'],
                'Count': [metrics['fraud'], metrics['legitimate']]
            })
            
            fig_fraud = px.pie(
                fraud_data,
                values='Count',
                names='Type',
                title='Transaction Distribution',
                color='Type',
                color_discrete_map={'Fraud': '#ff4444', 'Legitimate': '#44ff44'}
            )
            fraud_chart.plotly_chart(fig_fraud, use_container_width=True)
        
        # Latency chart
        if len(metrics['latencies']) > 0:
            latency_data = pd.DataFrame({
                'Transaction': list(range(len(metrics['latencies']))),
                'Latency (ms)': list(metrics['latencies'])
            })
            
            fig_latency = go.Figure()
            fig_latency.add_trace(go.Scatter(
                x=latency_data['Transaction'],
                y=latency_data['Latency (ms)'],
                mode='lines+markers',
                name='Latency',
                line=dict(color='#1f77b4')
            ))
            fig_latency.add_hline(
                y=100,
                line_dash="dash",
                line_color="red",
                annotation_text="Target: 100ms"
            )
            fig_latency.update_layout(
                title='Inference Latency Over Time',
                xaxis_title='Transaction Number',
                yaxis_title='Latency (ms)'
            )
            latency_chart.plotly_chart(fig_latency, use_container_width=True)
        
        # Recent transactions table
        if len(st.session_state.predictions) > 0:
            recent_df = pd.DataFrame(list(st.session_state.predictions))
            recent_df = recent_df[['transaction_id', 'amount', 'fraud_probability', 
                                   'is_fraud_predicted', 'inference_time_ms', 'timestamp']]
            recent_df = recent_df.sort_values('timestamp', ascending=False).head(10)
            
            # Format columns
            recent_df['amount'] = recent_df['amount'].apply(lambda x: f"${x:,.2f}")
            recent_df['fraud_probability'] = recent_df['fraud_probability'].apply(lambda x: f"{x:.1%}")
            recent_df['is_fraud_predicted'] = recent_df['is_fraud_predicted'].apply(lambda x: "🚨 FRAUD" if x else "✅ LEGIT")
            recent_df['inference_time_ms'] = recent_df['inference_time_ms'].apply(lambda x: f"{x:.2f}ms")
            
            table_placeholder.dataframe(recent_df, use_container_width=True, hide_index=True)
        
        # Auto-refresh
        if auto_refresh:
            time.sleep(refresh_interval)
            st.rerun()
        else:
            break

if __name__ == "__main__":
    main()
