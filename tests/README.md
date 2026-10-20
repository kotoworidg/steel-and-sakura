# Validation tests

Run `python -m unittest discover -s tests -p 'test_*.py'` for offline regression checks. `scripts/build.ps1` runs these automatically after RPFM pack validation and `scripts/validate_offline.py`. A test deliberately corrupts a temporary soldier count and requires the validator to reject it. No game runtime test has been performed.
