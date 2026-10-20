# Validation tests

Run `python -m unittest discover -s tests -p 'test_*.py'` for offline regression checks. `scripts/build.ps1` runs these automatically after RPFM pack validation and `scripts/validate_offline.py`. The three tests include deliberate soldier-count and localization-key corruption cases. No game runtime test has been performed.
