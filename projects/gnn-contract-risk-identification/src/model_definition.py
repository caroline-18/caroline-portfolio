# src/model_definition.py

import torch
import torch.nn.functional as F
from torch_geometric.nn import GATConv

class GATModel(torch.nn.Module):
    """
    This is our Graph Attention Network (GNN).
    
    It has two layers. It takes in node features (our 384-dim embeddings)
    and outputs a risk score for each class (Low, Medium, High).
    """
    
    def __init__(self, in_features, hidden_features, num_classes, heads=4):
        """
        Define the layers of the model.
        
        in_features: Size of our input embeddings (384)
        hidden_features: Size of the intermediate layer (e.g., 64)
        num_classes: Number of output classes (e.g., 3 for Low/Medium/High)
        heads: Number of "attention heads" (a GAT-specific parameter)
        """
        super(GATModel, self).__init__()
        
        # We use a dropout layer to prevent overfitting (a good practice)
        self.dropout_rate = 0.6
        
        # --- Layer 1 ---
        # Takes 384-dim embeddings -> [heads * hidden_features]
        self.conv1 = GATConv(
            in_features, 
            hidden_features, 
            heads=heads, 
            dropout=self.dropout_rate
        )
        
        # --- Layer 2 ---
        # This is the final layer that gives us the class scores.
        # It takes [heads * hidden_features] -> num_classes
        self.conv2 = GATConv(
            hidden_features * heads, # Input is the concatenated output of all heads
            num_classes, 
            heads=1,           # Final layer usually has 1 head
            concat=False,      # We want a single output vector, not concatenated
            dropout=self.dropout_rate
        )

    def forward(self, data):
        """
        This defines the "forward pass" - how data flows through the model.
        
        'data' will be a PyTorch Geometric object containing:
         - data.x: Our node features (embeddings)
         - data.edge_index: Our graph connections (edges)
        """
        x, edge_index = data.x, data.edge_index
        
        # Apply dropout to the input features
        x = F.dropout(x, p=self.dropout_rate, training=self.training)
        
        # Pass data through the first layer
        x = self.conv1(x, edge_index)
        
        # Apply an activation function (ELU is common with GAT)
        x = F.elu(x)
        
        # Apply dropout to the hidden layer
        x = F.dropout(x, p=self.dropout_rate, training=self.training)
        
        # Pass data through the final layer
        x = self.conv2(x, edge_index)
        
        # Return the final predictions (as log probabilities)
        return F.log_softmax(x, dim=1)