from pathlib import Path
from datetime import datetime
from io import BytesIO
import hashlib
import json
import streamlit as st
import pandas as pd
from PIL import Image
from src.predict import predict_all, load_model
from disease_info import readable_name, get_disease_info

BASE = Path(__file__).resolve().parent
RESULTS = BASE / 'results'
HISTORY = BASE / 'results' / 'scan_history.json'

st.set_page_config(page_title='AgroVision | LeafLens AI', page_icon='🔬', layout='wide', initial_sidebar_state='expanded')
st.markdown("""<style>
:root {--navy:#101d35;--teal:#087f8c;--ink:#18324b;--muted:#64748b;}
.stApp {background:linear-gradient(135deg,#f6fafc 0%,#eaf4f8 100%);color:var(--ink)}
[data-testid="stSidebar"] {background:linear-gradient(180deg,#101d35,#182f4e);border-right:1px solid #2b4562}
[data-testid="stSidebar"] * {color:#e7f3f8 !important}
[data-testid="stSidebar"] [role="radiogroup"] label {border-radius:11px;padding:9px 12px;margin:2px 0}
[data-testid="stSidebar"] [role="radiogroup"] label:hover {background:#28445e}
h1,h2,h3 {color:#122b45 !important;letter-spacing:-.025em}
.block-container {max-width:1260px;padding-top:2rem;padding-bottom:4rem}
[data-testid="stMetric"] {background:#fff;border:1px solid #dce9ef;border-radius:17px;padding:17px;box-shadow:0 5px 22px #132d4210}
[data-testid="stMetricLabel"] {color:#587184}
.stButton>button[kind="primary"] {background:#087f8c;color:white;border:0;border-radius:11px;font-weight:700}
.stButton>button[kind="primary"]:hover {background:#056775;color:white}
[data-testid="stFileUploader"] {background:white;border-radius:15px;padding:12px;border:1px solid #dce9ef}
[data-testid="stExpander"] {background:white;border:1px solid #dce9ef;border-radius:13px;margin-bottom:9px}
[data-testid="stAlert"] {border-radius:13px}
.hero {background:linear-gradient(115deg,#101d35,#1a3e5b 65%,#087f8c);padding:38px 42px;border-radius:24px;color:white;margin-bottom:25px;box-shadow:0 14px 36px #102a3b24}
.hero .eyebrow {color:#7ce4dc;letter-spacing:.2em;font-size:12px;font-weight:800}
.hero h1 {color:white !important;font-size:clamp(32px,4vw,53px);line-height:1.12;margin:14px 0}
.hero p {color:#d5e6f0;font-size:16px;max-width:670px;line-height:1.7}
.hero .pill {display:inline-block;background:#ffffff1c;border:1px solid #ffffff35;border-radius:30px;padding:7px 13px;font-size:12px;color:#d6f6f2;margin-top:10px}
.section-kicker {font-size:12px;letter-spacing:.14em;color:#087f8c;font-weight:800;text-transform:uppercase;margin-bottom:6px}
.brand {font-size:25px;font-weight:850;color:#fff;letter-spacing:-.04em}
.brand span {color:#65e1d7}
.brand-sub {color:#b4d2dd;font-size:12px;letter-spacing:.16em;margin:0 0 22px}
</style>""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown('<div class="brand">◈ Agro<span>Vision</span></div><div class="brand-sub">LEAFLENS AI · CROP HEALTH</div>',unsafe_allow_html=True)
    page = st.radio('Navigate', ['Home', 'Disease Detection', 'Disease Library', 'Model Analytics', 'Scan History', 'About'], label_visibility='collapsed')
    st.divider()
    st.caption('🍅 Supported crop: Tomato')
    st.caption('🧠 Neural network: MobileNetV2')
    st.caption('Educational decision-support prototype; verify important findings.')

@st.cache_data
def read_history():
    if HISTORY.exists():
        try:
            return json.loads(HISTORY.read_text(encoding='utf-8'))
        except (json.JSONDecodeError, OSError):
            return []
    return []

def record_scan(disease, confidence, scores):
    items = read_history()
    items.insert(0, {'timestamp': datetime.now().isoformat(timespec='seconds'), 'disease': readable_name(disease), 'confidence': round(confidence,2), 'scores': {readable_name(k):round(v,3) for k,v in scores}})
    HISTORY.parent.mkdir(parents=True, exist_ok=True)
    HISTORY.write_text(json.dumps(items[:100], indent=2), encoding='utf-8')
    read_history.clear()

def model_status():
    try:
        _, classes = load_model()
        return len(classes)
    except Exception as exc:
        st.error(f'Model could not be loaded: {exc}')
        return 0

def show_detection():
    st.markdown('<div class="section-kicker">LEAFLENS AI / DIAGNOSTICS</div>',unsafe_allow_html=True)
    st.header('🔎 Analyse a tomato leaf')
    st.write('Upload a clear JPG or PNG photograph of a tomato leaf. Predictions are best-effort and may be unreliable on real-world images.')
    uploaded = st.file_uploader('Choose a leaf image', type=['jpg','jpeg','png'])
    if uploaded is None:
        st.info('Upload a leaf image to begin.')
        return
    try:
        img = Image.open(uploaded).convert('RGB')
    except Exception:
        st.error('The selected file is not a valid image.')
        return
    left, right = st.columns([1,1])
    with left:
        st.image(img, caption='Your uploaded leaf', use_container_width=True)
    with right:
        st.write(f'Image size: {img.width} × {img.height} pixels')
        if st.button('✨ Analyse leaf', type='primary', use_container_width=True):
            with st.spinner('Running MobileNetV2 inference...'):
                try:
                    scores = predict_all(img)
                except Exception as exc:
                    st.error(f'Prediction failed: {exc}')
                    return
            st.session_state['prediction'] = {'scores':scores, 'image_id': hashlib.sha256(uploaded.getvalue()).hexdigest()}
            record_scan(scores[0][0], scores[0][1], scores)
    result = st.session_state.get('prediction')
    if result and result['image_id'] == hashlib.sha256(uploaded.getvalue()).hexdigest():
        scores = result['scores']
        disease, confidence = scores[0]
        st.divider()
        st.subheader('Prediction report')
        a,b = st.columns(2)
        a.metric('Highest-scoring class', readable_name(disease))
        b.metric('Model confidence', f'{confidence:.2f}%')
        st.progress(min(1.0, confidence / 100))
        st.caption('Softmax confidence is not a calibrated probability or a confirmed diagnosis.')
        info = get_disease_info(disease)
        st.markdown('#### About this condition')
        st.write(info['symptoms'])
        st.markdown('#### Possible cause')
        st.write(info['cause'])
        st.markdown('#### General precautions')
        st.write(info['precautions'])
        with st.expander('Explore all 10 class scores'):
            df = pd.DataFrame([{'Class':readable_name(k), 'Score (%)':round(v,3)} for k,v in scores])
            st.bar_chart(df.set_index('Class'))
            st.dataframe(df, hide_index=True, use_container_width=True)
        report = f'''AGROVISION — LEAF ANALYSIS REPORT
Date: {datetime.now():%Y-%m-%d %H:%M}
Predicted class: {readable_name(disease)}
Model confidence: {confidence:.2f}%

Possible cause: {info['cause']}
Symptoms: {info['symptoms']}
General precautions: {info['precautions']}

All class scores:
''' + '\n'.join(f'{readable_name(k)}: {v:.2f}%' for k,v in scores) + '\n\nEducational prediction only; seek professional confirmation.'
        st.download_button('⬇ Download analysis report (TXT)', report, file_name='agrovision_report.txt', mime='text/plain')

if page == 'Home':
    st.markdown('''<div class="hero"><div class="eyebrow">AGROVISION / LEAFLENS AI</div><h1>Smarter insights for<br>healthier crops.</h1><p>Upload a tomato leaf photo, explore possible conditions, and understand your AI model — all in one intelligent crop-health workspace.</p><span class="pill">✦ Powered by MobileNetV2</span></div>''', unsafe_allow_html=True)
    st.markdown('<div class="section-kicker">Your workspace</div>', unsafe_allow_html=True)
    st.subheader('Crop intelligence at a glance')
    count = model_status()
    a,b,c = st.columns(3)
    a.metric('Supported crop','Tomato')
    b.metric('Model classes',count)
    c.metric('Model status','Ready' if count else 'Unavailable')
    st.info('Select Disease Detection in the sidebar to analyse a leaf, or explore the Disease Library and Model Analytics.')
elif page == 'Disease Detection':
    show_detection()
elif page == 'Disease Library':
    st.markdown('<div class="section-kicker">KNOWLEDGE BASE</div>',unsafe_allow_html=True)
    st.header('📚 Tomato disease library')
    from disease_info import DISEASE_INFO
    for name, info in DISEASE_INFO.items():
        with st.expander(name):
            st.write('**Possible cause:**', info['cause'])
            st.write('**Symptoms:**', info['symptoms'])
            st.write('**Precautions:**', info['precautions'])
elif page == 'Model Analytics':
    st.markdown('<div class="section-kicker">NEURAL NETWORK PERFORMANCE</div>',unsafe_allow_html=True)
    st.header('📊 Model analytics')
    st.caption('The plots below are saved project artifacts, not live recalculations.')
    history_file = RESULTS / 'training_history.json'
    if history_file.exists():
        with st.expander('Training history (raw data)'):
            try:
                st.json(json.loads(history_file.read_text(encoding='utf-8')))
            except (ValueError,OSError):
                st.warning('Training history could not be read.')
    for filename, title in [('training_curves.png','Training and validation curves'), ('confusion_matrix.png','Confusion matrix')]:
        st.subheader(title)
        path = RESULTS / filename
        if path.exists():
            st.image(str(path), use_container_width=True)
        else:
            st.warning(f'Missing artifact: {filename}')
    st.caption('Training/validation performance should not be described as independent test accuracy.')
elif page == 'Scan History':
    st.markdown('<div class="section-kicker">RECENT ACTIVITY</div>',unsafe_allow_html=True)
    st.header('🕒 Scan history')
    st.caption('Stored locally on this computer; image files are not saved.')
    items = read_history()
    if items:
        st.dataframe(pd.DataFrame([{'Date':x['timestamp'],'Prediction':x['disease'],'Confidence (%)':x['confidence']} for x in items]), hide_index=True, use_container_width=True)
        st.download_button('Download history (JSON)', json.dumps(items,indent=2), file_name='agrovision_history.json')
    else:
        st.info('No scans saved yet. Analyse a leaf to get started.')
else:
    st.header('About AgroVision · LeafLens AI')
    st.write('AgroVision is an educational prototype for tomato leaf image classification using PyTorch and MobileNetV2.')
    st.write('It currently recognizes 10 classes from its training setup. It is not a validated field diagnostic tool and should not be used alone to make crop-treatment decisions.')
