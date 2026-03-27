from Bio import SeqIO, pairwise2
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import linkage, dendrogram
from scipy.spatial.distance import squareform
# Load sequences
records = list(SeqIO.parse("../data/combined.fasta", "fasta"))


def clean_name(record):
    name = record.id.split("|")[-1]
    name = name.replace("_HUMAN", "")
    name = name.replace("_MOUSE", "")
    name = name.replace("_DROME", "")
    name = name.split("_")[0]
    return name


names = [clean_name(record) for record in records]
sequences = [str(record.seq) for record in records]

# Compute similarity matrix
n = len(sequences)
matrix = np.zeros((n, n))

for i in range(n):
    for j in range(n):
        score = pairwise2.align.globalxx(
            sequences[i], sequences[j],
            score_only=True
        )
        matrix[i, j] = score

# Convert to DataFrame
df = pd.DataFrame(matrix, index=names, columns=names)

# Normalize
df = df/df.values.max()

# Heatmap
group_colors = []
for record in records:
    if "HUMAN" in record.id or "MOUSE" in record.id or "DROME" in record.id:
        group_colors.append("blue")  # Bilateria
    else:
        group_colors.append("red")  # Cnidaria

g = sns.clustermap(df, cmap="viridis", row_colors=group_colors,
                   col_colors=group_colors, figsize=(10, 10),
                   xticklabels=True,
                   yticklabels=True,
                   dendrogram_ratio=(0.15, 0.15),
                   cbar_pos=(0.02, 0.8, 0.05, 0.15))
plt.title("Sequence Similarity Heatmap")
# Rotate labels for readability
plt.setp(g.ax_heatmap.get_xticklabels(), rotation=90, fontsize=9)
plt.setp(g.ax_heatmap.get_yticklabels(), rotation=0, fontsize=9)
g.figure.tight_layout()
g.savefig("../results/clustered_heatmap.png", dpi=300)
