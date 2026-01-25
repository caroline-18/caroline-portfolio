# Graph Neural Networks for Context-Aware Contract Risk Identification

## Overview
Legal contracts contain complex relationships between clauses, entities, and obligations that traditional text-based models often fail to capture. This project leverages **Graph Neural Networks (GNNs)** to model contracts as structured graphs, enabling context-aware identification of contractual risk.

The approach focuses on representing semantic and relational dependencies between clauses to improve risk detection accuracy and interpretability.

---

## Problem Statement
Traditional NLP models treat contracts as flat text, ignoring structural dependencies such as cross-referenced clauses and entity relationships. This limitation reduces effectiveness in identifying high-risk contractual terms.

**Objective:**  
To design a graph-based learning framework that captures contextual dependencies within contracts and accurately identifies risk-prone clauses.

---

## Methodology
- Preprocessed legal contract documents and extracted clauses, entities, and references.
- Modeled contracts as graphs where nodes represent clauses/entities and edges encode semantic or logical relationships.
- Implemented Graph Neural Network architectures to learn contextual embeddings for risk classification.
- Evaluated model performance on labeled contract data and analyzed predictions using explainability techniques.

---

## Tools & Technologies
- **Programming Language:** Python  
- **Libraries & Frameworks:** PyTorch, NetworkX, NumPy, Pandas  
- **Techniques:** Graph Neural Networks, NLP, Feature Engineering, Explainable AI  

---

## Results
- Successfully captured inter-clause dependencies that are missed by sequence-based models.
- Improved contextual understanding of contract risk compared to baseline text-only approaches.
- Generated interpretable insights highlighting clauses contributing most to contractual risk.

---

## Repository Structure
gnn-contract-risk-identification/
├── README.md
├── data/ # Contract datasets (or dataset links)
├── src/ # Graph construction and model code
├── experiments/ # Training and evaluation scripts
└── results/ # Outputs, metrics, and visualizations
