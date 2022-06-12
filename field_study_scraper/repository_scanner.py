from pydriller import Repository, Commit
from abc import ABC, abstractmethod


class Scanner(ABC):
    @abstractmethod
    def scan(self, commit: Commit):
        pass

    @abstractmethod
    def export(self):
        pass


class RepositoryScanner:
    __slots__ = ["repo", "branch", "scanners"]
    repo: Repository
    branch: str
    scanners: list[Scanner]

    def __init__(
        self,
        clone_url: str,
        branch: str,
        latest_commit_hash: str,
        scanners: list[Scanner],
    ):
        self.repo = Repository(
            clone_url,
            only_in_branch=branch,
            to_commit=latest_commit_hash,
            order="reverse",
        )
        self.branch = branch
        self.scanners = scanners

    def commit_filter(self, commit_iter):
        commit: Commit
        for commit in commit_iter:
            if (
                bool(commit.parents)
                and bool(commit.modified_files)
                and self.branch in commit.branches  # double check correct branch
            ):
                yield commit

    def run(self):
        for k, commit in enumerate(self.commit_filter(self.repo.traverse_commits())):
            for scanner in self.scanners:
                scanner.scan(commit)
            if k >= 99:
                break

        # save the accumulated file data
        for scanner in self.scanners:
            scanner.export()
