import streamlit as st
from openai import OpenAI
import base64
import time
import random
import os
from openai import OpenAI

# ==========================================
# 1. PAGE CONFIG & CUSTOM CSS
# ==========================================
# This must be the very first Streamlit command
st.set_page_config(page_title="AI Homework Assistant", layout="wide", page_icon="📚")

# Inject Custom CSS for dynamic, colorful, and large UI
custom_css = """
<style>
    /* Global Background & Text Size */
    .stApp {
        background: linear-gradient(135deg, #fdfbfb 0%, #ebedee 100%);
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    p, span, div, label { font-size: 18px !important; }

    /* Headers */
    h1 {
        color: #2c3e50;
        font-size: 3.5rem !important;
        text-align: center;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        padding-bottom: 20px;
    }
    h2, h3 { color: #34495e; font-size: 2.5rem !important; }

    /* Buttons */
    .stButton>button {
        background: linear-gradient(90deg, #4b6cb7 0%, #182848 100%);
        color: white;
        border-radius: 12px;
        border: none;
        padding: 15px 30px;
        font-size: 22px !important;
        font-weight: bold;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px 0 rgba(75, 108, 183, 0.5);
        width: 100%;
    }
    .stButton>button:hover {
        transform: translateY(-3px) scale(1.02);
        box-shadow: 0 8px 25px 0 rgba(75, 108, 183, 0.8);
        color: #f1f1f1;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] { gap: 15px; justify-content: center; }
    .stTabs [data-baseweb="tab"] {
        font-size: 24px !important;
        font-weight: 600;
        padding: 15px 30px;
        background-color: white;
        border-radius: 15px 15px 0 0;
        box-shadow: 0 -4px 15px rgba(0,0,0,0.05);
        color: #7f8c8d;
    }
    .stTabs [aria-selected="true"] {
        color: #4b6cb7 !important;
        border-bottom: 4px solid #4b6cb7;
        background-color: #fdfbfb;
    }

    /* Inputs */
    .stTextArea textarea, .stTextInput input {
        font-size: 20px !important;
        border-radius: 12px;
        border: 2px solid #bdc3c7;
        padding: 15px;
        transition: border-color 0.3s ease;
    }
    .stTextArea textarea:focus, .stTextInput input:focus {
        border-color: #4b6cb7;
        box-shadow: 0 0 10px rgba(75, 108, 183, 0.2);
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] { font-size: 3rem !important; color: #27ae60; }
    [data-testid="stMetricLabel"] { font-size: 1.2rem !important; font-weight: bold; }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ==========================================
# 2. INITIALIZATION & API FUNCTIONS
# ==========================================
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)
                
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = [
        {"role": "system", "content": "You are an expert, patient AI tutor. Provide clear, step-by-step solutions. If the user asks a follow-up question, explain the concepts thoroughly."}
    ]

def encode_image(uploaded_file):
    """Encodes the uploaded image to base64"""
    return base64.b64encode(uploaded_file.getvalue()).decode('utf-8')

def get_ai_solution(system_prompt, user_prompt="Please solve this.", image_bytes=None):
    """Sends text and/or an image to OpenAI's model for single queries (Tab 2)"""
    user_content = [{"type": "text", "text": user_prompt}]
    
    if image_bytes is not None:
        base64_image = encode_image(image_bytes)
        user_content.append({
            "type": "image_url", 
            "image_url": {"url": f"data:image/jpeg;base64,{base64_image}", "detail": "high"}
        })
        
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            max_tokens=1000,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"An error occurred: {e}"

def send_chat_history_to_ai(messages):
    """Sends the entire conversation history to OpenAI (Tab 1)"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            max_tokens=1500,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"An error occurred: {e}"

# ==========================================
# 3. WEB APP UI
# ==========================================
st.title("📚 AI Homework & Abacus Platform")

tab1, tab2 = st.tabs(["💬 General Homework Chat", "🧮 Abacus Tools"])

# ------------------------------------------
# TAB 1: GENERAL HOMEWORK (CHAT MODE)
# ------------------------------------------
with tab1:
    # PHASE 1: INITIAL UPLOAD
    if len(st.session_state.chat_messages) == 1:
        st.markdown("### Upload a problem or type your question below to start.")
        
        col1, col2 = st.columns(2)
        with col1:
            first_q = st.text_area("Type your question:", placeholder="E.g., How do I solve this?")
        with col2:
            hw_image = st.file_uploader("Upload a photo of your question (Optional)", type=["jpg", "jpeg", "png"], key="hw_start")
        
        if st.button("Start Tutoring", type="primary"):
            if first_q.strip() == "" and hw_image is None:
                st.warning("Please upload an image or type a question!")
            else:
                first_message_content = []
                text_to_send = first_q if first_q.strip() != "" else "Please solve the problem in the attached image."
                first_message_content.append({"type": "text", "text": text_to_send})
                
                if hw_image is not None:
                    base64_image = encode_image(hw_image)
                    first_message_content.append({
                        "type": "image_url", 
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}", "detail": "high"}
                    })
                
                st.session_state.chat_messages.append({"role": "user", "content": first_message_content})
                st.rerun()

    # PHASE 2: ACTIVE CHAT INTERFACE
    else:
        # Display history
        for msg in st.session_state.chat_messages:
            if msg["role"] == "system": continue
                
            with st.chat_message(msg["role"]):
                if isinstance(msg["content"], list):
                    for item in msg["content"]:
                        if item["type"] == "text": st.write(item["text"])
                        elif item["type"] == "image_url": st.caption("📎 *Image Uploaded*")
                else:
                    st.write(msg["content"])

        # AI Response Trigger
        if st.session_state.chat_messages[-1]["role"] == "user":
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    ai_response = send_chat_history_to_ai(st.session_state.chat_messages)
                    st.write(ai_response)
                    st.session_state.chat_messages.append({"role": "assistant", "content": ai_response})
                    st.rerun()

        # Follow-up Input
        if follow_up := st.chat_input("Ask a follow-up question..."):
            st.session_state.chat_messages.append({"role": "user", "content": follow_up})
            st.rerun()
            
        st.divider()
        if st.button("Clear Chat & Start New Problem"):
            st.session_state.chat_messages = [st.session_state.chat_messages[0]]
            st.rerun()

# ------------------------------------------
# TAB 2: ABACUS TOOLS
# ------------------------------------------
with tab2:
    abacus_tool = st.radio("Select a tool:", ["Image Solver", "MCQ Quiz"], horizontal=True)
    st.divider()

    # --- Tool A: Image Solver ---
    if abacus_tool == "Image Solver":
        st.subheader("Abacus Image Solver")
        st.markdown("Upload a photo of an abacus. The AI will read the bead positions and calculate the value.")
        abacus_image = st.file_uploader("Upload abacus photo", type=["jpg", "jpeg", "png"], key="abacus")
        
        if abacus_image is not None:
            col1, col2 = st.columns([1, 2])
            with col1:
                st.image(abacus_image, caption="Uploaded Abacus", use_container_width=True)
            
            with col2:
                if st.button("Calculate Value", key="btn_abacus", type="primary"):
                    with st.spinner("Reading bead positions..."):
                        system_prompt = """
                        You are an expert at reading a standard Soroban (Japanese Abacus). 
                        Look closely at the image provided. 
                        1. Identify the active beads.
                        2. Remember that upper deck beads are worth 5, and lower deck beads are worth 1.
                        3. Break down the value column by column from left to right.
                        4. Output the final total number represented on the abacus.
                        """
                        answer = get_ai_solution(system_prompt=system_prompt, user_prompt="What number is shown on this abacus?", image_bytes=abacus_image)
                        st.success("Analysis Complete")
                        st.write(answer)

    # --- Tool B: Interactive MCQ Quiz ---
    elif abacus_tool == "MCQ Quiz":
        st.subheader("⏱️ Abacus MCQ Quiz")

        if 'quiz_status' not in st.session_state:
            st.session_state.quiz_status = 'setup'
        if 'quiz_data' not in st.session_state:
            st.session_state.quiz_data = []
        if 'start_time' not in st.session_state:
            st.session_state.start_time = 0

        # SETUP PHASE
        if st.session_state.quiz_status == 'setup':
            col1, col2 = st.columns(2)
            with col1:
                topic = st.selectbox("Select Topic", [
                    "Basic Addition & Subtraction (1-Digit)", 
                    "Addition & Subtraction (2-Digit)", 
                    "Multiplication (1-Digit x 2-Digit)"
                ])
            with col2:
                num_q = st.number_input("Number of Questions", min_value=1, max_value=20, value=5)

            if st.button("Start Quiz", type="primary"):
                questions = []
                for _ in range(num_q):
                    if "1-Digit" in topic and "Addition" in topic:
                        a, b = random.randint(1, 9), random.randint(1, 9)
                        op = random.choice(['+', '-'])
                        if op == '-' and a < b: a, b = b, a
                        correct_ans = a + b if op == '+' else a - b
                        q_text = f"{a} {op} {b} = ?"
                    elif "2-Digit" in topic:
                        a, b = random.randint(10, 99), random.randint(10, 99)
                        op = random.choice(['+', '-'])
                        if op == '-' and a < b: a, b = b, a
                        correct_ans = a + b if op == '+' else a - b
                        q_text = f"{a} {op} {b} = ?"
                    elif "Multiplication" in topic:
                        a, b = random.randint(2, 9), random.randint(10, 99)
                        correct_ans = a * b
                        q_text = f"{a} x {b} = ?"

                    options = [correct_ans]
                    while len(options) < 4:
                        wrong_ans = correct_ans + random.choice([-10, -5, -1, 1, 5, 10])
                        if wrong_ans not in options and wrong_ans >= 0:
                            options.append(wrong_ans)
                    
                    random.shuffle(options)
                    questions.append({
                        "question": q_text, 
                        "options": options, 
                        "answer": correct_ans,
                        "user_choice": None
                    })

                st.session_state.quiz_data = questions
                st.session_state.start_time = time.time()
                st.session_state.quiz_status = 'running'
                st.rerun()

        # RUNNING PHASE
        elif st.session_state.quiz_status == 'running':
            st.info("⏱️ Quiz in progress... Answer all questions and hit Submit at the bottom.")
            
            with st.form("quiz_form"):
                for i, q in enumerate(st.session_state.quiz_data):
                    st.markdown(f"**Q{i+1}: {q['question']}**")
                    st.radio("Select answer:", q['options'], key=f"q_ans_{i}", index=None)
                    st.divider()

                submitted = st.form_submit_button("Submit Quiz")
                
                if submitted:
                    for i in range(len(st.session_state.quiz_data)):
                        st.session_state.quiz_data[i]['user_choice'] = st.session_state[f"q_ans_{i}"]
                        
                    st.session_state.end_time = time.time()
                    st.session_state.quiz_status = 'completed'
                    st.rerun()

        # EVALUATION PHASE
        elif st.session_state.quiz_status == 'completed':
            st.subheader("📊 Evaluation Results")
            
            time_taken = round(st.session_state.end_time - st.session_state.start_time, 1)
            score = sum(1 for q in st.session_state.quiz_data if q['user_choice'] == q['answer'])
            total = len(st.session_state.quiz_data)
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Marks Obtained", f"{score} / {total}")
            col2.metric("Accuracy", f"{int((score/total)*100)}%")
            col3.metric("Time Taken", f"{time_taken} seconds")
            
            st.divider()
            
            for i, q in enumerate(st.session_state.quiz_data):
                user_ans = q['user_choice']
                if user_ans == q['answer']:
                    st.success(f"**Q{i+1}: {q['question']}** | You chose: {user_ans} ✅")
                else:
                    ans_display = user_ans if user_ans is not None else "Skipped"
                    st.error(f"**Q{i+1}: {q['question']}** | You chose: {ans_display} ❌ | Correct Answer: {q['answer']}")

            if st.button("Take Another Quiz", type="primary"):
                st.session_state.quiz_status = 'setup'
                st.rerun()