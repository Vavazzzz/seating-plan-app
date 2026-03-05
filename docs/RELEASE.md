# Release Workflow

This document describes steps to prepare a new release for the Seating Plan Application.

1. **Bump Version**
   - Update the `version` field in `pyproject.toml` to the next semantic version, e.g., `1.1.9`.

2. **Update CHANGELOG**
   - Add an entry under the new version header in `CHANGELOG.md` (create the file if missing).
   - Include a summary of new features, bug fixes, and breaking changes.

3. **Update README Release Notes**
   - Add a bullet list under the "Release Notes (latest)" section.

4. **Run Tests**
   ```bash
   python -m pytest -q
   ```
   All tests should pass before proceeding.

5. **Commit Changes**
   ```bash
   git add pyproject.toml CHANGELOG.md README.md
   git commit -m "Bump version to x.y.z"
   ```

6. **Tag the Release**
   ```bash
   git tag -a v1.1.9 -m "Release v1.1.9"
   git push origin main --tags
   ```

7. **Build Artifacts** (optional)
   - Use PyInstaller spec or other packaging tools to generate executables.
   - Upload to GitHub releases or distribution channel.

8. **Publish Documentation**
   - Merge documentation updates to `main` and verify on GitHub pages if used.

9. **Notify Users**
   - Announce release via project channels, update repository description, etc.

An example for a minor release:
```
# Bump to 1.1.9
sed -i "s/version = \"1.1.8\"/version = \"1.1.9\"/" pyproject.toml
# Add changelog entry
# Commit
# Tag
```
