# funda-insights

## Usage
For the availability there are 3 options: 
- `all` (available, unavailable, negotiation)
- `available` (available)
- `unavailable` (sold houses)

You can use the python script as follows:

`poetry run python funda_insights/funda_data_retriever.py --area amsterdam 
--page_start 1 --n_pages 1 --availability all`

