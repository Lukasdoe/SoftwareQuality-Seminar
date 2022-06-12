# Title: "The Unsafety in Java Regression Test Selection and its Occurrence in the Wild"

This is all the work that I did for the "Software Quality"-Seminar, hosted by the Chair for Software and Systems Engineering (I04) at TUM.

All the work is shared under the CC-BY-4.0 license. I am looking forward to seeing what other people can make out of the data, feel free to give me a heads up :)

Seminar Paper: [PDF](./paper.pdf)
Seminar Presentation: [PDF](./presentation_handout.pdf) ([with notes](./presentation/presentation.pdf))

## Structure

- Paper source (LaTeX): [paper](./paper/)
- Presentation source (LaTeX): [presentation](./presentation/)
- PoC Repositories (Java): [proof_of_concept_repos](./proof_of_concept_repos/)
- Analysis-Code (mostly Python) + Results: [field_study_scraper](./field_study_scraper/)

The PoC Repositories are an important source for part 1 of the paper, where I find an document sources of unsafety of the examined RTS tools.

The Analysis-Code is more important for part 2, the field study. There, I analyze 100 real world open source Java projects from GitHub for the previously identified sources of unsafety.
