# Graph Neural Networks for Context-Aware Contract Risk Identification

## Overview
Contract analysis is a critical task in legal and business domains, where identifying risky clauses is essential for mitigating financial, legal, and compliance risks. Traditional text-based approaches often process clauses independently and fail to capture the contextual dependencies that exist across contract documents.

This project introduces a **graph-based learning framework** that represents contracts as structured graphs and applies **Graph Neural Networks (GNNs)** to perform context-aware contractual risk identification.

---

## Problem Statement
Contractual risk frequently arises from interactions between multiple clauses rather than isolated statements. Dependencies between clauses such as termination conditions, liability limitations, and indemnity provisions are often distributed across different sections of a contract.

**Objective:**  
To develop a graph-based machine learning approach that captures inter-clause relationships and accurately identifies high-risk contractual components.

---

## Methodology
- Modeled contracts as graphs where nodes represent individual clauses and edges encode structural and semantic relationships.  
- Generated clause-level feature representations from textual content.  
- Applied Graph Neural Networks to learn context-aware embeddings for risk classification.  
- Evaluated model performance using standard classification metrics and qualitative analysis of predicted risk patterns.

---

## Tools & Technologies
- **Programming Language:** Python  
- **Libraries & Frameworks:** PyTorch, PyTorch Geometric, NetworkX  
- **Techniques:** Graph Neural Networks, Graph Representation Learning, NLP-based Feature Engineering  

---

## Results
- Demonstrated improved contract risk identification by incorporating clause-level contextual dependencies.  
- Showed the effectiveness of graph-based modeling compared to clause-independent text classification approaches.

---

## Skills Demonstrated
Graph Modeling • Graph Neural Networks • NLP + Graph Learning • Research-Oriented Machine Learning
