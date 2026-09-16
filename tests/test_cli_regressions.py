"""Regression tests for the three faults fixed in 3.2.4.

Each of these shipped. The first two broke the website's bots and CI. The third
left `archive check-format` blind to the site's "videos" buttons: a label
missing from its map is not checked at all, so a wrong class there passed.
"""

from unittest.mock import MagicMock, patch

import pytest

from magmascript import cli
from magmascript.cli import COMMANDS, main
from magmascript.domains.archive import ArchiveClient
from magmascript.domains.scores.tools import PlayerStats, ScoresReport


class TestDomainRegistration:
    """3.2.2 and 3.2.3: every domain command was "Unknown domain".

    Registration ran only `if not COMMANDS`, and the built-in commands had
    started registering themselves at import, so the table was never empty.
    """

    def test_builtins_are_registered_at_import(self):
        # The precondition that exposed the bug. If this stops holding, the
        # test below no longer exercises it.
        assert "run" in COMMANDS

    @pytest.mark.parametrize("domain", ["archive", "mb", "lastfm", "scores", "search"])
    def test_domain_commands_are_reachable(self, domain, capsys):
        with patch("sys.argv", ["magmascript", domain, "--help"]):
            try:
                main()
            except SystemExit:
                pass
        assert "Unknown domain" not in capsys.readouterr().err
        assert domain in COMMANDS
        assert cli._DOMAINS_REGISTERED


class TestScoresReportPostDiscussion:
    """Every release: `scores report --post-discussion` raised NameError.

    cli.py called datetime.now() without importing datetime, so the report
    printed and the Discussion was never posted.
    """

    def test_posts_with_a_dated_title(self, capsys):
        client = MagicMock()
        client.report.return_value = ScoresReport(
            generated_at="September 16, 2026",
            total_games=0,
            total_scores=0,
            scoreboards=[],
            player_stats=[PlayerStats(name="JAM", total_entries=1, games_played=1)],
        )
        gh = MagicMock()
        gh.create_discussion.return_value = "https://example.invalid/discussions/1"

        with patch("magmascript.core.config.get_config"), \
             patch("magmascript.domains.gh.GHClient", return_value=gh):
            cli._dispatch_scores("report", ["--post-discussion"], client, "table")

        title, body, category = gh.create_discussion.call_args.args
        assert title.startswith("Weekly High Scores — 20")
        assert "# Weekly High Scores" in body
        assert category == "high-scores"
        gh.close.assert_called_once()


class TestArchiveVideosLabel:
    """The site renamed the artist "music videos" pages to "videos" (website
    53dc9606). With the old map, "videos" was not a known label, so the checker
    skipped those buttons -- 34 of them on the site at the time -- and the
    mismatch below went unreported."""

    CSS = ".nav-card.c-videos { color: red; }\n.nav-card.c-music-videos { color: red; }\n"

    def _page(self, tmp_path, cls):
        artist = tmp_path / "archive" / "by-artist" / "someone"
        artist.mkdir(parents=True)
        (artist / "someone-shared.css").write_text(self.CSS, encoding="utf-8")
        (artist / "about.html").write_text(
            '<div class="sub-nav">\n'
            '    <a href="./" class="nav-card c-back">← back</a>\n'
            f'    <a href="videos.html" class="nav-card {cls}">videos</a>\n'
            '</div>\n',
            encoding="utf-8",
        )
        return ArchiveClient(project_root=tmp_path)

    def test_videos_link_with_videos_class_is_clean(self, tmp_path):
        assert self._page(tmp_path, "c-videos").check_format() == []

    def test_videos_link_with_old_class_warns(self, tmp_path):
        warnings = self._page(tmp_path, "c-music-videos").check_format()
        assert len(warnings) == 1
        assert "expected c-videos" in warnings[0].msg
