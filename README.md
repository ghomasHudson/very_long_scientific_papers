# Very Long scientific papers

This dataset contains code and data for the very long scientific papers dataset based on arxiv.org. The data is stored under the `final/test` directory with `PAPER_ID.main.txt` and corresponding `PAPER_ID.abstract.txt` files.

## Data gathering process

The data is gathered (`main.py`) using the following steps:

- Search for anything containing the word `thesis` in the title using the arxiv api
- Download the source for these documents
- Use engrafo to convert this into html
- Filter the html to remove math, images, etc..
- Find the abstract and seperate it (if cannot be found, skip document)
- Convert to txt format

To gather your own data, simply run `main.py`.
