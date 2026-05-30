# app.py (Complete Code with Corrected Theme)

import gradio as gr
from transformers import pipeline
import torch
import os
import json
import logging # Added for better logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

print("--- Initializing Intent Detection App ---")

# --- 1. Define File Paths (Relative to app.py in 'Harmful Language Detection' folder) ---
MODEL_PATH = "./model/" # Points to the 'model' subfolder within the current directory
LABEL_MAP_PATH = "./intent_label_mapping_combined.json" # Points to the JSON file in the current directory

logging.info(f"Model path set to: {MODEL_PATH}")
logging.info(f"Label map path set to: {LABEL_MAP_PATH}")

# --- 2. Load the Model Pipeline ---
classifier_pipeline = None
id2label = None
label_names_ordered = [] # Initialize ordered list

logging.info(f"Attempting to load model from: {MODEL_PATH}")
try:
    # --- Basic File Checks ---
    if not os.path.isdir(MODEL_PATH):
        raise FileNotFoundError(f"Model directory not found: {MODEL_PATH}")
    config_path = os.path.join(MODEL_PATH, "config.json")
    # Check for either .safetensors or .bin weights file
    weights_path_options = [
        os.path.join(MODEL_PATH, "model.safetensors"),
        os.path.join(MODEL_PATH, "pytorch_model.bin")
    ]
    tokenizer_config_path = os.path.join(MODEL_PATH, "tokenizer_config.json")

    if not os.path.exists(config_path):
        raise FileNotFoundError(f"config.json not found in model directory: {MODEL_PATH}")
    if not any(os.path.exists(p) for p in weights_path_options):
         # Find which one might exist if error occurs
         found_weights = [p for p in weights_path_options if os.path.exists(p)]
         raise FileNotFoundError(f"Model weights (model.safetensors or pytorch_model.bin) not found in {MODEL_PATH}. Found: {found_weights if found_weights else 'None'}")
    if not os.path.exists(tokenizer_config_path):
         raise FileNotFoundError(f"Tokenizer config (tokenizer_config.json) not found in model directory: {MODEL_PATH}")

    logging.info("✅ Found config, weights, and tokenizer files.")

    # --- Determine Device ---
    device_num = 0 if torch.cuda.is_available() else -1
    device_name = "GPU" if device_num == 0 else "CPU"
    logging.info(f"CUDA available: {torch.cuda.is_available()}. Loading model onto {device_name}.")

    # --- Load Pipeline ---
    classifier_pipeline = pipeline(
        "text-classification",
        model=MODEL_PATH,
        tokenizer=MODEL_PATH, # Load tokenizer from the same path
        device=device_num,
        top_k=None # Get scores for all classes
    )
    logging.info("✅ Model pipeline loaded successfully!")

    # --- 3. Load id2label mapping ---
    try:
        id2label = classifier_pipeline.model.config.id2label
        id2label = {int(k): v for k, v in id2label.items()} # Ensure keys are integers
        logging.info("Loaded id2label from model config.")
        label_names_ordered = [id2label[i] for i in sorted(id2label.keys())]
        logging.info(f"Using labels (in order): {label_names_ordered}")
    except (AttributeError, KeyError, TypeError) as e:
        logging.warning(f"Could not get valid id2label from model config ({e}), loading from JSON file...")
        if os.path.exists(LABEL_MAP_PATH):
            try:
                with open(LABEL_MAP_PATH, 'r') as f:
                    label_maps = json.load(f)
                    id2label = {int(k): v for k, v in label_maps.get('id2label', {}).items()}
                if not id2label:
                    logging.error(f"Error: 'id2label' map not found or empty in {LABEL_MAP_PATH}")
                    id2label = None
                else:
                    logging.info("Loaded id2label from JSON file.")
                    label_names_ordered = [id2label[i] for i in sorted(id2label.keys())] # Define order here too
                    logging.info(f"Using labels (in order): {label_names_ordered}")
            except Exception as json_e:
                 logging.error(f"Error reading label map JSON file ({LABEL_MAP_PATH}): {json_e}")
                 id2label = None
        else:
            logging.error(f"Error: Label map file not found at {LABEL_MAP_PATH}")
            id2label = None

    if id2label is None:
        logging.error("❌ Critical: Could not load id2label mapping.")

except Exception as e:
    logging.error(f"❌ Error loading model pipeline or label map: {e}", exc_info=True)

# --- 4. Define Enhanced Prediction Function ---
def predict_intent_enhanced(text_input):
    """Classifies intent and returns formatted output for Blocks UI."""
    # Check if essential components are loaded
    if classifier_pipeline is None or id2label is None:
        logging.error("Prediction function called but pipeline or id2label not loaded.")
        # Ensure label_names_ordered exists even if empty for the return structure
        labels_to_show = label_names_ordered if 'label_names_ordered' in globals() and label_names_ordered else ["Error"]
        return "Error: Model not loaded.", {label: 0.0 for label in labels_to_show}, "Error"

    # Ensure consistent label names are available for returning scores
    labels_to_show = label_names_ordered

    if not isinstance(text_input, str) or not text_input.strip():
        logging.warning("Empty input received.")
        return "Please enter some text.", {label: 0.0 for label in labels_to_show}, "Neutral" # Default style

    logging.info(f"Received input: '{text_input[:100]}...'") # Log truncated input
    try:
        # Get scores for all classes
        raw_results = classifier_pipeline(text_input)[0] # pipeline returns all scores in a list inside a list
        logging.info(f"Pipeline results: {raw_results}")

        if not isinstance(raw_results, list): # Check if the result is a list of dicts
            raise ValueError("Expected list of scores from pipeline.")

        all_scores = raw_results
        confidences = {label: 0.0 for label in labels_to_show} # Initialize
        top_label = "Unknown"
        top_score = 0.0

        for item in all_scores:
            item_label_name_raw = item['label']
            item_score = item['score']

            # Convert raw label (like LABEL_1) to text label using id2label map
            if item_label_name_raw.startswith("LABEL_"):
                try:
                    item_label_id = int(item_label_name_raw.split("_")[1])
                    item_text_label = id2label.get(item_label_id, "Unknown")
                except (IndexError, ValueError):
                    item_text_label = "Unknown" # Handle malformed label
            else:
                # If the label is already text, use it directly (check if it's valid)
                item_text_label = item_label_name_raw if item_label_name_raw in labels_to_show else "Unknown"

            # Store confidence if label is known and valid
            if item_text_label != "Unknown":
                confidences[item_text_label] = float(item_score) # Ensure score is float
                # Track the top prediction based on score
                if item_score > top_score:
                    top_score = item_score
                    top_label = item_text_label

        result_text = f"Predicted Intent: **{top_label}** (Score: {top_score:.2f})"

        # --- Define Output Style/Color based on prediction ---
        if top_label in ['threatening_action', 'planning_crime']:
            style = "Error"
        elif top_label in ['confession', 'discussing_illegal_activity']:
            style = "Warning"
        else: # neutral or Unknown
            style = "Success" # Use success for neutral, could use default for Unknown

        return result_text, confidences, style # Return text, scores dict, and style string

    except Exception as e:
        logging.error(f"Error during prediction pipeline call: {e}", exc_info=True)
        return f"Error predicting: {e}", {label: 0.0 for label in labels_to_show}, "Error"


# --- 5. Create and Launch the Gradio Blocks Interface ---
if classifier_pipeline is not None and id2label is not None:
    logging.info("--- Creating Gradio Interface ---")

    # Define the theme with the corrected color name
    theme = gr.themes.Soft(primary_hue="blue", secondary_hue="sky") # Corrected color

    with gr.Blocks(theme=theme) as demo:
        gr.Markdown(
            """
            # 🕵️ Harmful Language & Criminal Intent Detector
            Enter a sentence or dialogue snippet below to classify its intent using a fine-tuned DistilBERT model.
            Categories: **neutral, confession, planning_crime, threatening_action, discussing_illegal_activity**.
            """
        )
        with gr.Row():
            with gr.Column(scale=2):
                text_input = gr.Textbox(
                    lines=5,
                    placeholder="Type or paste dialogue here...",
                    label="Input Dialogue"
                )
                submit_button = gr.Button("Analyze Intent", variant="primary")
            with gr.Column(scale=1):
                # Use Textbox for main result (easier to potentially style later if needed)
                result_output = gr.Textbox(label="Result", interactive=False)
                # Use Label for confidence scores display
                confidence_output = gr.Label(label="Confidence Scores", num_top_classes=len(label_names_ordered)) # Use ordered names

        gr.Examples(
            examples=[
                ["I admit, I took the files from his desk."],
                ["Meet me by the docks at 2 AM, bring the tools."],
                ["If he talks, make sure he doesn't talk again."],
                ["Just reviewing the quarterly sales figures."],
                ["They discussed the heist they pulled off last summer."],
                ["You better keep your mouth shut, or else."],
                ["Leave the package by the third dumpster behind the diner at 9 PM."],
            ],
            inputs=text_input
        )

        # Define interactions - Simplified click without dynamic styling for reliability
        submit_button.click(
            fn=predict_intent_enhanced,
            inputs=text_input,
            outputs=[result_output, confidence_output] # Output text and scores dict
            # The third output 'style' is ignored here for simplicity
        )

    logging.info("--- Launching Gradio Interface ---")
    logging.info("Interface will be available at a local URL (e.g., http://127.0.0.1:7860)")
    # share=False keeps it local, share=True creates a temporary public link
    demo.launch(share=False)

else:
    logging.error("--- Interface Launch Failed ---")
    logging.error("Could not launch Gradio interface. Check model/label map loading errors above.")