from __future__ import annotations

import site
from typing import TYPE_CHECKING, Final

from pipx.backends.pip import PipBackend
from pipx.constants import PIPX_SHARED_PTH

if TYPE_CHECKING:
    from pathlib import Path

    from pytest_mock import MockerFixture

# No single-byte code page can represent these, so a .pth written with the locale encoding fails on any
# legacy-code-page Windows install rather than only on the handful whose code page happens to miss them.
NON_ASCII_NAME: Final[str] = "用户-Пользователь"


def test_pth_file_readable_with_non_ascii_path(tmp_path: Path) -> None:
    non_ascii_path = tmp_path / NON_ASCII_NAME / "pipx" / "shared" / "site-packages"
    non_ascii_path.mkdir(parents=True)

    pth_file = tmp_path / PIPX_SHARED_PTH
    pth_file.write_text(f"{non_ascii_path}\n", encoding="utf-8")

    known_paths: set[str] = set()
    site.addpackage(str(tmp_path), pth_file.name, known_paths)

    assert str(non_ascii_path).casefold() in {p.casefold() for p in known_paths}


def test_pth_file_written_as_utf8_for_non_ascii_shared_libs(mocker: MockerFixture, tmp_path: Path) -> None:
    """A PIPX_HOME holding non-ASCII characters must not depend on the locale encoding."""
    venv_site_packages = tmp_path / NON_ASCII_NAME / "venvs" / "app" / "site-packages"
    shared_site_packages = tmp_path / NON_ASCII_NAME / "shared" / "site-packages"
    for path in (venv_site_packages, shared_site_packages):
        path.mkdir(parents=True)
    mocker.patch("pipx.backends.pip.run_subprocess")
    mocker.patch("pipx.backends.pip.subprocess_post_check")
    mocker.patch("pipx.backends.pip.get_venv_paths", return_value=(None, venv_site_packages, None))
    mocker.patch("pipx.backends.pip.get_site_packages", return_value=venv_site_packages)
    shared = mocker.patch("pipx.backends.pip.shared_libs")
    shared.site_packages = shared_site_packages

    PipBackend().create_venv(
        tmp_path / NON_ASCII_NAME / "venvs" / "app",
        python="python",
        venv_args=[],
        pip_args=[],
        include_pip=False,
        verbose=True,
    )

    # site.addpackage decodes .pth files as UTF-8 first, so assert the bytes on disk, not the text a
    # matching locale would happen to give back. Newlines stay untested: text mode translates them.
    pth_file = venv_site_packages / PIPX_SHARED_PTH
    assert pth_file.read_bytes().decode("utf-8").strip() == str(shared_site_packages)
