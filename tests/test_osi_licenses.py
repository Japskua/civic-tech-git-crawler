"""Tests for OSI-approved license detection.

Regression coverage for the bug where GPL/AGPL/LGPL repositories were flagged
is_osi_approved=False because the GitHub Licenses API returns deprecated SPDX
short identifiers (e.g. "GPL-3.0") while the allow-list only held the modern
disambiguated forms (e.g. "GPL-3.0-only").
"""

import pytest

from civic_tech_crawler.utils.osi_licenses import is_osi_approved


# Deprecated SPDX short identifiers as emitted by the GitHub Licenses API.
# These are the exact values observed in datasets/2026_05/repo_metrics.csv that
# were previously (incorrectly) flagged non-OSI.
GITHUB_SHORT_FORMS = ["GPL-2.0", "GPL-3.0", "AGPL-3.0", "LGPL-2.1", "LGPL-3.0"]

# Modern, disambiguated SPDX identifiers.
MODERN_FORMS = [
    "GPL-2.0-only", "GPL-2.0-or-later",
    "GPL-3.0-only", "GPL-3.0-or-later",
    "AGPL-3.0-only", "AGPL-3.0-or-later",
    "LGPL-3.0-only", "LGPL-3.0-or-later",
]

PERMISSIVE = ["MIT", "Apache-2.0", "BSD-2-Clause", "BSD-3-Clause", "ISC", "MPL-2.0"]

# Not OSI-approved (CC0 is a public-domain dedication; the rest are sentinels).
NON_OSI = ["CC0-1.0", "NOASSERTION", "Proprietary", "", None]


@pytest.mark.parametrize("spdx", GITHUB_SHORT_FORMS)
def test_github_deprecated_short_forms_are_osi(spdx):
    assert is_osi_approved(spdx) is True


@pytest.mark.parametrize("spdx", MODERN_FORMS)
def test_modern_spdx_forms_are_osi(spdx):
    assert is_osi_approved(spdx) is True


@pytest.mark.parametrize("spdx", PERMISSIVE)
def test_permissive_licenses_are_osi(spdx):
    assert is_osi_approved(spdx) is True


@pytest.mark.parametrize("spdx", NON_OSI)
def test_non_osi_values_are_rejected(spdx):
    assert is_osi_approved(spdx) is False


def test_none_does_not_raise():
    # Repositories with no detected license pass spdx_id=None.
    assert is_osi_approved(None) is False
