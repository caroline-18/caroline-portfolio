# src/02_graph_construction.py

import re
from torch_geometric.data import Data

import torch
from sentence_transformers import util

from sentence_transformers import SentenceTransformer
import networkx as nx
import numpy as np


# Load a small, fast, and effective model for embedding.
# This will download the model the first time you run it.
print("Loading embedding model (this may take a moment)...")
EMBEDDING_MODEL = SentenceTransformer('all-MiniLM-L6-v2')
print("Embedding model loaded.")

def generate_node_embeddings(nodes_list):
    """
    Takes the list of nodes from Stage 1 and adds a
    feature vector ('embedding') to each one.
    """

    # 1. Get a list of all the text content
    content_to_embed = [node['content'] for node in nodes_list]

    # 2. Embed all of them at once (this is very fast on a GPU)
    print(f"Generating {len(content_to_embed)} embeddings...")
    embeddings = EMBEDDING_MODEL.encode(content_to_embed, show_progress_bar=True)

    # 3. Add the embedding back into our node list
    for i, node in enumerate(nodes_list):
        node['embedding'] = embeddings[i]

    print("Embeddings generated.")
    return nodes_list

def build_graph(nodes_list_with_embeddings):
    """
    Takes the list of nodes (now with embeddings) and
    builds a NetworkX graph, adding STRUCTURAL, SEMANTIC,
    and [NEW] REFERENTIAL edges.
    """
    G = nx.Graph()
    
    # --- 1. Add all the nodes to the graph (Same as before) ---
    for i, node_data in enumerate(nodes_list_with_embeddings):
        G.add_node(
            i, 
            type=node_data['type'],
            content=node_data['content'],
            embedding=node_data['embedding']
        )
    
    # --- 2. Add STRUCTURAL edges (Same as before) ---
    for i in range(len(nodes_list_with_embeddings) - 1):
        G.add_edge(i, i + 1, type="STRUCTURAL")
    print(f"Added {G.number_of_edges()} STRUCTURAL edges.")
    
    # --- 3. Add SEMANTIC edges (Same as before) ---
    print("Calculating semantic similarities...")
    SIMILARITY_THRESHOLD = 0.8 
    
    embeddings = [node['embedding'] for node in nodes_list_with_embeddings]
    embeddings_array = np.array(embeddings)
    embeddings_tensor = torch.tensor(embeddings_array)
    
    cos_scores = util.cos_sim(embeddings_tensor, embeddings_tensor)
    semantic_edge_count = 0
    
    for i in range(len(cos_scores)):
        for j in range(i + 1, len(cos_scores)):
            score = cos_scores[i][j]
            if score > SIMILARITY_THRESHOLD:
                G.add_edge(
                    i, 
                    j, 
                    type="SEMANTIC", 
                    score=float(score)
                )
                semantic_edge_count += 1
                
    print(f"Added {semantic_edge_count} new SEMANTIC edges.")
    
    # --- 4. [UPGRADED] Add REFERENTIAL edges ---
    print("Finding and adding REFERENTIAL edges...")
    
    # Pattern 1: Looks for "Term" shall mean... (now more flexible)
    # Makes quotes optional, looks for capitalized word
    definition_pattern_1 = re.compile(r'("?([A-Z][A-Za-z\s]+)"?)\s+(shall mean|is defined as|means|shall have the meaning)', re.IGNORECASE)
    
    # Pattern 2: Looks for (... hereinafter "Term")
    definition_pattern_2 = re.compile(r'\((?:hereinafter\s+)?(?:referred\s+to\s+as\s+)?"([^"]+)"\)', re.IGNORECASE)

    definitions_map = {} # Stores { "Defined Term": node_id }
    
    # First pass: Find all definitions
    for node_id, data in G.nodes(data=True):
        # Try pattern 1
        matches_1 = definition_pattern_1.findall(data['content'])
        for match in matches_1:
            defined_term = match[0].replace('"', '').strip() # Get the term
            if len(defined_term) > 3: 
                definitions_map[defined_term] = node_id
                
        # Try pattern 2
        matches_2 = definition_pattern_2.findall(data['content'])
        for match in matches_2:
            defined_term = match.strip() # This pattern only captures the term
            if len(defined_term) > 3:
                definitions_map[defined_term] = node_id

    print(f"Found {len(definitions_map)} defined terms.")
    
    # Second pass: Find all references
    referential_edge_count = 0
    if definitions_map: # Only run if we found definitions
        # Create a fast regex to find any of our defined terms
        reference_pattern = re.compile(r'\b(' + '|'.join(re.escape(k) for k in definitions_map.keys()) + r')\b', re.IGNORECASE)
        
        for node_id, data in G.nodes(data=True):
            references = reference_pattern.findall(data['content'])
            for term in references:
                term_key = next(k for k in definitions_map if k.lower() == term.lower())
                def_node_id = definitions_map[term_key]
                
                if node_id != def_node_id:
                    G.add_edge(
                        node_id, 
                        def_node_id, 
                        type="REFERENTIAL",
                        term=term_key
                    )
                    referential_edge_count += 1

    print(f"Added {referential_edge_count} new REFERENTIAL edges.")
    
    # --- 5. Return the final graph ---
    print(f"Graph built: {G.number_of_nodes()} nodes, {G.number_of_edges()} total edges.")
    return G

def process_contract_to_graph(pdf_path, data_processor_func):
    """
    A main "pipeline" function that runs all steps.
    """
    # 1. Run Stage 1 (from our other file)
    nodes_list = data_processor_func(pdf_path)

    # 2. Run Stage 2a (Embeddings)
    nodes_with_embeddings = generate_node_embeddings(nodes_list)

    # 3. Run Stage 2b (Build Graph)
    graph = build_graph(nodes_with_embeddings)

    return graph

def convert_nx_to_pyg_data(nx_graph, labels_tensor):
    """
    Converts our NetworkX graph into a PyTorch Geometric
    Data object that our GATModel can understand.

    [THIS IS THE CORRECTED VERSION that accepts 2 arguments]
    """
    pyg_graph = Data()

    # --- 1. Node Features (x) ---
    embeddings = [data['embedding'] for _, data in nx_graph.nodes(data=True)]
    embeddings_array = np.array(embeddings)
    pyg_graph.x = torch.tensor(embeddings_array, dtype=torch.float)

    # --- 2. Edge Index (edge_index) ---
    edge_list = list(nx_graph.edges())
    source_nodes = [u for u, v in edge_list]
    target_nodes = [v for u, v in edge_list]

    pyg_graph.edge_index = torch.tensor([
        source_nodes + target_nodes,  # Add 0->1, 1->2
        target_nodes + source_nodes   # Add 1->0, 2->1
    ], dtype=torch.long).contiguous()

    # --- 3. Labels (y) [THE UPDATE] ---
    # Assign the "ground truth" labels we pass in
    pyg_graph.y = labels_tensor

    print("\nConverted NetworkX graph to PyTorch Geometric data object.")
    return pyg_graph