# src/generate_plots.py

import matplotlib.pyplot as plt 
import numpy as np
import torch
import os
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay, classification_report

# --- Helper Function to Ensure Plots Save/Load Correctly ---
def get_data_file_path(filename):
    """ Looks for data files inside the 'notebooks' folder """
    script_dir = os.path.dirname(__file__) # Directory of this script (src)
    project_root = os.path.dirname(script_dir) # Directory above src (Capstone)
    notebooks_dir = os.path.join(project_root, 'notebooks') # Path to notebooks folder
    return os.path.join(notebooks_dir, filename) # Path to file inside notebooks

def get_plot_save_path(filename):
    """ Ensures plots are saved in the main project directory """
    script_dir = os.path.dirname(__file__) # Directory of this script (src)
    project_root = os.path.dirname(script_dir) # Directory above src (Capstone)
    return os.path.join(project_root, filename) # Save plots in Capstone folder

# --- Graph 1: Class Distribution ---
def plot_class_distribution(train_labels_path='train_labels.pt', test_labels_path='test_labels.pt'):
    print("\nGenerating Class Distribution plot...")
    try:
        train_labels = torch.load(get_data_file_path(train_labels_path)) # <--- CHANGE HERE
        test_labels = torch.load(get_data_file_path(test_labels_path))  # <--- CHANGE HERE
    except FileNotFoundError:
        print(f"Error: Could not find label files ({train_labels_path} or {test_labels_path}). Run the notebook first.")
        return

    all_labels = np.concatenate([train_labels.numpy(), test_labels.numpy()])
    class_counts = np.bincount(all_labels)
    classes = ['Low Risk (0)', 'Medium Risk (1)', 'High Risk (2)']

    counts_for_plot = np.zeros(3)
    counts_for_plot[:len(class_counts)] = class_counts

    plt.figure(figsize=(8, 6))
    bars = plt.bar(classes, counts_for_plot, color=['green', 'orange', 'red'])
    plt.ylabel('Number of Nodes')
    plt.title('Class Distribution Across Entire Dataset')
    plt.yscale('log')
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2.0, yval, int(yval), va='bottom', ha='center')

    plt.tight_layout()
    save_path = get_plot_save_path('class_distribution.png')
    plt.savefig(save_path)
    plt.close() # Close the figure to free memory
    print(f"Saved: {save_path}")

# --- Graph 2: Training Loss Curve ---
def plot_loss_curve(losses_path='losses.pt'):
    print("\nGenerating Training Loss Curve plot...")
    try:
        losses = torch.load(get_data_file_path(losses_path))
    except FileNotFoundError:
        print(f"Error: Could not find loss file ({losses_path}). Run the notebook first.")
        return

    epochs = range(0, len(losses) * 5, 5) # Assuming loss recorded every 5 epochs

    plt.figure(figsize=(10, 6))
    plt.plot(epochs[:len(losses)], losses, marker='o', linestyle='-', color='b') # Ensure epochs match losses length
    plt.xlabel('Epoch')
    plt.ylabel('Loss (Negative Log Likelihood)')
    plt.title('GNN Training Loss Over Epochs')
    plt.grid(True)
    plt.tight_layout()
    save_path = get_plot_save_path('training_loss_curve.png')
    plt.savefig(save_path)
    plt.close()
    print(f"Saved: {save_path}")

# --- Graph 3: Confusion Matrix ---
def plot_confusion_matrix(test_labels_path='test_labels.pt', test_preds_path='test_predictions.pt'):
    print("\nGenerating Confusion Matrix plot...")
    try:
        true_labels_tensor = torch.load(get_data_file_path(test_labels_path))      # <--- CHANGE HERE
        predicted_labels_tensor = torch.load(get_data_file_path(test_preds_path)) # <--- CHANGE HERE
    except FileNotFoundError:
        print(f"Error: Could not find test label/prediction files. Run the notebook first.")
        return

    true_labels = true_labels_tensor.numpy()
    predicted_labels = predicted_labels_tensor.numpy()
    classes = ['Low (0)', 'Medium (1)', 'High (2)']

    cm = confusion_matrix(true_labels, predicted_labels, labels=[0, 1, 2])
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=classes)

    fig, ax = plt.subplots(figsize=(8, 8))
    disp.plot(cmap=plt.cm.Blues, ax=ax, values_format='d')
    plt.title('Confusion Matrix on Unseen Test Data')
    plt.tight_layout()
    save_path = get_plot_save_path('confusion_matrix.png')
    plt.savefig(save_path)
    plt.close()
    print(f"Saved: {save_path}")

# --- Graph 4: Performance Metrics ---
def plot_performance_metrics(test_labels_path='test_labels.pt', test_preds_path='test_predictions.pt'):
    print("\nGenerating Performance Metrics plot...")
    try:
        true_labels_tensor = torch.load(get_data_file_path(test_labels_path))      # <--- CHANGE HERE
        predicted_labels_tensor = torch.load(get_data_file_path(test_preds_path)) # <--- CHANGE HERE
    except FileNotFoundError:
        print(f"Error: Could not find test label/prediction files. Run the notebook first.")
        return

    true_labels = true_labels_tensor.numpy()
    predicted_labels = predicted_labels_tensor.numpy()
    classes = ['Low (0)', 'Medium (1)', 'High (2)']

    report = classification_report(true_labels, predicted_labels, labels=[0, 1, 2], target_names=classes, output_dict=True, zero_division=0)

    metrics_to_plot = ['precision', 'recall', 'f1-score']
    class_1_scores = [report.get('Medium (1)', {}).get(m, 0) for m in metrics_to_plot] # Handle cases where a class might be missing
    class_2_scores = [report.get('High (2)', {}).get(m, 0) for m in metrics_to_plot]
    accuracy = report.get('accuracy', 0)

    x = np.arange(len(metrics_to_plot))
    width = 0.35

    fig, ax = plt.subplots(figsize=(10, 6))
    rects1 = ax.bar(x - width/2, class_1_scores, width, label='Medium Risk (Class 1)', color='orange')
    rects2 = ax.bar(x + width/2, class_2_scores, width, label='High Risk (Class 2)', color='red')

    ax.text(0.95, 0.95, f'Overall Accuracy: {accuracy:.2f}', transform=ax.transAxes,
            fontsize=12, verticalalignment='top', horizontalalignment='right',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    ax.set_ylabel('Score')
    ax.set_title('Performance Metrics on Test Set (Risky Classes)')
    ax.set_xticks(x)
    ax.set_xticklabels(metrics_to_plot)
    ax.legend()
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    ax.set_ylim(0, 1.05)

    def autolabel(rects):
        for rect in rects:
            height = rect.get_height()
            ax.annotate(f'{height:.2f}',
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3), textcoords="offset points",
                        ha='center', va='bottom')

    autolabel(rects1)
    autolabel(rects2)

    fig.tight_layout()
    save_path = get_plot_save_path('performance_metrics.png')
    plt.savefig(save_path)
    plt.close()
    print(f"Saved: {save_path}")

# --- Main Execution Block ---
if __name__ == "__main__":
    print("--- GENERATING ALL PLOTS ---")
    
    # Check if necessary libraries are installed
    try:
        import matplotlib
        import sklearn
    except ImportError:
        print("Error: Missing libraries. Please install matplotlib and scikit-learn:")
        print("pip install matplotlib scikit-learn")
    else:
        plot_class_distribution()
        plot_loss_curve()
        plot_confusion_matrix()
        plot_performance_metrics()
        print("\n--- Plot generation complete. Check your main project folder for .png files. ---")