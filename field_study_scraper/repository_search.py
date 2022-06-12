import os
from git.objects import commit
from github import Github, UnknownObjectException
from github.Branch import Branch
from pydriller import Repository as LocalRepo
from github import Repository as RemoteRepo
from itertools import islice
import logging
import sys
import re
import pandas as pd
from pydriller.git import Git

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(sys.stdout))


class RepositorySearch:
    start_with_first_page = True
    query_string_1 = """
        is:public
        archived:false
        pushed:>=2020-06-01
        NOT tutorial NOT example NOT sample in:description
        fork:false
        stars:>=100
    """

    query_string_2 = """
        language:"Java"
        is:public
        archived:false
        pushed:>=2020-06-01
        NOT tutorial NOT example NOT sample in:description
        fork:false
        stars:>=100
    """

    query_string_3 = """
        mvn in:readme
        is:public
        archived:false
        pushed:>=2020-06-01
        NOT tutorial NOT example NOT sample in:description
        fork:false
        stars:>=100
    """

    unit_test_regex = re.compile(r"(@Test|extends\ TestCase)")

    def __init__(self, github_login: str) -> None:
        self.github = Github(github_login)
        self.result = pd.DataFrame(
            columns=[
                "repo_name",
                "page",
                "stars",
                "number_of_tests",
                "total_number_commits",
                "url",
                "latest_commit_hash",
                "main_branch",
                "java_language_percent",
            ]
        )
        self.result.set_index("repo_name", inplace=True)

    def run(self):
        logger.info(
            "Querying Github API for repositories, press CTRL+C to end the search and save results."
        )
        pages = self.github.search_repositories(
            query=self.query_string_2, sort="stars", order="desc"
        )
        logger.info(f"Found {pages.totalCount} valid repositories, starting search.")
        for i in range(0, pages.totalCount):
            try:
                logger.info(f"Entering page {i}")

                remote_repo: RemoteRepo
                for remote_repo in pages.get_page(i):
                    try:
                        # Only select projects with Java as the main language
                        repo_languages = remote_repo.get_languages()
                        if "Java" not in repo_languages.keys():
                            logger.info(
                                f"Skipping {remote_repo.name} because it doesn't contain Java code."
                            )
                            continue

                        summed_langs = sum(v for k, v in repo_languages.items())
                        languages = [
                            (k, v / summed_langs * 100) for k, v in repo_languages.items()
                        ]
                        languages.sort(key=lambda x: x[1], reverse=True)
                        repo_languages = {k: v for k, v in languages}
                        if repo_languages["Java"] <= 50:
                            logger.info(
                                f"Skipping {remote_repo.name} because its main language is not Java (only {repo_languages['Java']}%)"
                            )
                            continue

                        # Only select repositories with a "main" or "master" branch (further only called "main")
                        main_branch: str = None
                        repo_branch_names = {branch.name for branch in remote_repo.get_branches()}
                        if "main" in repo_branch_names:
                            main_branch = "main"
                        elif "master" in repo_branch_names:
                            main_branch = "master"
                        else:
                            logger.info(
                                f"Skipping {remote_repo.full_name}, no main / master branch found."
                            )
                            continue

                        local_repo = LocalRepo(
                            remote_repo.clone_url,
                            order="reverse",
                            only_in_branch=main_branch,
                        )

                        i = 0
                        for commit in local_repo.traverse_commits():
                            if commit.files > 0:
                                i += 1
                            if i > 100:
                                last_valid_commit = commit
                                break

                        # Only select project with at least 101 commits on the main branch
                        if i < 100 or last_valid_commit is None:
                            logger.info(
                                f"Skipping {remote_repo.full_name}, less than 101 commits on the {main_branch} branch."
                            )
                            continue

                        # Initialize local repository for file searches
                        local_git = Git(last_valid_commit.project_path)
                        local_git.checkout(last_valid_commit.hash)

                        # Only select maven projects (find pom.xml file)
                        if os.path.join(local_git.path, "pom.xml") not in local_git.files():
                            logger.info(
                                f"Skipping {remote_repo.full_name}, no pom.xml file found."
                            )
                            continue

                        # Only select repository with at least 100 unit tests
                        # Based on annotations or junit3 classes
                        num_unit_tests = 0
                        for file_path in local_git.files():
                            if not file_path.endswith(".java"):
                                continue
                            with open(file_path) as src_file:
                                for line in src_file.readlines():
                                    if re.search(self.unit_test_regex, line):
                                        num_unit_tests += 1

                        if num_unit_tests < 100:
                            logger.info(
                                f"Skipping {remote_repo.full_name}, less than 100 unit tests {main_branch} branch."
                            )
                            continue

                        # save to dataframe
                        logger.info(f"Saving repository {remote_repo.full_name}")
                        self.result.loc[remote_repo.full_name] = {
                            "repo_name": remote_repo.full_name,
                            "page": i,
                            "url": remote_repo.clone_url,
                            "stars": remote_repo.stargazers_count,
                            "java_language_percent": repo_languages["Java"],
                            "number_of_tests": num_unit_tests,
                            "total_number_commits": remote_repo.get_commits().totalCount,
                            "latest_commit_hash": next(local_repo.traverse_commits()).hash,
                            "main_branch": main_branch,
                        }
                        self.result.sort_values("stars", ascending=False, inplace=True)
                        self.result.to_csv("./new_repos.csv")
                    except Exception as e:
                        logger.error(f"{remote_repo.name}: {e}")
            except Exception as e:
                logger.error(e)
                return
