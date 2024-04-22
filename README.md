# mlx-marimo-llm
Apple MLX LLMs - mlx-lm + marimo 

## edit: should be working now serially, running llama 8b-instruct 8bit (mlx) locally

- Entire concept and code and functions / SERP functions heavily copied from Matt Shumer @ https://github.com/mshumer/ai-researcher/blob/main/Claude_Researcher.ipynb
- My sole contribution on top of Matt's awesome notebook is putting it in Marimo and refactoring it to run on mlx-lm, trying to avoid parallel generations that cause crashes. Modify as you see fit!

## quick usage info
- sunday kid activities starting so here's a quick usage guide:
- pip install mlx-lm (macos only)
- pip install marimo
- change your model directory (using llama3 here but you could use anything)
- add your serp api key
- marimo edit marimo-serplexity.py (opens a browser to edit)
- may overwhelm and crash your system given the text gen volume. to be worked on, unless someone else gets to it before me
- UI is very very raw and not even close to what a good marimo app should look like
