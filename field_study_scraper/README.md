# Field Study Scraper

In order to test a bunch of real world software development projects for unsafety in RTS, I
performed a broad search in the top 100 GitHub Java projects. This folder contains the resources
used to query, download and analyze the projects.

Results for the different kinds of unsafety (details in the paper and presentation) are stored in a
csv for each scanned project in the `*_data` folders.

I know that the code is quite messy, but I just didn't have time (yet) to clean it up.

## Run

This repository manages its Python package dependencies using Poetry. To install the dependency management tool, refer to [the installation docs](https://python-poetry.org/docs/#installation) or use the following command for the linux installation:

```bash
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -
```

The Github API requires a personal access token to work using your Github account. This can be acquired here: https://github.com/settings/tokens ([guide](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token))
