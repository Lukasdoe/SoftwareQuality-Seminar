#! /usr/bin/env python3.9

import argparse
import logging
import os
import re
import signal
import subprocess
import sys
from typing import Iterator

import pandas as pd
from github import Github, UnknownObjectException
from numpy import isnan
from pydriller import Commit, Git, Repository
from pydriller.domain.commit import ModifiedFile

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(sys.stdout))


def get_args() -> dict[str, str]:
    p = argparse.ArgumentParser(
        description="Query Github API for git repositories which contain Maven projects that mainly use the Java programming language. Output is sorted by Github stars."
    )
    p.add_argument(
        "--output",
        "-o",
        default="./repos.csv",
        help="Pandas DF output dump path (CSV-Format)",
        required=False,
    )
    p.add_argument(
        "--input",
        "-i",
        help="Pandas DF input path (CSV-Format)",
        required=False,
    )
    p.add_argument(
        "--token", "-t", type=str, required=True, help="Github API Auth Token."
    )
    return p.parse_args()


class RepositoryParser:
    java_file_extensions = {"java", "jar", "class"}
    grep_include_str = " ".join(f"--include='*.{p}'" for p in java_file_extensions)
    ignored_file_extensions = {
        "gitignore",
        "adoc",
        "Jenkinsfile",
        "sh",
        "cmd",
        "exe",
        "md",
        "README",
        "LICENSE",
        "NOTICE",
        "Makefile",
        "html"
    }
    ignored_directories = {".vscode", ".idea", ".git", ".mvn", "META-INF"}
    grep_exclude_str = " ".join(
        f"--exclude-dir='{dir_name}'" for dir_name in ignored_directories
    )
    result_dfs = dict()

    def __init__(self, repo_url: str, dfs_to_generate: set[str]):
        self.repo = Repository(repo_url, order="reverse")

        if "external_files" in dfs_to_generate:
            self.result_dfs["external_files"] = pd.DataFrame(
                columns=["commit_hash", "modified_file_path", "affected_files"]
            )
            self.result_dfs["external_files"].set_index("commit_hash", inplace=True)

        if "dependency_injection" in dfs_to_generate:
            self.result_dfs["dependency_injection"] = pd.DataFrame(columns=["commit_hash", "modified_file_path", "line"])
            self.result_dfs["dependency_injection"].set_index(
                "commit_hash", inplace=True
            )

    def filter_commit(self, commit: Commit) -> bool:
        return (
            # 1. don't use the first commit
            commit.parents == []
            or
            # 2. only use commits from the master branch
            not ("master" in commit.branches or "main" in commit.branches)
            or
            # 3. only use commits which actually contain changes
            commit.files == 0
        )

    def detect_configuration_file_changes(self, commit: Commit):
        # detect, if non-java files where changed in the commit
        for mf in self.modified_file_iter_filter(commit.modified_files):
            try:
                # search for files containing a reference to the changed file
                grep_res = subprocess.check_output(
                    f'grep -F "{mf.filename}" -RHno {self.grep_exclude_str} {self.grep_include_str} {commit.project_path} | cut -d: -f1-2',
                    shell=True,
                ).decode()
                if grep_res:
                    logger.info(
                        f"Commit #{commit.hash}, file {commit.project_path}/{mf.new_path or mf.old_path} was a config file change."
                    )
                    logger.debug(grep_res)
                    self.result_dfs["external_files"].loc[commit.hash] = {
                        "commit_hash": commit.hash,
                        "changed_file_path": mf.new_path or mf.old_path,
                        "affected_files": grep_res.splitlines(),
                    }
            except subprocess.CalledProcessError:
                pass

    def modified_file_iter_filter(
        self, mfs: Iterator[ModifiedFile]
    ) -> Iterator[ModifiedFile]:
        for mf in mfs:
            # exclude files from ignored directories
            if (
                not bool(
                    re.search(
                        f"(^|/)({'|'.join(self.ignored_directories)})/",
                        mf.new_path or mf.old_path,
                    )
                )
                and
                # exclude ignored files and java files (we only search external files)
                mf.filename.split(".")[-1]
                not in self.java_file_extensions | self.ignored_file_extensions
            ):
                yield mf

    def detect_dependency_injection_changes(self, commit: Commit) -> None:
        search_string = "@Bean"

        for mf in commit.modified_files:
            for line, string in mf.diff_parsed["deleted"] + mf.diff_parsed["added"]:
                if search_string in string:
                    logger.info(
                        f"Commit #{commit.hash}, file {commit.project_path}/{mf.new_path or mf.old_path} changed a @Bean."
                    )
                    self.result_dfs["dependency_injection"].loc[commit.hash] = {
                        "commit_hash": commit.hash,
                        "modified_file_path": mf.new_path or mf.old_path,
                        "line": line,
                    }

    def prepare_local_repo(self, commit: Commit) -> None:
        git_wrapper = Git(commit.project_path)
        git_wrapper.checkout(commit.hash)

    def run(self):
        if len(self.result_dfs) < 1:
            return

        for commit in self.repo.traverse_commits():
            if self.filter_commit(commit):
                continue
            self.prepare_local_repo(commit)

            if "external_files" in self.result_dfs.keys():
                self.detect_configuration_file_changes(commit)

            if "dependency_injection" in self.result_dfs.keys():
                self.detect_dependency_injection_changes(commit)


def df_saver(df: pd.DataFrame, output_path: str) -> None:
    def signal_handler(sig, frame):
        save_df(df, output_path)
        sys.exit(0)

    return signal_handler


def save_df(df: pd.DataFrame, output_path: str):
    df.sort_values("stars", ascending=False, inplace=True)
    df.to_csv(output_path)


if __name__ == "__main__":
    args = get_args()
    gh = Github(login_or_token=args.token)
    data_storage = (
        pd.read_csv(args.input)
        if args.input is not None
        else pd.DataFrame(columns=["repo_name", "page", "url", "stars"])
    )
    data_storage.set_index("repo_name", inplace=True)
    signal.signal(signal.SIGINT, df_saver(data_storage, args.output))
    loadRepositories(data_storage, gh)
    save_df(data_storage, args.output)
