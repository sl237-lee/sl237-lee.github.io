import gradio as gr
from deepface import DeepFace
import cv2
import numpy as np
from PIL import Image

def estimate_age(image):
    """Estimate age from face image"""
    try:
        # Convert PIL to numpy array
        img_array = np.array(image)
        
        # Analyze face
        result = DeepFace.analyze(
            img_path=img_array, 
            actions=['age', 'gender', 'emotion'],
            enforce_detection=False
        )
        
        # Extract results
        if isinstance(result, list):
            result = result[0]
        
        age = result['age']
        gender = result['dominant_gender']
        emotion = result['dominant_emotion']
        
        # Format results
        output = f"""
# Analysis Results

## Estimated Age: **{age} years old**

### Additional Info:
- **Gender:** {gender.capitalize()}
- **Dominant Emotion:** {emotion.capitalize()}

---
*This is an AI estimate and may not be perfectly accurate*
        """
        
        return output
        
    except Exception as e:
        return f"❌ Error: {str(e)}\n\nPlease ensure the image contains a clear face."

# Create Gradio interface
with gr.Blocks(title="Age Detector") as demo:
    gr.Markdown("""
    # 👤 AI Age Detector
    
    Upload a photo to estimate age using deep learning!
    
    **Requirements:**
    - Clear face photo
    - Good lighting
    - Face should be visible
    """)
    
    with gr.Row():
        with gr.Column():
            image_input = gr.Image(type="pil", label="📸 Upload Face Photo")
            predict_btn = gr.Button("🔍 Analyze", variant="primary", size="lg")
            
            gr.Markdown("""
            ### 💡 Tips:
            - Use a front-facing photo
            - Ensure face is well-lit
            - Avoid sunglasses or face coverings
            """)
        
        with gr.Column():
            results_output = gr.Markdown(label="Results")
    
    gr.Markdown("""
    ---
    ### About:
    This app uses DeepFace AI models to estimate age, gender, and emotion from facial photos.
    
    **Note:** Results are estimates and may vary based on image quality and lighting.
    """)
    
    predict_btn.click(
        fn=estimate_age,
        inputs=image_input,
        outputs=results_output
    )

if __name__ == "__main__":
    demo.launch(share=True)
