"""scripts/paper_stats.py"""

import tiktoken

from tqdm import tqdm

from config import PAPERS_DIR

PAPERS_TXT_DIR = PAPERS_DIR.joinpath("txt")

tokenizer = tiktoken.get_encoding("cl100k_base")

# Get the number of papers
num_papers = len(list(PAPERS_TXT_DIR.glob("*.txt")))
print(f"Number of papers: {num_papers}")

# # Get the number of tokens in the papers, along with some basic statistics
num_tokens = []
for paper in tqdm(PAPERS_TXT_DIR.glob("*.txt"), desc="Counting tokens"):
    with open(paper, "r", encoding="utf-8") as f:
        num_tokens.append(len(tokenizer.encode(f.read())))
print(f"Number of tokens: {sum(num_tokens)}")
print(f"Average number of tokens per paper: {round(sum(num_tokens) / len(num_tokens))}")
print(f"Max number of tokens in a paper: {max(num_tokens)}")
print(f"Min number of tokens in a paper: {min(num_tokens)}")
