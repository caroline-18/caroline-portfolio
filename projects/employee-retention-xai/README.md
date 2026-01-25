# Data-Driven Employee Retention: A Machine Learning Approach

## Overview
Employee attrition poses a significant challenge for organizations, leading to increased recruitment costs, loss of expertise, and reduced workforce stability. Accurately predicting employee turnover and understanding the factors influencing retention are essential for effective human resource planning.

This project applies **machine learning techniques** to predict employee attrition using structured HR data. The focus is on building reliable predictive models and extracting **interpretable insights** that can support data-driven decision-making in human resource management.

---

## Problem Statement
Employee attrition is influenced by multiple factors such as job role, compensation, workload, and career progression. Traditional analytical approaches often fail to capture complex relationships among these factors.

**Objective:**  
To develop a machine learning framework that:
- Predicts employee attrition with high reliability  
- Identifies key factors influencing employee turnover  
- Provides interpretable insights to support HR policy design  

---

## Methodology
- Collected and preprocessed structured HR data containing demographic, performance, and compensation-related attributes.
- Performed data cleaning, feature selection, and normalization.
- Trained and evaluated multiple machine learning models, with a focus on **Random Forest** due to its robustness and interpretability.
- Addressed class imbalance to improve prediction reliability.
- Analyzed feature importance from tree-based models to understand drivers of employee attrition.

---

## Model Interpretability
Interpretability was achieved using **feature importance analysis** from the trained Random Forest model.  
This approach highlights the relative contribution of each employee attribute to attrition predictions, enabling transparent and actionable interpretation of model behavior.

---

## Tools & Technologies
- **Programming Language:** Python  
- **Libraries & Frameworks:**  
  - Scikit-learn  
  - Pandas  
  - NumPy  
  - Matplotlib  
- **Techniques:**  
  - Supervised Machine Learning  
  - Feature Engineering  
  - Class Imbalance Handling  
  - Model Interpretation  

---

## Results
- Achieved reliable employee attrition prediction performance using ensemble-based models.
- Identified key retention drivers such as:
  - Job role and workload  
  - Compensation and incentives  
  - Career growth indicators  
- Generated interpretable insights suitable for strategic HR decision-making.

## Project Structure
employee-retention-xai
│ README.md
│
├───data
│ Employee.csv
│
├───models
│ best_random_forest.pkl
│ scaler.pkl
│
├───notebooks
│ Retention.ipynb
│
├───results
│ prediction_result.pdf
│ figures
│
└───src
workplace.py


---

## Skills Demonstrated
- Predictive Modeling for HR Analytics  
- Feature Importance Analysis  
- Applied Machine Learning  
- Research-Oriented Data Analysis  

---

## Notes
This project is intended for academic and analytical demonstration purposes.  
The dataset used is for educational use only.

