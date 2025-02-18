import pystac_client
import pystac_client.exceptions

client = pystac_client.Client.open("https://api.stac.ceda.ac.uk")

# Search 1: This works (ok but it was just a basic test)
results = client.search(
    collections="cmip6",
    max_items=10,
)
items = list(results.items_as_dicts())
print(f"Search 1: Found {len(items)} items\n")

# Search 2: This also works
results = client.search(
    collections="cmip6",
    max_items=None,
    limit=100,
    query=[
        "cmip6:variable_id=rsus",
        "cmip6:experiment_id=historical",
    ],
)
found = set()
numMatched = 0
for page in results.pages():
    numMatched = page.extra_fields["numMatched"]
    found = found | set(
        [
            (
                item.properties["cmip6:experiment_id"],
                item.properties["cmip6:variable_id"],
            )
            for item in page.items
        ]
    )
assert found == set([("historical", "rsus")])
print(f"Search 2: Found {numMatched} items\n")

"""
The above uses query and works, but I am finding it limiting. Other examples I
find (even on CEDA's site,
https://cedadev.github.io/datapoint/usage.html#more-about-searches) are single
facet only. For example, I cannot figure out how to search for multiple
variables at once (say `rsus` or `rsds`). Adding another variable item
overwrites the first one. I looked up the query extension...

https://github.com/stac-api-extensions/query

...and tried to expand the query based on guidance there...
"""

results = client.search(
    collections="cmip6",
    max_items=None,
    limit=100,
    query={
        "query": {
            "cmip6:experiment_id": {"in": ["historical"]},
            "cmip6:variable_id": {"in": ["rsus", "rsds"]},
        }
    },
)
try:
    items = list(results.items_as_dicts())
except pystac_client.exceptions.APIError as exc:
    print(exc)
    print("Search 3: failed\n")

"""
...but this fails validation. I get an error that seems to limit what is
possible with query.

'cmip6:variable_id', 'ctx': {'expected': \"'eq', 'ne', 'lt', 'lte', 'gt' or
'gte'\"}

I also found the following recommendation on the query extension README: "It is
recommended to implement the Filter Extension instead of the Query Extension.
Filter Extension is more well-defined, more expressive, and uses the
standardized CQL2 query language instead of the proprietary language defined
here."

So I also tried to use filter instead...
"""

# This does not return anything.
results = client.search(
    collections="cmip6",
    max_items=10,
    filter={"op": "=", "args": [{"property": "cmip6:variable_id"}, "rsus"]},
)
found = set()
numMatched = 0
for page in results.pages():
    numMatched = page.extra_fields["numMatched"]
    found = found | set([item.properties["cmip6:variable_id"] for item in page.items])
print(f"Search 4: Found {numMatched} items\n")

"""
...but this returns no results (but doesn't fail validation).
"""
