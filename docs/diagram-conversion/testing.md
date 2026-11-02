# 图表转换 Testing Strategy

**Sources:** [Product Brief](product-brief.md), [Functional Specification](functional-spec.md), [Architecture Design](architecture.md).

## Projects And Verified Commands

Mermaid NG lives in the `tools/mermaid-visual-editor` submodule of the worktree that includes it. Its `vscode-extension/` folder contains the extension manifest, JavaScript entry point and webview assets. Packaging that folder creates the VSIX; there is no separate compile step or test runner in the inspected version. Use a clean or explicitly identified submodule revision so a test result can be tied to its source.

The following command forms were run successfully against submodule revision `8f9bbc90f9f33a13cb5e2eda44100856795c4c01`. Run packaging from `tools/mermaid-visual-editor/vscode-extension/`; replace `<absolute-test-path>` with a disposable path. `--offline` works when `@vscode/vsce` is already in the npm cache; on a fresh machine, obtain that package from npm first.

```powershell
npm exec --offline --yes --package=@vscode/vsce -- vsce package --allow-missing-repository --out '<absolute-test-path>\mermaid-ng.vsix'
code --user-data-dir '<absolute-test-path>\profile' --extensions-dir '<absolute-test-path>\extensions' --install-extension '<absolute-test-path>\mermaid-ng.vsix'
code --user-data-dir '<absolute-test-path>\profile' --extensions-dir '<absolute-test-path>\extensions' --list-extensions --show-versions
code --new-window --user-data-dir '<absolute-test-path>\profile' --extensions-dir '<absolute-test-path>\extensions' '<absolute-test-path>\smoke.mmd'
```

Verify that the extension list contains the package ID and expected version before UI testing. Keep the test profile separate from the user's ordinary VS Code profile. Installing the same VSIX into the ordinary profile is a separate, explicit deployment step; verify it with `code --list-extensions --show-versions`.

## Test Levels And Oracles

- **Package and installation:** A successful VSIX command, an install success response, and the expected ID/version in VS Code's extension list establish that the artifact can be deployed. They do not establish that its editor works.
- **Extension integration:** Use a disposable `.mmd` or Markdown file in a real VS Code window. Confirm the Mermaid NG command opens its webview, the diagram renders, a visual edit changes the Mermaid text, saving writes the expected file, and reopening shows the saved result. Compare the source text and visible diagram; do not infer success from the command exit code alone. This is the minimum real editor boundary for [FS-EDT-003/004](functional-spec.md#fs-edt-mermaid-编辑器).
- **Repeatable UI smoke path:** Open the disposable `.mmd` file in VS Code, run `Mermaid NG: Open Mermaid Diagrams from File` from the Command Palette, click `Process box` in the palette, and confirm a new node and declaration appear. Click `Save`, read the source file, close the Mermaid webview, run the same command again, and confirm the node still appears. This path was exercised in VS Code 1.144.0 with Mermaid NG 2.5.0 on 2026-10-29.
- **Layout and swimlanes:** For changes to rendering, layout or drag behavior, check the visible canvas and saved Mermaid text after reopening. Preserve node identity, lane membership and positions according to [FS-EDT-002/007](functional-spec.md#fs-edt-mermaid-编辑器). Use a flowchart and a native swimlane diagram; package installation alone cannot cover these contracts.
- **Confluence integration:** Use the authorized Atlassian MCP with a disposable composite page and Whiteboard. Compare retrieved page content, editable shapes, identity and remote revision markers with the local source. Keep this separate from VS Code installation checks; the tenant capabilities remain unverified in the [architecture open decisions](architecture.md#open-decisions).

## Environment And Evidence

- Before UI actions, confirm that the desktop tool can activate the exact VS Code test window, capture its actual content, and send a harmless input. If activation or capture fails, record UI testing as `inconclusive`; an accessibility tree or installed extension ID alone is insufficient. Do not keep retrying the same inaccessible window.
- Treat palette click and drag-and-drop as separate gestures. A successful palette click does not establish drag-and-drop behavior; record a drag test as `inconclusive` if the desktop input tool leaves the diagram unchanged without an observable error.
- Use disposable source files and an isolated VS Code profile for repeatable UI tests. Do not use the user's open editor with unsaved work. Record the submodule revision, VSIX version, VS Code version, command results, relevant screenshots, and before/after source text in the Feature Plan or validation record, not in this strategy.
- Mock VS Code or Atlassian only for narrow parser or conversion logic. Final acceptance of webview gestures, save/reopen behavior, or Whiteboard editability requires the real boundary.

### Remote Windows UI test machine

Use the dedicated Windows EC2 instance when local desktop use would interrupt the user. Keep its security group closed to inbound traffic. For unattended runs, use a dedicated IAM identity limited to this instance, the required Systems Manager document, and the private test bucket prefixes. Protect its local credential with the operating system's user-bound encryption and keep it outside the repository. A console-based `aws login` session expires and cannot serve as the unattended credential.

1. Start the instance with `aws ec2 start-instances --instance-ids <id> --region <region>`, wait for `instance-running`, and confirm the Systems Manager node is `Online`. Run setup and file checks through `AWS-RunPowerShellScript`.
2. Package the identified source revision locally, transfer the VSIX through the private test bucket, and compare SHA256 on the instance. Install it with VS Code's `--user-data-dir`, `--extensions-dir`, and `--install-extension` options; verify `publisher.extension@version` with `--list-extensions --show-versions`. Use a disposable `.mmd` file. Keep workspace trust decisions inside that isolated profile.
3. Run UI gestures in the dedicated low-privilege Windows user's active console session. Systems Manager commands run as `SYSTEM` in session 0, so they cannot establish a UI result by themselves. Start a scheduled task with `LogonType Interactive` for the test user; perform a related sequence of keystrokes or clicks and capture the screen within the same task to preserve focus. First verify the session is active and a screenshot shows the actual VS Code window.
4. Capture with `Graphics.CopyFromScreen`, upload the PNG to the private bucket using the instance role's limited `s3:PutObject` permission, and inspect the downloaded image. Pair the image with the `.mmd` file read through Systems Manager. For a save/reopen check, close and reopen the webview before the final screenshot.
5. In a cleanup step even after test failure, stop the instance with `aws ec2 stop-instances` and wait for `instance-stopped`. Remove temporary transfer objects and retain only the evidence needed for the validation record. Stopping ends compute charges; EBS and retained bucket objects still consume storage.

The test user's auto-logon uses a random password stored as a Windows LSA secret, not a plaintext `DefaultPassword` registry value. Limit that account to the disposable test directory. Do not place account IDs, keys, passwords, signed URLs, or instance-specific paths in this document or the repository.

## Cadence And Independent Review

- While editing, run the smallest code or parser check that covers the changed behavior. At a delivery boundary, rebuild the VSIX and repeat the affected real VS Code flow. After changes to bundled Mermaid, webview controls, file writeback or geometry storage, repeat the flowchart and swimlane save/reopen checks on the final tree.
- An independent review is warranted when the change can silently alter diagram meaning, lane membership, saved geometry, remote Whiteboard identity, or overwrite detection. The reviewer checks source and observed results; a green packaging command is not a substitute for UI or Confluence evidence.

## Open Decisions

- The product owner has not set performance or fidelity budgets. Measurement methods and thresholds should be added only after the owning requirement and architecture define what matters.
