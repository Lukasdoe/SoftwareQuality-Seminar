import re

import pandas as pd
from pydriller import Commit, Git
from repository_scanner import Scanner


class ReflectionScanner(Scanner):
    __slots__ = [
        "df_reflection_access",
        "df_reflection_changes",
        "export_path_access",
        "export_path_changes",
    ]
    df: pd.DataFrame
    export_path: str

    reflective_access_pattern = re.compile(
        r"[\^\s]Class.forName\(\"(?P<fqn>[a-zA-Z_\.]*)\""
    )

    def __init__(self, export_path_access: str, export_path_changes: str):
        # action \in {ADD = 1, COPY = 2, RENAME = 3, DELETE = 4, MODIFY = 5, UNKNOWN = 6}
        self.df_reflection_access = pd.DataFrame(
            columns=["commit_hash", "file_path", "filename", "line", "accessed_class"]
        )
        self.df_reflection_changes = pd.DataFrame(
            columns=[
                "commit_hash",
                "file_path",
                "filename",
                "action",
                "reflective_reference_filepath",
                "reflective_reference_line",
            ]
        )
        self.export_path_access = export_path_access
        self.export_path_changes = export_path_changes

    def scan(self, commit: Commit):
        git = Git(commit.project_path)
        old_head = git.get_head().hash

        # 1. collect all files / class specifiers that are used for undetected reflective class loading
        git.checkout(commit.hash)
        accessed_classes_detail = dict()
        accessed_classes = set()

        for abs_path, proj_path in zip(
            git.files(),
            list(map(lambda f: f.replace(commit.project_path + "/", ""), git.files())),
        ):
            # 1. only scan java code source files
            if len(proj_path.split(".")) < 2 or proj_path.split(".")[-1] != "java":
                continue

            with open(abs_path) as f:
                for line_n, line in enumerate(f.readlines()):
                    # 2. search for every occurrence of the reflective class loading
                    for match in self.reflective_access_pattern.finditer(line):
                        accessed_classes.add(match.group("fqn"))
                        accessed_classes_detail[match.group("fqn")] = (
                            proj_path,
                            line_n,
                        )

                        self.df_reflection_access = self.df_reflection_access.append(
                            {
                                "commit_hash": commit.hash,
                                "file_path": proj_path,
                                "filename": proj_path.split("/")[-1],
                                "line": line_n,
                                "accessed_class": match.group("fqn"),
                            },
                            ignore_index=True,
                        )

        git.checkout(old_head)

        # 3. translate java fully qualified class names to a possible path (only works for local classes)
        accessed_classes = frozenset(
            fqcn.replace(".", "/") for fqcn in accessed_classes
        )

        # 4. search for changes in the accessed class files
        for mf in commit.modified_files:
            path = mf.new_path or mf.old_path
            for fqcn in accessed_classes:
                if fqcn in path:
                    self.df_reflection_changes = self.df_reflection_changes.append(
                        {
                            "commit_hash": commit.hash,
                            "file_path": path,
                            "filename": mf.filename,
                            "action": mf.change_type.value,
                            "reflective_reference_filepath": accessed_classes_detail[
                                fqcn.replace("/", ".")
                            ][0],
                            "reflective_reference_line": accessed_classes_detail[fqcn.replace("/", ".")][
                                1
                            ],
                        },
                        ignore_index=True,
                    )

    def export(self):
        self.df_reflection_changes.to_csv(self.export_path_changes)
        self.df_reflection_access.to_csv(self.export_path_access)
