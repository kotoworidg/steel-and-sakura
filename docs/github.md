# GitHub publishing notes

The local `origin` is set to the user-provided URL:
`https://github.com/kotoworidg/steel-and-sakura.git`.

The GitHub connector is authenticated as `kotoworidg`, but its repository API
returned 404 for this URL and listed no accessible repositories. Repository
visibility and write access could not be verified. No commits have been
created or pushed as of the initial access check. The project remains linked
locally to the supplied URL. A local source commit was created on
2026-10-20. A renewed GitHub repository lookup still returned 404, so no push
was attempted; remote publishing needs access verification.

The repository ignore rules exclude local backups, decoded/extracted game
tables, generated `.pack` files, tool binaries, and RPFM configuration. Keep
those local. The tracked project files are scripts and documentation; the
current infantry source JSON is generated from the installed game tables and
is intentionally excluded from publication.

Before publishing, review the tracked file list with `git status --short` and
check that the repository's visibility fits the intended audience.
