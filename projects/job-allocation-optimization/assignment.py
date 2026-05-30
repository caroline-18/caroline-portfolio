import streamlit as st
import numpy as np
import pandas as pd
from scipy.optimize import linear_sum_assignment
from pulp import LpMaximize, LpProblem, LpVariable, lpSum

# ------------------ FUNCTION DEFINITIONS ------------------

# Function for Hungarian Method (Maximization)
def hungarian_method_maximization(profit_matrix):
    row_ind, col_ind = linear_sum_assignment(profit_matrix, maximize=True)
    total_profit = profit_matrix[row_ind, col_ind].sum()
    return total_profit, row_ind, col_ind

# Function for Hungarian Method (Minimization)
def hungarian_method_minimization(profit_matrix):
    max_profit = profit_matrix.max()
    cost_matrix = max_profit - profit_matrix
    row_ind, col_ind = linear_sum_assignment(cost_matrix)
    total_profit = profit_matrix[row_ind, col_ind].sum()
    return total_profit, row_ind, col_ind

# Function for ILP (Maximization)
def ilp_maximization(profit_matrix):
    num_workers, num_jobs = profit_matrix.shape
    prob = LpProblem("Job_Assignment_Maximization", LpMaximize)
    x = [[LpVariable(f"x_{i}_{j}", cat="Binary") for j in range(num_jobs)] for i in range(num_workers)]
    prob += lpSum(profit_matrix[i][j] * x[i][j] for i in range(num_workers) for j in range(num_jobs))
    
    for i in range(num_workers):
        prob += lpSum(x[i][j] for j in range(num_jobs)) == 1
    
    for j in range(num_jobs):
        prob += lpSum(x[i][j] for i in range(num_workers)) == 1
    
    prob.solve()
    total_profit = prob.objective.value()
    return total_profit, prob

# Function for ILP (Minimization)
def ilp_minimization(profit_matrix):
    num_workers, num_jobs = profit_matrix.shape
    prob = LpProblem("Job_Assignment_Minimization", LpMaximize)
    max_profit = profit_matrix.max()
    cost_matrix = max_profit - profit_matrix
    x = [[LpVariable(f"x_{i}_{j}", cat="Binary") for j in range(num_jobs)] for i in range(num_workers)]
    prob += lpSum(cost_matrix[i][j] * x[i][j] for i in range(num_workers) for j in range(num_jobs))
    
    for i in range(num_workers):
        prob += lpSum(x[i][j] for j in range(num_jobs)) == 1
    
    for j in range(num_jobs):
        prob += lpSum(x[i][j] for i in range(num_workers)) == 1
    
    prob.solve()
    total_cost = prob.objective.value()
    return total_cost, prob

# ------------------ STREAMLIT UI ------------------

st.title("Job Assignment Optimization")
st.write("Solve the Job Assignment Problem using Hungarian Method and ILP (Maximization and Minimization)")

# Select input method (Upload CSV or Manual Input)
input_method = st.radio("Choose Input Method", ("Upload CSV", "Manual Input"))

# Initialize profit_matrix
profit_matrix = None

if input_method == "Upload CSV":
    uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file, index_col=0)
        profit_matrix = df.values
        st.write(f"Profit Matrix:\n", df)

elif input_method == "Manual Input":
    n = st.number_input("Enter the size of the matrix (n x n)", min_value=2, step=1)

    matrix_values = []
    for i in range(n):
        row = st.text_input(f"Enter values for row {i + 1} (comma separated)", "")
        row_values = [int(x) for x in row.split(",") if x.strip() != ""]
        if len(row_values) == n:
            matrix_values.append(row_values)

    if len(matrix_values) == n:
        profit_matrix = np.array(matrix_values)
        st.write("Profit Matrix:", pd.DataFrame(profit_matrix))
    else:
        st.warning("Please make sure all rows have exactly n values.")

# Ensure profit_matrix is defined before using it
if profit_matrix is not None:
    optimization_type = st.selectbox("Choose Optimization Type", ["Maximization", "Minimization"])
    method_type = st.selectbox("Choose Method", ["Hungarian Method", "ILP Method"])

    if optimization_type == "Maximization":
        if method_type == "Hungarian Method":
            total_profit, row_ind, col_ind = hungarian_method_maximization(profit_matrix)
            st.write(f"Maximization using Hungarian Method - Total Profit: {total_profit}")
            st.write(f"Optimal Assignments: {list(zip(row_ind, col_ind))}")

        elif method_type == "ILP Method":
            total_profit, prob = ilp_maximization(profit_matrix)
            st.write(f"Maximization using ILP Method - Total Profit: {total_profit}")

    elif optimization_type == "Minimization":
        if method_type == "Hungarian Method":
            total_profit, row_ind, col_ind = hungarian_method_minimization(profit_matrix)
            st.write(f"Minimization using Hungarian Method - Total Profit: {total_profit}")
            st.write(f"Optimal Assignments: {list(zip(row_ind, col_ind))}")

        elif method_type == "ILP Method":
            total_cost, prob = ilp_minimization(profit_matrix)
            st.write(f"Minimization using ILP Method - Total Cost: {total_cost}")

else:
    st.warning("Please upload a CSV file or manually enter a valid profit matrix before proceeding.")