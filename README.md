# funda-insights

## Usage
For the availability there are 3 options: 
- `all` (available, unavailable, negotiation)
- `available` (available)
- `unavailable` (sold houses)

You can choose to load the house urls from disk if you already have 
scraped them, by passing the `load_urls_from_disk` argument. By default, the urls
are not loaded from disk.

You can use the python script as follows:

```
poetry run python funda_insights/funda_data_retriever.py 
--area gouda 
--page_start 1 
--n_pages 1 
--availability all
--load_urls_from_disk
```

