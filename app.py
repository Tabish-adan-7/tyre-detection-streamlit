import streamlit as st
import tensorflow as tf
import numpy as np
import cv2
from PIL import Image
import time
from datetime import datetime
import pandas as pd
import base64

# Page Configuration
st.set_page_config(
    page_title="Tyre Inspector Pro",
    page_icon="🛞",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Professional Industrial Look
st.markdown("""
<style>
    /* Import Inter Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* Global Styles */
    .stApp {
        font-family: 'Inter', sans-serif;
    }

    /* Main Header */
    .industrial-header {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        padding: 1rem;
        border-radius: 0 0 10px 10px;
        margin-bottom: 2rem;
        color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }

    /* Drop Zone */
    .drop-zone {
        border: 3px dashed #4a5568;
        border-radius: 20px;
        padding: 3rem;
        text-align: center;
        background: #f7fafc;
        transition: all 0.3s;
        cursor: pointer;
    }
    .drop-zone:hover {
        border-color: #667eea;
        background: #ebf4ff;
    }

    /* Safety Scale */
    .safety-scale {
        background: linear-gradient(90deg, #f56565 0%, #ecc94b 50%, #48bb78 100%);
        height: 12px;
        border-radius: 6px;
        margin: 1rem 0;
        position: relative;
    }
    .safety-marker {
        width: 20px;
        height: 20px;
        background: white;
        border: 3px solid #2d3748;
        border-radius: 50%;
        position: absolute;
        top: -4px;
        transform: translateX(-50%);
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }

    /* Result Cards */
    .result-card {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin: 1rem 0;
        border-left: 5px solid;
    }
    .result-card.good {
        border-left-color: #48bb78;
    }
    .result-card.suspicious {
        border-left-color: #ecc94b;
    }
    .result-card.defective {
        border-left-color: #f56565;
    }

    /* Status Badge */
    .status-badge {
        padding: 0.5rem 1.5rem;
        border-radius: 30px;
        font-weight: 600;
        font-size: 1.2rem;
        display: inline-block;
        margin: 1rem 0;
    }
    .badge-good {
        background: #c6f6d5;
        color: #22543d;
    }
    .badge-suspicious {
        background: #feebc8;
        color: #7b341e;
    }
    .badge-defective {
        background: #fed7d7;
        color: #742a2a;
    }

    /* Comparison View */
    .comparison-container {
        display: flex;
        gap: 1rem;
        margin: 1rem 0;
    }
    .image-box {
        flex: 1;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 0.5rem;
        background: white;
    }
    .image-label {
        text-align: center;
        font-weight: 600;
        color: #4a5568;
        margin-bottom: 0.5rem;
    }

    /* Progress Animation */
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
    .scanning-pulse {
        animation: pulse 1.5s infinite;
        text-align: center;
        padding: 1rem;
        font-size: 1.2rem;
        color: #4a5568;
    }

    /* Box Legend */
    .box-legend {
        display: flex;
        gap: 1rem;
        margin: 1rem 0;
        padding: 0.5rem;
        background: #f7fafc;
        border-radius: 8px;
    }
    .legend-item {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 0.9rem;
    }
    .color-box {
        width: 20px;
        height: 20px;
        border-radius: 4px;
    }
    .color-box.red { background: #dc2626; }
    .color-box.orange { background: #f97316; }
    .color-box.yellow { background: #eab308; }

    /* Review Section */
    .review-section {
        background: #fff3cd;
        border: 1px solid #ffeeba;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        color: #856404;
    }

    /* Footer */
    .industrial-footer {
        text-align: center;
        padding: 1rem;
        color: #718096;
        font-size: 0.9rem;
        border-top: 1px solid #e2e8f0;
        margin-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'history' not in st.session_state:
    st.session_state.history = []
if 'total_scans' not in st.session_state:
    st.session_state.total_scans = 0
    st.session_state.good_count = 0
    st.session_state.suspicious_count = 0
    st.session_state.defective_count = 0

# Industrial Header
st.markdown("""
<div class="industrial-header">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <div style="display: flex; align-items: center; gap: 1rem;">
            <h1 style="margin: 0; font-size: 2rem;">🛞 Tyre Inspector Pro</h1>
            <span style="background: rgba(255,255,255,0.2); padding: 0.3rem 1rem; border-radius: 20px; font-size: 0.9rem;">Industrial Grade</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    with st.expander("🎮 Controls", expanded=True):
        # Visual Safety Scale
        st.markdown("### Safety Scale")
        st.markdown("""
        <div class="safety-scale">
            <div class="safety-marker" style="left: 14%;"></div>
            <div class="safety-marker" style="left: 30%;"></div>
        </div>
        <div style="display: flex; justify-content: space-between; font-size: 0.9rem; color: #718096;">
            <span>🔴 Critical</span>
            <span>🟡 Review</span>
            <span>🟢 Safe</span>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        # Mode selection
        mode_tab = st.radio(
            "Inspection Mode",
            ["📸 Single", "🎥 Live", "📁 Batch"],
            horizontal=True,
            label_visibility="collapsed"
        )

        mode_map = {"📸 Single": "Upload", "🎥 Live": "Camera", "📁 Batch": "Batch"}
        mode = mode_map[mode_tab]

        st.markdown("---")

        # Options
        show_boxes = st.toggle("Show Defect Boxes", value=True)
        compare_view = st.toggle("Show Original Comparison", value=True)

    # Session Analytics
    with st.expander("📊 Session Analytics", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total", st.session_state.total_scans)
        with col2:
            pass_rate = (st.session_state.good_count / max(st.session_state.total_scans, 1)) * 100
            st.metric("Pass Rate", f"{pass_rate:.0f}%")
        with col3:
            st.metric("Quality Issues", st.session_state.suspicious_count)

        if st.session_state.history:
            st.markdown("### Recent")
            for record in st.session_state.history[-3:]:
                icon = "✅" if record['category'] == 'good' else "⚠️" if record['category'] == 'suspicious' else "❌"
                st.markdown(f"{icon} {record['time']} - {record['score']:.2f}")

    with st.expander("ℹ️ About", expanded=False):
        st.markdown("**Model:** DenseNet121")
        st.markdown("**Version:** Pilot(1.1)")
        st.markdown("**Industrial AI Tyre Inspection System**")


# Load Model
@st.cache_resource
def load_model():
    try:
        model = tf.keras.models.load_model("DenseNet121_finetuned.keras")
        return model
    except Exception as e:
        st.error(f"System Error: Model initialization failed")
        return None


model = load_model()


def preprocess_image(image):
    """Preprocess image and check for quality"""
    try:
        if len(image.shape) == 2:
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        elif image.shape[2] == 4:
            image = cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)

        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        brightness = np.mean(gray)

        if brightness < 15:
            return None, "Image too dark. Please ensure proper lighting.", None

        img_resized = cv2.resize(image, (224, 224))
        img_array = img_resized / 255.0
        img_array = np.expand_dims(img_array, axis=0)

        return img_array, None, {"brightness": brightness, "original": image}
    except Exception as e:
        return None, "Image processing failed", None


def remove_text_regions(image):
    """Remove text/logos to match training data distribution"""
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

    # Detect text regions (high gradient areas)
    grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
    grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
    gradient_magnitude = np.sqrt(grad_x ** 2 + grad_y ** 2)

    # Threshold to find text-like regions
    _, text_mask = cv2.threshold(gradient_magnitude, 30, 255, cv2.THRESH_BINARY)

    # Dilate to cover the text areas better
    kernel = np.ones((5, 5), np.uint8)
    text_mask = cv2.dilate(text_mask, kernel, iterations=2)

    # Blur only the text regions
    blurred = cv2.GaussianBlur(image, (15, 15), 0)
    result = image.copy()
    result[text_mask > 0] = blurred[text_mask > 0]

    return result
#function to check if the image is blurry
def is_image_blurry(image, threshold=0.05):
    """Detect blur using edge density"""
    try:
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

        # Detect edges using Canny
        edges = cv2.Canny(gray, 50, 150)

        # Calculate edge density (percentage of image that is edges)
        edge_density = np.sum(edges > 0) / edges.size

        print(f"Edge density: {edge_density:.4f}")

        # Blurry = LOW edge density (few edges)
        is_blurry = edge_density < threshold

        return is_blurry, edge_density

    except Exception as e:
        print(f"Blur detection error: {e}")
        return False, 0


def check_image_resolution(image):
    """Check image resolution and return quality info"""
    try:
        h, w = image.shape[:2]
        is_hd = (w >= 640) or (h >= 640)

        print(f"Image resolution: {w} x {h} pixels - {'Acceptible' if is_hd else 'Low resolution'}")

        return is_hd, w, h

    except Exception as e:
        print(f"Resolution check error: {e}")
        return True, 0, 0  # Default to HD if error
def draw_defect_boxes(image, confidence):
    """Draw professional bounding boxes around defects"""
    try:
        # Create a copy of the image
        boxed_image = image.copy()

        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)

        # Apply adaptive thresholding
        thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                       cv2.THRESH_BINARY_INV, 11, 2)

        # Morphological operations to clean up
        kernel = np.ones((3, 3), np.uint8)
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)

        # Find contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        box_count = 0
        large_count = medium_count = small_count = 0

        for contour in contours:
            area = cv2.contourArea(contour)

            # Filter based on area
            if 100 < area < 5000:
                # Get bounding box
                x, y, w, h = cv2.boundingRect(contour)

                # Calculate aspect ratio to filter out long, thin lines
                aspect_ratio = w / h if h > 0 else 0

                if 0.2 < aspect_ratio < 5:
                    box_count += 1

                    # Color code based on area size
                    if area > 500:
                        color = (220, 38, 38)  # Red for large defects
                        thickness = 3
                        large_count += 1
                        label = f"L{large_count}"
                    elif area > 200:
                        color = (245, 158, 11)  # Orange for medium defects
                        thickness = 2
                        medium_count += 1
                        label = f"M{medium_count}"
                    else:
                        color = (250, 204, 21)  # Yellow for small defects
                        thickness = 2
                        small_count += 1
                        label = f"S{small_count}"

                    # Draw rectangle
                    cv2.rectangle(boxed_image, (x, y), (x + w, y + h), color, thickness)

                    # Add label with background
                    cv2.rectangle(boxed_image, (x, y - 25), (x + 40, y - 5), color, -1)
                    cv2.putText(boxed_image, label, (x + 5, y - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        # Add legend at the top
        legend_y = 30
        cv2.putText(boxed_image, f"Large: {large_count}", (10, legend_y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (220, 38, 38), 2)
        cv2.putText(boxed_image, f"Medium: {medium_count}", (150, legend_y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (245, 158, 11), 2)
        cv2.putText(boxed_image, f"Small: {small_count}", (300, legend_y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (250, 204, 21), 2)

        return boxed_image, box_count, large_count, medium_count, small_count
    except Exception as e:
        st.warning(f"Box drawing error: {str(e)}")
        return image, 0, 0, 0, 0


def has_prominent_logo(image):
    """Check if image has prominent text/logo"""
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

    # Count high-frequency edges (text areas)
    edges = cv2.Canny(gray, 50, 150)
    edge_ratio = np.sum(edges > 0) / edges.size

    # Also check for high contrast regions
    laplacian = cv2.Laplacian(gray, cv2.CV_64F)
    contrast_ratio = np.mean(np.abs(laplacian))

    # If high edge density or contrast, likely has text/logo
    return edge_ratio > 0.08 or contrast_ratio > 30


def predict_image(model, image):
    """Defect detection - Reject low-res ONLY for good tyres"""

    # Step 1: Check image resolution
    is_hd, width, height = check_image_resolution(image)

    # Step 2: Check blur using edge density
    is_blurry, edge_density = is_image_blurry(image, threshold=0.02)

    if is_blurry:
        return "BLURRY", 0, "blurry", "📷 BLURRY IMAGE - Please upload a clear image", None

    # Step 3: Check for logo presence
    has_logo = has_prominent_logo(image)

    # Step 4: Clean and predict
    image_cleaned = remove_text_regions(image)
    processed_img, error, metrics = preprocess_image(image_cleaned)
    if error:
        return None, None, None, error, None

    try:
        prediction = model.predict(processed_img, verbose=0)
        confidence = float(prediction[0][0])

        # Store original confidence
        original_confidence = confidence

        # SPECIAL HANDLING: If low resolution AND model says GOOD (confidence > 0.60)
        if not is_hd and confidence > 0.60:
            return "LOW QUALITY", confidence, "low_quality", f" IMAGE QUALITY TOO LOW ({width}x{height}) - Please upload a higher quality image (minimum 640p)", None

        # Normal processing for:
        # - HD images (any result)
        # - Low-res defective tyres (confidence <= 0.60)

        # Threshold at 0.60
        if confidence > 0.60:
            label = "PASS"
            category = "good"
            message = "✅ Tyre passed inspection - Safe for use"
        else:
            label = "REJECT"
            category = "defective"
            message = "❌ Tyre rejected - Defect detected"

        # Add metrics for tracking
        if metrics:
            metrics['has_logo'] = has_logo
            metrics['logo_detected'] = has_logo
            metrics['resolution'] = f"{width}x{height}"
            metrics['is_hd'] = is_hd
            metrics['original_confidence'] = original_confidence

        return label, confidence, category, message, metrics

    except Exception as e:
        return None, None, None, f"Prediction error: {str(e)}", None

# Main Content Area
if mode == "Upload":
    st.markdown("### 📸 Upload Inspection")

    # State 1: Idle - Drop zone
    if 'uploaded_image' not in st.session_state:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("""
            <div class="drop-zone">
                <h2 style="font-size: 3rem; margin: 0;">📤</h2>
                <h3>Drop your tyre image here</h3>
                <p style="color: #718096;">or click to browse</p>
                <p style="font-size: 0.9rem; color: #a0aec0;">Supports: JPG, PNG</p>
            </div>
            """, unsafe_allow_html=True)

            uploaded_file = st.file_uploader(
                "Upload Tyre image",
                type=["jpg", "jpeg", "png"],
                label_visibility="collapsed",
                key="uploader"
            )

            if uploaded_file:
                file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
                image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
                st.session_state.uploaded_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                st.session_state.processing = True
                st.rerun()

    # State 2 & 3: Processing/Result
    else:
        image = st.session_state.uploaded_image

        # Process image
        if st.session_state.get('processing', False):
            with st.spinner("🔍 Analyzing tyre surface..."):
                # Get prediction
                label, confidence, category, recommendation, metrics = predict_image(model, image)

                if label:
                    if label:
                        # Draw boxes ONLY for defective or suspicious images, not for good ones
                        boxed_image = None
                        box_count = large = medium = small = 0

                        if show_boxes and category in ['defective','suspicious']:  # Only draw boxes for non-good images
                            boxed_image, box_count, large, medium, small = draw_defect_boxes(image, confidence)

                    # Store results
                    st.session_state.result = {
                        'label': label,
                        'confidence': confidence,
                        'category': category,
                        'recommendation': recommendation,
                        'boxed_image': boxed_image,
                        'box_count': box_count,
                        'large': large,
                        'medium': medium,
                        'small': small,
                        'original_image': image
                    }

                    # Update stats
                    st.session_state.total_scans += 1
                    if category == 'good':
                        st.session_state.good_count += 1
                    elif category == 'suspicious':
                        st.session_state.suspicious_count += 1
                    else:
                        st.session_state.defective_count += 1

                    # Add to history
                    st.session_state.history.append({
                        'time': datetime.now().strftime("%H:%M"),
                        'score': confidence,
                        'category': category
                    })

                st.session_state.processing = False
                st.rerun()

        # Display results
        else:
            result = st.session_state.result

            # Show comparison view if enabled
            if compare_view and show_boxes and result['boxed_image'] is not None:
                st.markdown("#### 🔍 Comparison View")
                col1, col2 = st.columns(2)

                with col1:
                    st.markdown('<div class="image-label">📸 Original Image</div>', unsafe_allow_html=True)
                    st.image(result['original_image'], use_container_width=True)

                with col2:
                    st.markdown('<div class="image-label">🔍 Detected Defects</div>', unsafe_allow_html=True)
                    st.image(result['boxed_image'], use_container_width=True)

                    # Show box statistics
                    if result['box_count'] > 0:
                        st.markdown(f"""
                        <div class="box-legend">
                            <div class="legend-item"><span class="color-box red"></span> Large: {result['large']}</div>
                            <div class="legend-item"><span class="color-box orange"></span> Medium: {result['medium']}</div>
                            <div class="legend-item"><span class="color-box yellow"></span> Small: {result['small']}</div>
                            <div class="legend-item">📍 Total: {result['box_count']}</div>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                # Single image view
                st.markdown("#### 🔍 Inspection View")
                if show_boxes and result['boxed_image'] is not None:
                    st.image(result['boxed_image'], use_container_width=True)

                    if result['box_count'] > 0:
                        st.markdown(f"""
                        <div class="box-legend">
                            <div class="legend-item"><span class="color-box red"></span> Large: {result['large']}</div>
                            <div class="legend-item"><span class="color-box orange"></span> Medium: {result['medium']}</div>
                            <div class="legend-item"><span class="color-box yellow"></span> Small: {result['small']}</div>
                            <div class="legend-item">📍 Total: {result['box_count']}</div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.image(result['original_image'], use_container_width=True)

            # Result Card (separate from images)
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                card_class = f"result-card {result['category']}"
                badge_class = f"status-badge badge-{result['category']}"
                badge_icon = "✅" if result['category'] == 'good' else "⚠️" if result[
                                                                                  'category'] == 'suspicious' else "❌"

                # Calculate marker position for safety scale
                marker_pos = result['confidence'] * 100
                marker_color = "#48bb78" if result['confidence'] > 0.3 else "#ecc94b" if result[
                                                                                             'confidence'] > 0.14 else "#f56565"

                st.markdown(f"""
                <div class="{card_class}">
                    <div class="{badge_class}">{badge_icon} {result['label']}</div>

                """, unsafe_allow_html=True)

                # Show review section only for suspicious cases
                if result['category'] == 'suspicious':
                    st.markdown(f"""
                    <div class="review-section">
                        <strong>⚠️ Manual Inspection Required</strong><br>
                        {result['recommendation']}<br>
                        Please visually inspect the highlighted areas.
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.info(result['recommendation'])

                # Action buttons
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button("📄 Generate Report", use_container_width=True):
                        report = f"""
TYRE INSPECTION REPORT
======================
Date: {datetime.now().strftime("%Y-%m-%d %H:%M")}
Result: {result['label']}
Safety Score: {result['confidence'] * 100:.1f}%
Status: {result['recommendation']}
Defect Areas: {result.get('box_count', 0)}
- Large: {result.get('large', 0)}
- Medium: {result.get('medium', 0)}  
- Small: {result.get('small', 0)}
                        """
                        st.download_button("📥 Download Report", report,
                                           f"tyre_report_{datetime.now().strftime('%Y%m%d_%H%M')}.txt")

                with col_b:
                    if st.button("🔄 New Scan", use_container_width=True):
                        # Clear session state
                        keys_to_clear = ['uploaded_image', 'result', 'processing']
                        for key in keys_to_clear:
                            if key in st.session_state:
                                del st.session_state[key]
                        st.rerun()

                st.markdown("</div>", unsafe_allow_html=True)

elif mode == "Camera":
    st.markdown("### 🎥 Live Inspection")

    col1, col2 = st.columns([2, 1])

    with col1:
        camera_image = st.camera_input("", label_visibility="collapsed", key="camera")

    with col2:
        st.markdown("""
        <div style="background: #f7fafc; padding: 1rem; border-radius: 10px;">
            <h4>📝 Quick Guide</h4>
            <ol style="color: #4a5568;">
                <li>Position tyre in frame</li>
                <li>Ensure good lighting</li>
                <li>Click capture</li>
                <li>View instant results</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)

    if camera_image:
        bytes_data = camera_image.getvalue()
        cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
        image_rgb = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2RGB)

        with st.spinner("🔍 Analyzing..."):
            label, confidence, category, recommendation, metrics = predict_image(model, image_rgb)

            if label:
                # Update stats
                st.session_state.total_scans += 1
                if category == 'good':
                    st.session_state.good_count += 1
                elif category == 'suspicious':
                    st.session_state.suspicious_count += 1
                else:
                    st.session_state.defective_count += 1

                st.session_state.history.append({
                    'time': datetime.now().strftime("%H:%M"),
                    'score': confidence,
                    'category': category
                })

                # Draw boxes if enabled
                boxed_image = None
                box_count = large = medium = small = 0
                if show_boxes and category in ['defective', 'suspicious']:  # Only draw boxes for non-good images
                    boxed_image, box_count, large, medium, small = draw_defect_boxes(image_rgb, confidence)

                # Show comparison or single view
                if compare_view and show_boxes and boxed_image is not None:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown('<div class="image-label">📸 Original</div>', unsafe_allow_html=True)
                        st.image(image_rgb, use_container_width=True)
                    with col2:
                        st.markdown('<div class="image-label">🔍 Detected</div>', unsafe_allow_html=True)
                        st.image(boxed_image, use_container_width=True)
                else:
                    if show_boxes and boxed_image is not None:
                        st.image(boxed_image, use_container_width=True)
                    else:
                        st.image(image_rgb, use_container_width=True)

                # Result display
                color = "#48bb78" if category == 'good' else "#ecc94b" if category == 'suspicious' else "#f56565"
                icon = "✅" if category == 'good' else "⚠️" if category == 'suspicious' else "❌"

                st.markdown(f"""
                <div style="background: white; padding: 1.5rem; border-radius: 10px; border-left: 5px solid {color}; margin-top: 1rem;">
                    <h3 style="margin-top: 0;">{icon} {label}</h3>
                    <div style="font-size: 2.5rem; margin: 0.5rem 0;">{confidence * 100:.1f}%</div>
                    <p style="color: #718096;">Safety Score</p>
                """, unsafe_allow_html=True)

                if category == 'suspicious':
                    st.markdown(f"""
                    <div class="review-section" style="margin: 1rem 0;">
                        <strong>⚠️ Manual Inspection Required</strong><br>
                        {recommendation}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.info(recommendation)

                st.markdown("</div>", unsafe_allow_html=True)

elif mode == "Batch":
    st.markdown("### 📁 Batch Processing")

    uploaded_files = st.file_uploader(
        "Select multiple images",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=True,
        key="batch"
    )

    if uploaded_files:
        results = []
        progress_bar = st.progress(0)

        for i, file in enumerate(uploaded_files):
            progress_bar.progress((i + 1) / len(uploaded_files))

            file_bytes = np.asarray(bytearray(file.read()), dtype=np.uint8)
            image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            label, confidence, category, recommendation, metrics = predict_image(model, image_rgb)

            if label:
                # Draw boxes for preview if needed
                box_count = 0
                large = medium = small = 0
                if show_boxes and category in ['defective', 'suspicious']:  # Only count boxes for non-good images
                    _, box_count, large, medium, small = draw_defect_boxes(image_rgb, confidence)
                else:
                    box_count = large = medium = small = 0  # Set to zero for good images

                results.append({
                    "File": file.name[:20] + "..." if len(file.name) > 20 else file.name,
                    "Status": "✅" if label == "PASS" else "⚠️" if label in ["BLURRY", "LOW QUALITY"] else "❌",
                    "Score": f"{confidence * 100:.1f}%",
                    "Result": label,
                    "Defects": f"{box_count} (L:{large} M:{medium} S:{small})" if box_count > 0 else "None",
                    "Action": "Pass" if label == "PASS" else "Review" if label in ["BLURRY",
                                                                                   "LOW QUALITY"] else "Reject"
                })

                # Update stats
                st.session_state.total_scans += 1
                if label == "PASS":
                    st.session_state.good_count += 1
                elif label in ["BLURRY", "LOW QUALITY"]:
                    st.session_state.suspicious_count += 1
                else:
                    st.session_state.defective_count += 1

        progress_bar.empty()

        # Show results table
        st.markdown("### Batch Results")
        df = pd.DataFrame(results)
        st.dataframe(df, use_container_width=True, hide_index=True)

        # Summary
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total", len(results))
        with col2:
            passed = sum(1 for r in results if r["Result"] == "PASS")
            st.metric("✅ Pass",passed)
        with col3:
            rejected = sum(1 for r in results if r["Result"] == "REJECT")
            st.metric("⚠️ Review", rejected)
        with col4:
            low_quality = sum(1 for r in results if r["Result"] == "Low Quality")
            blurry = sum(1 for r in results if r["Result"]== "BLURRY")
            total_issues = low_quality + blurry
            st.metric("❌ Quality Issues", total_issues)

        # Download button
        if st.button("📥 Download Report"):
            csv = df.to_csv(index=False)
            b64 = base64.b64encode(csv.encode()).decode()
            href = f'<a href="data:file/csv;base64,{b64}" download="batch_report.csv">Click to Download CSV</a>'
            st.markdown(href, unsafe_allow_html=True)

# Footer
st.markdown("""
<div class="industrial-footer">
    <span>Industrial Grade AI Tyre Inspection System</span>
</div>
""", unsafe_allow_html=True)