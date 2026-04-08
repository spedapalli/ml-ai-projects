---
description: Review the give PR as argument and provide direct critique on how the code can be improved
context: fork
allowed-tools: Bash(git:*), Bash(gh:*)
model: haiku
---
## Context
- Current src directory `./*/src`
## Task
Review and critique the PR $ARGUMENTS for the following:
1. Code quality
2. Security implications(auth, data, password exposure)
3. Performance concerns (N+1 queries, missing indexes)
4. Test coverage gaps
5. Consistency with existing patterns in ./*/src directory

Be direct. Flag issues by severity
