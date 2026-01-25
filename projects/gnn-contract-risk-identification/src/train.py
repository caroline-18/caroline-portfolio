# src/train.py

import torch
import torch.optim as optim
import torch.nn.functional as F
import re
import os
import random
from torch_geometric.data import Batch

# Import all our custom modules
from data_processing import find_all_contract_paths, process_contract_pdf
from graph_construction import (
    generate_node_embeddings, 
    build_graph, 
    convert_nx_to_pyg_data
)
from model_definition import GATModel

# --- 1. DEFINE GROUND TRUTH "RISK LEXICON" ---
RISK_LEXICON = {
    # High Risk (Class 2)
    "uncapped liability": 2,
    "unlimited liability": 2,
    "indemnify": 2,
    "indemnification": 2,
    "liquidated damages": 2,
    "sole discretion": 2,
    
    # Medium Risk (Class 1)
    "penalty": 1,
    "terminate for convenience": 1,
    "non-solicitation": 1,
    "exclusivity": 1,
    "arbitration": 1,
    "governing law": 1,
    "best efforts": 1,
}

def create_labels(nodes_list):
    """
    Iterates through all nodes and assigns a risk label
    based on our RISK_LEXICON.
    """
    labels = []
    for node in nodes_list:
        node_label = 0 # Default: Low Risk
        node_text_lower = node['content'].lower()
        
        for keyword, risk_class in RISK_LEXICON.items():
            if re.search(r'\b' + re.escape(keyword) + r'\b', node_text_lower):
                node_label = max(node_label, risk_class) 
        
        labels.append(node_label)
        
    num_risky = sum(1 for l in labels if l > 0)
    print(f"Created {len(labels)} labels. Found {num_risky} risky nodes.")
    return torch.tensor(labels, dtype=torch.long), num_risky

# --- 2. [NEW FUNCTION] DEFINE THE EVALUATION SCRIPT ---

def evaluate_model(model, graph_data, data_name="Test Data"):
    """
    Takes a trained model and new graph data,
    and prints a performance report.
    """
    print(f"\n--- EVALUATING ON {data_name} ---")
    
    model.eval() # Set model to evaluation mode
    
    with torch.no_grad():
        final_predictions = model(graph_data)
        
    predicted_classes = final_predictions.argmax(dim=1)
    
    print(f"Node | Ground Truth Label | Model's Prediction")
    print("-" * 40)
    
    correct_count = 0
    total_risky_nodes_found = 0
    total_risky_nodes_missed = 0
    
    for i in range(len(graph_data.y)):
        truth = graph_data.y[i].item()
        pred = predicted_classes[i].item()
        
        if truth == pred:
            correct_count += 1
            
        if truth > 0: # If this is a real risky node
            if truth == pred:
                total_risky_nodes_found += 1
                print(f" {i:03d} |         {truth}          |         {pred}       [CORRECT]")
            else:
                total_risky_nodes_missed += 1
                print(f" {i:03d} |         {truth}          |         {pred}       [---MISSED---]")

    accuracy = correct_count / len(graph_data.y)
    
    print(f"\n--- {data_name} Report ---")
    print(f"Overall Accuracy: {accuracy * 100:.2f}%")
    print(f"Correctly Identified Risky Nodes: {total_risky_nodes_found}")
    print(f"Missed Risky Nodes: {total_risky_nodes_missed}")
    
    return accuracy

# --- 3. [UPGRADED FUNCTION] DEFINE THE TRAINING PIPELINE ---

def run_training_pipeline():
    """
    [UPGRADED] This version will find ALL contracts,
    create an 80/20 train/test split, and train the
    model on a "master batch" of all training graphs.
    """
    print("--- STARTING MASTER TRAINING PIPELINE ---")
    
    # --- 1. Find and Split All Data ---
    all_paths = find_all_contract_paths()
    if not all_paths:
        print("No contracts found. Exiting.")
        return

    print(f"Found {len(all_paths)} total contracts.")
    
    # Shuffle the data for a random train/test split
    random.seed(42) # Use a seed for reproducible results
    random.shuffle(all_paths)
    
    # Create an 80/20 split
    split_index = int(len(all_paths) * 0.8)
    train_paths = all_paths[:split_index]
    test_paths = all_paths[split_index:]

    print(f"Creating training set with {len(train_paths)} contracts.")
    print(f"Creating test set with {len(test_paths)} contracts.")

    # --- 2. Build Master Train Graph ---
    train_graph_list = []
    for path in train_paths:
        print(f"Processing (Train): {os.path.basename(path)}")
        nodes_list = process_contract_pdf(path)
        labels, num_risky = create_labels(nodes_list)
        nodes_with_embeddings = generate_node_embeddings(nodes_list)
        nx_graph = build_graph(nodes_with_embeddings)
        pyg_data = convert_nx_to_pyg_data(nx_graph, labels)
        train_graph_list.append(pyg_data)
        
    # Batch all training graphs into one giant graph
    train_data = Batch.from_data_list(train_graph_list)
    
    # --- 3. Build Master Test Graph ---
    test_graph_list = []
    for path in test_paths:
        print(f"Processing (Test): {os.path.basename(path)}")
        nodes_list = process_contract_pdf(path)
        labels, num_risky = create_labels(nodes_list)
        nodes_with_embeddings = generate_node_embeddings(nodes_list)
        nx_graph = build_graph(nodes_with_embeddings)
        pyg_data = convert_nx_to_pyg_data(nx_graph, labels)
        test_graph_list.append(pyg_data)
        
    # Batch all test graphs into one giant graph
    test_data = Batch.from_data_list(test_graph_list)

    # --- 4. Initialize Model & Training ---
    model = GATModel(in_features=384, hidden_features=64, num_classes=3)
    optimizer = optim.Adam(model.parameters(), lr=0.005, weight_decay=5e-4)
    
    # Calculate weights based on the ENTIRE training set
    class_counts = torch.bincount(train_data.y)
    full_class_counts = torch.zeros(3, dtype=torch.float)
    full_class_counts[:len(class_counts)] = class_counts.float()
    full_class_counts = full_class_counts + 1 
    weights = train_data.y.shape[0] / (3 * full_class_counts)
    
    print(f"\nTraining on {train_data.num_nodes} nodes across {len(train_paths)} contracts.")
    print(f"Training with Class Weights: {weights}")
    print("--- Starting Model Training ---")

    losses = []
    
    model.train() 
    for epoch in range(201): # You can increase this to 300 or 400
        optimizer.zero_grad()
        out = model(train_data)
        loss = F.nll_loss(out, train_data.y, weight=weights)
        loss.backward()
        optimizer.step()
        
        if epoch % 5 == 0:
            losses.append(loss.item()) 
            
        if epoch % 20 == 0:
            print(f"Epoch {epoch:03d} | Loss: {loss.item():.4f}")
            
    print("--- Training Complete ---")
    
    # --- 5. Evaluate the Trained Model ---
    # Evaluate on the data it trained on
    evaluate_model(model, train_data, "TRAIN DATA (MASTER BATCH)")
    
    # Evaluate on the unseen test data (the real test)
    # --- [NEW] Calculate final test predictions ONCE ---
    model.eval()
    with torch.no_grad():
        final_test_predictions_raw = model(test_data)
    final_test_predicted_classes = final_test_predictions_raw.argmax(dim=1)
    # --- End New ---

    # Now call evaluate_model (it will recalculate internally, which is fine)
    evaluate_model(model, test_data, "TEST DATA (UNSEEN BATCH)")

    # --- [CORRECTED] Return the predictions we just calculated ---
    return model, train_data, test_data, final_test_predicted_classes, losses