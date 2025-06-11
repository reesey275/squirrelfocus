# Work Item Generator

Use this template to create focused tasks from daily notes or planning
sessions. Generated tasks must keep each line under 79 characters.

## Template

```
Title: <short phrase summarizing the task>
Description: <single sentence description>
Type: <bug|feature|chore>
Tags: <comma separated keywords>
Steps:
  1. <first action>
  2. <next action>
  3. <final action>
```

## Example

Input:
```
Need to add automated style checks to the pipeline
```

Output:
```
Title: Add lint check to CI
Description: Fail builds when ruff finds issues
Type: feature
Tags: ci,lint,automation
Steps:
  1. Update CI config with ruff command
  2. Ensure ruff is installed in test env
  3. Verify pipeline fails on lint errors
```
