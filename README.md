# Hyperliquid Builder List

A community maintained list of Hyperliquid Builders. Each builder must have a specific set of data to be included in the list. This list is free and maintained by the Hyperliquid community, feel free to contribute to the list by adding new builders or updating existing ones. Please follow the instructions below to add a new builder to the list.


# Adding a new builder


## Using a LLM to research and add a new builder
Simply modify the `LLM_PROMPT.md` file to include the URL and contract address of the builder you want to add. Then simply ask your favorite LLM to read it and allow it to to write the data in your local copy of the repo. Finding asset data (logo.svg, brand assets, etc.) is tricky, sometimes the LLM might not be able to gather it directly but will point you to places to research further.

## Manually adding a new builder
- Create a new folder in data with the address of the builder as name of the folder
- Copy blank.json to the new folder and fill in the data
- Example:
```json
{
    "id": "required_must_be_unique",
    "category": "required_must_exist_in_categories.json",
    "name": "required",
    "description": "required",
    "url": "required",
    "socials":{ 
        "x": null,
        "discord": null,
        "telegram": null,
        "linkedin": null,
        "youtube": null,
        "instagram": null,
        "facebook": null,
        "reddit": null,
        "github": null
    },
    "brand_color": "optional_must_be_hex_color"
}
```
```The **id** must be unique and is required. It must be a lowercase string with no spaces and only alphanumeric characters and underscores.
The **category** must be one of the values in categories.json and is required.
The **name** is a human readable name of the builder, is required, doesn't have to be unique
The **description** is a short description of the builder, is required
The **url** is the canonical URL of the builder, is required
The **socials** is an object with the social media platforms of the builder, is optional. Each social media platform must be one of the values in the socials object in blank.json
The **brand_color** is the primary color of the builder, is optional. It must be a valid hex color code
```
- Create a new folder in assets with the address of the builder as name of the folder
- Add either a logo.svg or a logo.png to the new folder. You can also add additional brand assets to a 'brand' folder inside the address folder
- Run the `aggregate.py` script to update the builders.json file

## Validation

Before you open a pull request, run:

```bash
python3 validate.py
```

This checks every `data/*.json` file (schema, category, logo, duplicate `id`) and confirms `builders.json` matches `aggregate.py`. The same check runs in GitHub Actions on pushes and pull requests to `main`.

