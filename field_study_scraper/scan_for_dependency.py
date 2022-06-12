#!/usr/bin/env python3

import re
import os

import pandas as pd
from pydriller import Repository
from pydriller.git import Git

repos = pd.read_csv("./final_data/repo_searches/acc.csv")

# com\.google\.inject
# org\.springframework
# com\.google\.dagger
# <artifactId>cdi-api<\/artifactId>

# <artifactId>starts-maven-plugin<\/artifactId>
# org\.hyrts
# org\.openclover
# org\.ekstazi
# incremental-builder-with-ekstazi

# com\.netflix\.governator
search_regex = re.compile(r"<artifactId>junit<\/artifactId>(\n|.)*<version>3")

result_df = pd.DataFrame(
    columns=[
        "repo_name",
        "clone_url",
    ]
)

if __name__ == "__main__":
    for index, repo in repos.iloc[:100].iterrows():
        # keep the iterator alive, to keep the tempfiles
        try:
            commit_iter = Repository(
                repo["url"],
                only_in_branch=repo["main_branch"],
                order="reverse",
                to_commit=repo["latest_commit_hash"],
            ).traverse_commits()
            latest_commit = next(commit_iter)
            git = Git(latest_commit.project_path)
            git.checkout(repo["main_branch"])

            found_dep = False
            for root, _, files in os.walk(latest_commit.project_path):
                if "pom.xml" in files:
                    try:
                        with open(os.path.join(root, "pom.xml"), "r") as f:
                            for line in f.readlines():
                                if search_regex.search(line):
                                    project_file_path = os.path.join(
                                        root.replace(latest_commit.project_path, ""),
                                        "pom.xml",
                                    )
                                    result_df.loc[repo["repo_name"]] = {
                                        "repo_name": repo["repo_name"],
                                        "clone_url": repo["url"],
                                        "filepath": project_file_path,
                                        "line": line,
                                    }
                                    break
                    except Exception as e:
                        print(e)
        except Exception as e:
            print(repo["repo_name"], e)
    result_df.to_csv("./mvn_package_usage_scan/junit3.csv")
