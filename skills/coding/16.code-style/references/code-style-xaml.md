# XAML Code-Style Decisions

Read this reference only when XAML is a confirmed language for the project.

## Evidence

- the UI framework (WPF, WinUI, Avalonia, or MAUI) and its resource-dictionary
  merge syntax;
- `App.xaml` and its merged dictionaries;
- existing `Styles/` folders and resource dictionaries.

All of these are read-only evidence for `define`.

## Owner Default

Use these unless the user or a project document says otherwise:

- Views hold layout only.
- View-specific styles live in one resource dictionary per view, for example
  `Styles/ExportView.xaml`, merged by that view.
- Shared styles live in `Styles/Shared.xaml`, merged by `App.xaml`.

## Apply Cautions

- Moving a style can change resource lookup: merge order, implicit
  `TargetType` styles, and `StaticResource` order.
- Style extraction is structural work for a strong model or the orchestrating
  session, never for a cheap model.
- Verify by build and, when available, by opening the view. Otherwise report
  that visual behavior is unverified.

## Placement

| Finding | Destination |
|---|---|
| A decided layout, style, or resource rule | The XAML section of `docs/code-style.md`, or of a project file when only that project uses the rule |
| A rule that applies to every language | The cross-language sections of `docs/code-style.md` |
| Unknown or conflicting evidence | Ask, or omit and report |
