import pandas as pd
from pydriller.domain.commit import Commit
from repository_scanner import Scanner


class ConfigFileScanner(Scanner):
    __slots__ = ["df", "export_filename"]
    df: pd.DataFrame
    export_path: str

    maven_config_dirs = frozenset(
        {
            "src/main/resources/",
            "src/test/resources/",
            "src/main/filters/",
            "src/test/filters/",
        }
    )

    def __init__(self, export_path: str):
        # action \in {ADD = 1, COPY = 2, RENAME = 3, DELETE = 4, MODIFY = 5, UNKNOWN = 6}
        self.df = pd.DataFrame(
            columns=["commit_hash", "file_path", "filename", "action", "changes"]
        )
        self.export_path = export_path

    def scan(self, commit: Commit):
        # 1. The file has to be modified by this commit
        for mf in commit.modified_files:
            path = mf.new_path or mf.old_path

            # 2. Modified file lives / lived in one of the maven default configuration directories
            if any(dir in path for dir in self.maven_config_dirs):
                self.df = self.df.append(
                    {
                        "commit_hash": commit.hash,
                        "file_path": path,
                        "action": mf.change_type.value,
                        "filename": mf.filename,
                        "changes": mf.diff_parsed,
                    },
                    ignore_index=True,
                )

    def export(self):
        self.df.to_csv(self.export_path)
