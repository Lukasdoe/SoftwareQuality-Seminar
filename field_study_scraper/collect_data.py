#! /usr/bin/env python3
import pandas as pd
import glob
import re
from matplotlib import pyplot as plt
from collections import defaultdict


def calc_commit_diff(df, list_changing_columns):
    commit_hashes = df["commit_hash"].drop_duplicates()
    hashes_with_diff = set()
    diffs_num = 0

    for i in range(len(commit_hashes) - 1):
        diff =  pd.concat(
                [
                    df[df["commit_hash"] == commit_hashes.iloc[i]],
                    df[df["commit_hash"] == commit_hashes.iloc[i + 1]],
                ]
            )[list_changing_columns].drop_duplicates(keep=False)
        if len(diff) > 0:
            hashes_with_diff.add(commit_hashes.iloc[i + 1])
            diffs_num += len(diff)
    return diffs_num, hashes_with_diff


def get_boxplot_data(data_points):
    bp = plt.boxplot(data_points)
    print(bp)
    return {
        "lq": bp["whiskers"][0].get_ydata()[0],
        "uq": bp["whiskers"][1].get_ydata()[0],
        "lw": bp["caps"][0].get_ydata()[0],
        "uw": bp["caps"][1].get_ydata()[0],
        # "b": bp["boxes"][0].get_ydata()[0],
        "m": bp["medians"][0].get_ydata()[0],
        "fliers": bp["fliers"][0].get_ydata(),
    }


def collect_box_plot():
    external_files = glob.glob("./configfile_data/config_file_scan_*.csv")
    spring_injection_files = glob.glob("./injection_data/injection_scan_*.csv")
    guice_injection_files = glob.glob(
        "./guice_injection_data/guice_injection_scan_*.csv"
    )
    profiling_files = glob.glob("./profiling_data/profiling_scan_*.csv")
    reflection_changes_files = glob.glob(
        "./reflection_data/reflected_class_changes_*.csv"
    )
    reflection_files = glob.glob("./reflection_data/reflection_access_*.csv")

    external_found_counts = []
    injection_found_counts = []
    profiling_ekstazi_found_counts = []
    profiling_openclover_found_counts = []
    reflection_found_counts = []
    reflection_changes_found_counts = []

    for file in external_files:
        df = pd.read_csv(file)
        external_found_counts.append(len(df))

    for file in spring_injection_files:
        df = pd.read_csv(file)
        injection_found_counts.append(len(df[df["filename"].str.endswith(".java")]))

    for k, file in enumerate(guice_injection_files):
        df = pd.read_csv(file)
        injection_found_counts[k] += len(df[df["filename"].str.endswith(".java")])

    for file in profiling_files:
        df = pd.read_csv(file).drop_duplicates("file_path")
        profiling_ekstazi_found_counts.append(
            len(df[df["problematic_tool"] == "ekstazi"])
        )
        profiling_openclover_found_counts.append(
            len(df[df["problematic_tool"] == "clover"])
        )

    for file in reflection_files:
        df = pd.read_csv(file)
        reflection_found_counts.append(len(df["file_path"].drop_duplicates()))

    for file in reflection_changes_files:
        df = pd.read_csv(file)
        reflection_changes_found_counts.append(len(df))

    print("External Files:", external_found_counts)
    # print(get_boxplot_data(external_found_counts), "\n")

    print("Injections:", injection_found_counts)
    # print(get_boxplot_data(injection_found_counts), "\n")

    print("Profiling Ekstazi:", profiling_ekstazi_found_counts)
    # print(get_boxplot_data(profiling_ekstazi_found_counts), "\n")

    print("Profiling OpenClover:", profiling_openclover_found_counts)
    # print(get_boxplot_data(profiling_openclover_found_counts), "\n")

    print("Reflections Access:", reflection_found_counts)
    # print(get_boxplot_data(reflection_found_counts), "\n")

    print("Reflections Changes:", reflection_changes_found_counts)
    # print(get_boxplot_data(reflection_found_counts), "\n")


def unsafety_per_commit():
    external_files = glob.glob("./configfile_data/config_file_scan_*.csv")
    spring_injection_files = glob.glob("./injection_data/injection_scan_*.csv")
    guice_injection_files = glob.glob(
        "./guice_injection_data/guice_injection_scan_*.csv"
    )
    profiling_files = glob.glob("./profiling_data/profiling_scan_*.csv")
    reflection_changes_files = glob.glob(
        "./reflection_data/reflected_class_changes_*.csv"
    )
    reflection_files = glob.glob("./reflection_data/reflection_access_*.csv")

    commits_with_external_unsafety = []
    commits_changing_injection_found_counts = []
    reflection_found_counts = []
    reflection_changes_found_counts = []

    commits_with_at_least_one_source_of_unsafety = set()

    for file in external_files:
        df = pd.read_csv(file)
        commits_with_at_least_one_source_of_unsafety |= set(df["commit_hash"].drop_duplicates())
        commits_with_external_unsafety.append(len(df["commit_hash"].drop_duplicates()))

    for file in spring_injection_files:
        df = pd.read_csv(file)
        commit_hashes = df[df["filename"].str.endswith(".java")]["commit_hash"].drop_duplicates()
        commits_with_at_least_one_source_of_unsafety |= set(commit_hashes)
        commits_changing_injection_found_counts.append(
            len(
               commit_hashes
            )
        )

    for k, file in enumerate(guice_injection_files):
        df = pd.read_csv(file)
        commit_hashes = df[df["filename"].str.endswith(".java")]["commit_hash"].drop_duplicates()
        commits_with_at_least_one_source_of_unsafety |= set(commit_hashes)
        commits_changing_injection_found_counts[k] += len(
            commit_hashes
        )

    for file in reflection_files:
        df = pd.read_csv(file)
        diff_num, hashes_with_diffs = calc_commit_diff(df, ["file_path", "filename", "accessed_class"])
        reflection_found_counts.append(diff_num
            
        )
        commits_with_at_least_one_source_of_unsafety |= set(hashes_with_diffs)

    for file in reflection_changes_files:
        df = pd.read_csv(file)
        commit_hashes = df["commit_hash"].drop_duplicates()
        commits_with_at_least_one_source_of_unsafety |= set(commit_hashes)
        reflection_changes_found_counts.append(len(commit_hashes))

    num_uns_comms = len(commits_with_at_least_one_source_of_unsafety)
    print(
        f"Of the {100*100} scanned commits, {sum(commits_with_external_unsafety)} external_files unsfty, {sum(commits_changing_injection_found_counts)} injection unsafety, {sum(reflection_found_counts)} reflections access unsfty and {sum(reflection_changes_found_counts)} reflections changes unsafety."
    )
    print(f"Number of commits with at least one unsafety: {num_uns_comms}")
    print(
        f"This results in the following percentages: {sum(commits_with_external_unsafety) / num_uns_comms} external_files unsfty, {sum(commits_changing_injection_found_counts) / num_uns_comms} injection unsafety, {sum(reflection_found_counts) / num_uns_comms} reflections access unsfty and {sum(reflection_changes_found_counts) / num_uns_comms} reflections changes unsafety."
    )
    print(commits_with_external_unsafety)
    print(commits_changing_injection_found_counts)
    print(reflection_found_counts)
    print(reflection_changes_found_counts)
    # print(
    #     sum(profiling_ekstazi_found_commits),
    #     sum(profiling_openclover_found_commits),
    #     profiling_ekstazi_found_commits,
    #     profiling_openclover_found_commits,
    # )


def all_other_stuff():
    ### config files

    data_files = glob.glob("**/config_*.csv")

    num_commits_with_changes = 0
    number_of_changed_files_total = 0
    number_of_changed_lines_total = 0

    for file in data_files:
        df = pd.read_csv(file)
        num_commits_with_changes += len(df["commit_hash"].drop_duplicates())
        number_of_changed_files_total += len(df)
        for change in df["changes"]:
            c = eval(change)
            number_of_changed_lines_total += len(c["added"])
            number_of_changed_lines_total += len(c["deleted"])

    print("Number of config files changing commits:", num_commits_with_changes)
    print("Total number of changed files (sum):", number_of_changed_files_total)
    print("Total number of changed lines:", number_of_changed_lines_total)

    ### injection data

    data_files = glob.glob("**/injection_scan*.csv")

    num_commits_with_changes = 0
    number_of_changed_beans_total = 0

    for file in data_files:
        df = pd.read_csv(file)
        num_commits_with_changes += len(df["commit_hash"].drop_duplicates())
        number_of_changed_beans_total += len(df)

    print("Number of bean changing commits:", num_commits_with_changes)
    print("Total number of changed beans:", number_of_changed_beans_total)

    reason_count = defaultdict(lambda: 0)
    ref_count = 0

    guice_csvs = glob.glob("**/guice_injection_scan*.csv")
    for file in guice_csvs:
        df = pd.read_csv(file)
        if len(df) > 0:
            ref_count += len(df[df["filename"].str.endswith(".java")])
            for reason in df[df["filename"].str.endswith(".java")]["reason"]:
                reason_count[reason] += 1
    print(reason_count, ref_count)

    ## profiling data

    data_files = glob.glob("**/profiling_scan*.csv")

    repos_only_ekstazi = 0
    repos_only_openclover = 0
    repos_both = 0
    files_total = 0

    for file in data_files:
        df = pd.read_csv(file)
        if len(df) > 0:
            unsupported_tools = df["problematic_tool"].drop_duplicates().to_list()
            if unsupported_tools == ["ekstazi", "clover"]:
                repos_both += 1
            elif "ekstazi" in unsupported_tools:
                repos_only_ekstazi += 1
            elif "clover" in unsupported_tools:
                repos_only_openclover += 1
            files_total += len(df["file_path"].drop_duplicates())

    print("Ekstazi only repos:", repos_only_ekstazi)
    print("Openclover only repos:", repos_only_openclover)
    print("Both unsupported:", repos_both)
    print("Total unsupported files:", files_total)

    ## reflection data

    data_files = glob.glob("**/reflection_access*.csv")

    min_uses = 0xFFFFFFF
    max_uses = 0
    min_uses_repo = ""
    max_uses_repo = ""

    number_of_projects_with_at_least_one_occurence = 0
    total_number_of_times_class_for_name_is_called = 0

    for file in data_files:
        df = pd.read_csv(file)
        if len(df) > 0:
            number_of_projects_with_at_least_one_occurence += 1

            number_of_uses = len(df["file_path"].drop_duplicates())
            total_number_of_times_class_for_name_is_called += number_of_uses
            if number_of_uses < min_uses:
                min_uses = number_of_uses
                min_uses_repo = file
            if number_of_uses > max_uses:
                max_uses = number_of_uses
                max_uses_repo = file

    print(
        "Number of repos with at least one occurence:",
        number_of_projects_with_at_least_one_occurence,
    )
    print("Total number of occurences:", total_number_of_times_class_for_name_is_called)
    print("Min occurences > 0:", min_uses, min_uses_repo)
    print("Max occurences:", max_uses, max_uses_repo)

    data_files = glob.glob("**/reflected_class_changes*.csv")

    total_num_commits = 0
    total_num_repos = 0

    for file in data_files:
        df = pd.read_csv(file)
        if len(df) > 0:
            total_num_repos += 1
            total_num_commits += len(df["commit_hash"].drop_duplicates())

    print("Number of repos with at least one occurence:", total_num_repos)
    print("Total number of occurences:", total_num_commits)

    ## full data affected

    df = pd.DataFrame(
        columns=[
            "project_name",
            "config_files",
            "dependency_injection",
            "profiling",
            "reflections",
        ]
    )

    repos = pd.read_csv("./final_data/repo_searches/acc.csv")
    for repo in repos.iloc:
        df = df.append({"project_name": repo["repo_name"]}, ignore_index=True)

    config_file_csvs = glob.glob("configfile_data/config_file_scan_*.csv")
    for file in config_file_csvs:
        config_df = pd.read_csv(file)
        df.at[int(re.search("(\d+)", file).groups()[0]), "config_files"] = len(
            config_df
        )

    injection_csvs = glob.glob("injection_data/injection_scan_*.csv")
    for file in injection_csvs:
        injection_df = pd.read_csv(file)
        df.at[int(re.search("(\d+)", file).groups()[0]), "dependency_injection"] = len(
            injection_df
        )

    guice_injection_csvs = glob.glob("guice_injection_data/guice_injection_scan*.csv")
    for file in guice_injection_csvs:
        guice_injection_df = pd.read_csv(file)
        df.at[
            int(re.search("(\d+)", file).groups()[0]), "dependency_injection_guice"
        ] = len(guice_injection_df)

    profiling_csvs = glob.glob("profiling_data/profiling_scan*.csv")
    for file in profiling_csvs:
        profiling_df = pd.read_csv(file)
        df.at[int(re.search("(\d+)", file).groups()[0]), "profiling"] = len(
            profiling_df.drop_duplicates("file_path")
        )

    reflection_csvs = glob.glob("reflection_data/reflection_access_*.csv")
    for file in reflection_csvs:
        reflection_df = pd.read_csv(file)
        df.at[int(re.search("(\d+)", file).groups()[0]), "reflections"] = len(
            reflection_df.drop_duplicates("file_path")
        )

    num_unsafe_repos = len(df) - len(
        df.loc[
            (df.config_files == 0)
            & (df.dependency_injection == 0)
            & (df.profiling == 0)
            & (df.reflections == 0)
        ]
    )
    num_super_unsafe_repos = len(
        df.loc[
            (df.config_files > 0)
            & (df.dependency_injection > 0)
            & (df.profiling > 0)
            & (df.reflections > 0)
        ]
    )
    print(
        f"Von 100 untersuchten Projekten haben {num_unsafe_repos} in den 100 untersuchten Commits mindestens 1 Art von unsafety. {num_super_unsafe_repos} Projekte beinhalten in den untersuchten Commits sogar jede Art von entdeckter Unsafety."
    )
