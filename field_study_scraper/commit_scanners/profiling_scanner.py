import re

import pandas as pd
from pydriller import Commit, Git
from repository_scanner import Scanner


class ProfilingScanner(Scanner):
    __slots__ = ["df", "export_filename"]
    df: pd.DataFrame
    export_path: str

    ekstazi_res = {
        re.compile(r"\.getAnnotatedInterfaces\(\)"),
        re.compile(r"\.getAnnotatedSuperclass\(\)"),
        re.compile(r"\.toGenericString\(\)"),
    }

    clover_res = {
        re.compile(r"\.getDeclaredClasses\(\)"),
        re.compile(r"\.getDeclaredFields\(\)"),
        re.compile(r"\.getClasses\(\)"),
        re.compile(r"\.getFields\(\)"),
    }

    def __init__(self, export_path: str):
        self.df = pd.DataFrame(
            columns=["commit_hash", "file_path", "filename", "line", "problematic_tool"]
        )
        self.export_path = export_path

    def scan(self, commit: Commit):
        git = Git(commit.project_path)
        old_head = git.get_head().hash

        git.checkout(commit.hash)
        for abs_path, proj_path in zip(
            git.files(),
            list(map(lambda f: f.replace(commit.project_path + "/", ""), git.files())),
        ):
            # 1. only scan java code source files
            if len(proj_path.split(".")) < 2 or proj_path.split(".")[-1] != "java":
                continue

            with open(abs_path) as f:
                for line_n, line in enumerate(f.readlines()):
                    # 2. search for every occurrence of the known broken methods
                    if any(
                        re.search(compiled_re, line) for compiled_re in self.ekstazi_res
                    ):
                        self.df = self.df.append(
                            {
                                "commit_hash": commit.hash,
                                "file_path": proj_path,
                                "filename": proj_path.split("/")[-1],
                                "line": line_n,
                                "problematic_tool": "ekstazi",
                            },
                            ignore_index=True,
                        )
                    if any(
                        re.search(compiled_re, line) for compiled_re in self.clover_res
                    ):
                        self.df = self.df.append(
                            {
                                "commit_hash": commit.hash,
                                "file_path": proj_path,
                                "filename": proj_path.split("/")[-1],
                                "line": line_n,
                                "problematic_tool": "clover",
                            },
                            ignore_index=True,
                        )

        git.checkout(old_head)

    def export(self):
        self.df.to_csv(self.export_path)
