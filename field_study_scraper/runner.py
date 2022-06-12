#!/usr/bin/env python3

from repository_scanner import RepositoryScanner
from commit_scanners import ConfigFileScanner, InjectionScanner, ProfilingScanner, ReflectionScanner, InjectionScannerGuice
import pandas as pd

repos = pd.read_csv("./final_data/repo_searches/acc.csv")

for index, repo in repos.iloc[:100].iterrows():
    print(f"Scanning repository {index}: {repo['repo_name']}")
    scanner = RepositoryScanner(
        repo["url"],
        repo["main_branch"],
        repo["latest_commit_hash"],
        [
            # ReflectionScanner(
            #     export_path_changes=f"./reflection_data/reflected_class_changes_{index}.csv",
            #     export_path_access=f"./reflection_data/reflection_access_{index}.csv",
            # ),
            # ProfilingScanner(f"./profiling_data/profiling_scan_{index}.csv"),
            # InjectionScanner(f"./injection_data/injection_scan_{index}.csv"),
            InjectionScannerGuice(f"./guice_injection_data/guice_injection_scan_{index}.csv"),
            # ConfigFileScanner(f"./configfile_data/config_file_scan_{index}.csv"),
        ],
    )
    try:
        scanner.run()
    except Exception as e:
        print(e)
