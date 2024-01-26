# funda-insights

To use the script you need to run the following

- If you want houses that are currently available:
`poetry run python funda_insights/funda_data_retriever.py --area amsterdam --page_start 1 --n_pages 100`

- If you want houses that are unavailable (and already sold):
`poetry run python funda_insights/funda_data_retriever.py --area amsterdam --page_start 1 --n_pages 100  --find_past 
  true`
