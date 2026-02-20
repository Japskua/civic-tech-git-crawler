OSI_APPROVED_SPDX_IDS: frozenset[str] = frozenset({
    "0BSD", "AAL", "AFL-3.0", "AGPL-3.0-only", "AGPL-3.0-or-later",
    "Apache-2.0", "APSL-2.0", "Artistic-2.0", "BlueOak-1.0.0",
    "BSD-1-Clause", "BSD-2-Clause", "BSD-2-Clause-Patent", "BSD-3-Clause",
    "BSD-3-Clause-LBNL", "BSL-1.0", "CAL-1.0", "CAL-1.0-Combined-Work-Exception",
    "CERN-OHL-P-2.0", "CERN-OHL-S-2.0", "CERN-OHL-W-2.0",
    "CNRI-Python", "CPAL-1.0", "CUA-OPL-1.0", "ECL-2.0", "EFL-2.0",
    "Entessa", "EPL-1.0", "EPL-2.0", "EUDatagrid", "EUPL-1.2",
    "Fair", "Frameworx-1.0", "FSFAP", "FTLL", "GPL-2.0-only",
    "GPL-2.0-or-later", "GPL-3.0-only", "GPL-3.0-or-later",
    "HPND", "Intel", "IPA", "IPL-1.0", "ISC", "JAM", "JSON",
    "LAL-1.3", "LGPL-2.0-only", "LGPL-2.0-or-later", "LGPL-2.1-only",
    "LGPL-2.1-or-later", "LGPL-3.0-only", "LGPL-3.0-or-later",
    "LiLiQ-P-1.1", "LiLiQ-R-1.1", "LiLiQ-Rplus-1.1", "LPL-1.0",
    "LPL-1.02", "LPPL-1.3c", "MIT", "MIT-0", "MIT-Modern-Variant",
    "Motosoto", "MPL-2.0", "MS-PL", "MS-RL", "MulanPSL-2.0",
    "Multics", "NASA-1.3", "NCSA", "NGPL", "Nokia", "NPOSL-3.0",
    "NTP", "OCLC-2.0", "OFL-1.1", "OGTSL", "OLDAP-2.8",
    "OSET-PL-2.1", "OSL-3.0", "PHP-3.01", "PostgreSQL", "PSF-2.0",
    "QPL-1.0", "RPL-1.5", "RPSL-1.0", "RSCPL", "SimPL-2.0",
    "SISSL", "Sleepycat", "SPL-1.0", "UCL-1.0", "Unicode-DFS-2016",
    "Unlicense", "UPL-1.0", "VSL-1.0", "W3C", "Watcom-1.0",
    "Xnet", "Zlib", "ZPL-2.0", "ZPL-2.1",
})


def is_osi_approved(spdx_id: str | None) -> bool:
    if spdx_id is None:
        return False
    return spdx_id in OSI_APPROVED_SPDX_IDS
