"""
Using the STAC python client to query the index.

You will see a `query` keyword, but this is not recommended by STAC. It is light
on features and the language is one of their invention. In contrast, `filters`
has many features and uses the Common Query Language
[CQL2](https://docs.ogc.org/is/21-065r2/21-065r2.html) to compose logical
operators.

NOTE: For the moment, if you want to query a property in the CMIP6 extension, it
must be prefixed by `properties.`. This is not the desired behavior and will be
[fixed](https://github.com/stac-extensions/cmip6/issues/9).
"""

import pystac_client

ITEMS_PER_PAGE = 100


def _check(results):
    """An example of how to take the results and page through them."""
    found = set()  # to ensure that we find just the variables in the search
    numMatched = 0
    numPage = 0
    for page in results.pages():
        numMatched = page.extra_fields["numMatched"]
        found = found | set(
            [item.properties["cmip6:variable_id"] for item in page.items]
        )
        numPage += 1
        print(f"page {numPage} returned {page.extra_fields["numReturned"]} items")
    print(f"Found {numMatched} total items, containing variable_id={found}")


client = pystac_client.Client.open("https://api.stac.ceda.ac.uk")

# Search for two variables composing a filter using the OR operator
results = client.search(
    collections="cmip6",
    limit=ITEMS_PER_PAGE,
    filter={
        "op": "or",
        "args": [
            {
                "args": [{"property": "properties.cmip6:variable_id"}, "rsus"],
                "op": "=",
            },
            {
                "args": [{"property": "properties.cmip6:variable_id"}, "rsds"],
                "op": "=",
            },
        ],
    },
)
_check(results)

# The same search using the IN operator
results = client.search(
    collections="cmip6",
    limit=ITEMS_PER_PAGE,
    filter={
        "op": "in",
        "args": [{"property": "properties.cmip6:variable_id"}, ["rsus", "rsds"]],
    },
)
_check(results)
