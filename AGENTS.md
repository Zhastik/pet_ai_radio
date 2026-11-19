# Repository Guidelines

## Project Structure

`ai_radio` is an empty workspace. As code is added, group related modules together and give tests clear names that identify the feature they cover. Use the chosen framework’s directory conventions. Document the application entry point, test locations, and any checked-in assets or fixtures in the README so contributors can find them.

## Build, Test, and Development

When you add tooling, document the exact commands for installing dependencies, running locally, building, and testing. Run each documented command from a clean checkout to verify its prerequisites. Include any required runtime version and configuration setup. Once Git is initialized, run `git status --short` to check which files your change touched.

## Coding Style and Testing

Follow the language’s standard formatter and the naming conventions in nearby code. If you introduce a formatter or linter, check in its configuration and document how to run it. Name tests after the behavior they verify and use the test runner’s discovery conventions. For a bug fix, add a regression test that fails before the fix and passes afterward. Keep fixtures small and deterministic.

## Commits and Pull Requests

Use short, imperative commit subjects such as `Add local playback settings`. In a pull request, explain what changed and why, list the checks you ran, and link the related issue when one exists. Include screenshots for visible interface changes when they help reviewers understand the change. Mention new setup steps or configuration values that affect other contributors.
