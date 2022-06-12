import re

import pandas as pd
from pydriller.domain.commit import Commit
from repository_scanner import Scanner


class InjectionScannerGuice(Scanner):
    __slots__ = ["df", "export_filename"]
    df: pd.DataFrame
    export_path: str

    search_res = {
        re.compile(r"@AutoBindSingleton"),
        re.compile(r"@Provides"),
        re.compile(r"@CheckedProvides"),
        re.compile(r"@ProvidesIntoSet"),
        re.compile(r"@ProvidesIntoMap"),
        re.compile(r"@ProvidesIntoOptional"),
        re.compile(r"bind\(.*\)"),
        re.compile(r"LifecycleInjector")
    }

    def __init__(self, export_path: str):
        # action \in {ADD = 1, COPY = 2, RENAME = 3, DELETE = 4, MODIFY = 5, UNKNOWN = 6}
        self.df = pd.DataFrame(
            columns=["commit_hash", "file_path", "filename", "reason", "change", "line"]
        )
        self.export_path = export_path

    def scan(self, commit: Commit):
        for mf in commit.modified_files:
            path = mf.new_path or mf.old_path
            for line, changed_string in mf.diff_parsed["deleted"] + mf.diff_parsed["added"]:
                for compiled_re in self.search_res:
                    if re.search(compiled_re, changed_string):
                        self.df = self.df.append(
                            {
                                "commit_hash": commit.hash,
                                "file_path": path,
                                "reason": compiled_re.pattern,
                                "filename": mf.filename,
                                "change": changed_string,
                                "line": line,
                            },
                            ignore_index=True,
                        )

    def export(self):
        self.df.to_csv(self.export_path)
