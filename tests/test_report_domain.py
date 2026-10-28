import pytest

from vyasa.domain.report import (
    EXAMPLE,
    INVALID,
    PATH,
    PRESENT,
    SECTIONS,
    ReportLimits,
    read_report,
    report_template,
)


def names(result):
    return [section.name for section in result.sections]


def test_the_example_reads_clean():
    result = read_report(EXAMPLE, ReportLimits())
    assert result.status == PRESENT
    assert names(result) == [name for name, _ in SECTIONS]
    assert result.dropped == ()


def test_the_template_matches_the_definition_and_limits():
    template = report_template(ReportLimits(512, 32), "index")
    assert template["path"] == PATH == ".vyasa/project-report.md"
    assert template["limits"] == {"max_file_bytes": 512 * 1024, "max_section_bytes": 32 * 1024, "source": "index"}
    assert [s["name"] for s in template["sections"]] == [name for name, _ in SECTIONS]
    assert template["example"] == EXAMPLE
    assert all(isinstance(rule, str) for rule in template["rules"])


def test_the_default_template_says_where_the_limits_come_from():
    assert report_template()["limits"]["source"] == "default"


def test_rules_forbid_guessing_and_secrets():
    rules = " ".join(report_template()["rules"]).lower()
    assert "omit" in rules and "credential" in rules and "repository" in rules


def test_unknown_heading_is_dropped_with_a_reason():
    result = read_report("## Overview\nHi\n\n## Gossip\nno\n", ReportLimits())
    assert names(result) == ["Overview"]
    assert result.dropped == (("Gossip", "is not a section of the template"),)


def test_heading_match_ignores_case_and_spacing():
    result = read_report("##   overview  \nHi\n", ReportLimits())
    assert names(result) == ["Overview"]


def test_duplicate_heading_keeps_the_first():
    result = read_report("## Overview\nfirst\n## Overview\nsecond\n", ReportLimits())
    assert result.sections[0].text == "first"
    assert result.dropped == (("Overview", "appears more than once"),)


def test_section_over_the_limit_is_dropped_naming_the_limit():
    body = "x" * 2000
    result = read_report(f"## Overview\n{body}\n## Architecture\nsmall\n", ReportLimits(16, 1))
    assert names(result) == ["Architecture"]
    assert result.dropped == (("Overview", "is larger than 1 KiB"),)


def test_credential_url_drops_only_that_section():
    result = read_report("## Overview\nsee https://user:secret@host/x\n## Architecture\nfine\n", ReportLimits())
    assert names(result) == ["Architecture"]
    assert result.dropped == (("Overview", "contains a URL with credentials"),)


def test_control_characters_are_stripped_but_newlines_and_tabs_stay():
    result = read_report("## Overview\na\x00b\x1b[31m\tc\nd\x7f\n", ReportLimits())
    assert result.sections[0].text == "ab[31m\tc\nd"


def test_headings_inside_code_fences_do_not_split_sections():
    text = "## Overview\n```\n## not a heading\n```\nafter\n"
    result = read_report(text, ReportLimits())
    assert names(result) == ["Overview"]
    assert "## not a heading" in result.sections[0].text
    assert result.dropped == ()


def test_text_before_the_first_heading_is_ignored():
    result = read_report("# Title\nintro\n## Overview\nHi\n", ReportLimits())
    assert names(result) == ["Overview"]
    assert result.dropped == ()


def test_empty_section_is_dropped():
    result = read_report("## Overview\n\n\n## Architecture\nx\n", ReportLimits())
    assert names(result) == ["Architecture"]
    assert result.dropped == (("Overview", "is empty"),)


def test_sections_come_back_in_template_order_with_sizes():
    result = read_report("## Architecture\nbb\n## Overview\na\n", ReportLimits())
    assert names(result) == ["Overview", "Architecture"]
    assert [s.size for s in result.sections] == [1, 2]


def test_a_report_with_no_known_section_is_present_but_empty():
    result = read_report("just words\n", ReportLimits())
    assert result.status == PRESENT and result.sections == ()


@pytest.mark.parametrize("text", ["", "\n\n"])
def test_blank_text_is_present_but_empty(text):
    assert read_report(text, ReportLimits()).sections == ()


def test_the_hash_is_carried():
    assert read_report("## Overview\nx\n", ReportLimits(), content_hash="abc").content_hash == "abc"
    assert INVALID == "invalid"
