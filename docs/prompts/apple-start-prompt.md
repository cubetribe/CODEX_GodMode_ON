# Apple Start Prompt

Use this for SwiftUI work on macOS and iOS.

These prompts assume the global install has already been applied.

## Prompt

```text
$godmode-workflow
$apple-platforms

Goal: <goal>

Context:
- <target app, scheme, directory, platform scope, or validation command>

Done when:
- <what finished looks like>
```

## Best for

- SwiftUI view work
- shared macOS and iOS UI flows
- state ownership and data-flow refactors
- Apple-platform validation work with `xcodebuild`

## Optional extras

- target app, scheme, or directory
- expected platform such as `macOS`, `iOS`, or both
- required validation command such as `xcodebuild build` or `xcodebuild test`
- add `$godmode-debug` or `$godmode-review` if the run is primarily debugging or assessment rather than implementation
- any release, versioning, or governance docs that the change must obey
