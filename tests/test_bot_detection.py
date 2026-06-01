import pytest

from civic_tech_crawler.collectors.person_metrics import is_bot_account


@pytest.mark.parametrize(
    "login",
    [
        "dependabot[bot]",
        "renovate[bot]",
        "github-actions[bot]",
        "pre-commit-ci[bot]",
        "codecov[bot]",
        "stale[bot]",
        "imgbot[bot]",
        "mergify[bot]",
        "allcontributors[bot]",
        "semantic-release-bot",
        "release-drafter[bot]",
    ],
)
def test_known_bot_accounts_are_detected(login):
    assert is_bot_account(login) is True


@pytest.mark.parametrize(
    "login",
    [
        "dependabot",
        "renovate",
        "github-actions",
        "snyk-bot",
        "pyup-bot",
        "weblate",
        "crowdin-bot",
        "netlify",
        "vercel",
        "sonarcloud",
        "coveralls",
        "codeclimate",
        "transifex-integration",
        "railway-app",
        "greenkeeper",
    ],
)
def test_known_bot_logins_without_bracket_suffix(login):
    assert is_bot_account(login) is True


@pytest.mark.parametrize(
    "login",
    [
        "octocat",
        "torvalds",
        "japskua",
        "kentcdodds",
        "sindresorhus",
        "alice-smith",
        "bob42",
    ],
)
def test_real_human_accounts_are_not_flagged(login):
    assert is_bot_account(login) is False


def test_none_login_is_not_a_bot():
    assert is_bot_account(None) is False


def test_empty_string_is_not_a_bot():
    assert is_bot_account("") is False


def test_bracket_suffix_is_case_insensitive():
    assert is_bot_account("Dependabot[Bot]") is True
    assert is_bot_account("renovate[BOT]") is True


def test_username_ending_in_bot_word_is_flagged():
    # The pattern matches logins ending in literal "Bot" (case-insensitive)
    # or hyphen-bot suffixes — common bot naming conventions.
    assert is_bot_account("my-ci-bot") is True
    assert is_bot_account("release-bot-internal") is True


def test_username_containing_robot_substring_is_not_falsely_flagged():
    # We don't want substrings like "robot" or "bottle" tripping the matcher
    # for legitimate humans whose names happen to contain "bot".
    assert is_bot_account("robotic-user") is False
    assert is_bot_account("bottle-collector") is False


def test_unrelated_hyphenated_username_is_not_a_bot():
    assert is_bot_account("data-engineer") is False
    assert is_bot_account("john-doe") is False
