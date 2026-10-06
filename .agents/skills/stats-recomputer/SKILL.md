---
name: stats-recomputer
description: Parses APA-style test statistics from text and recomputes them using scipy.
---
# Statistics Recomputer

## Responsibilities
- Parses strings containing APA-style test statistics (e.g., \	(42)=3.14, p=.001\ or \F(2,87)=5.23, p<.05\).
- Extracts the test type, degrees of freedom, reported value, and reported p-value.
- Recomputes the expected p-value and test statistic using \scipy.stats\.
- Compares the reported and recomputed values, enforcing a stated rounding tolerance.
- Logs the parsed test and degrees of freedom, and determines the final verdict (reproduces or fails).
