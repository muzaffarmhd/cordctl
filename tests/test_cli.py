import pytest
from click.testing import CliRunner
from cordctl.cli import main 

def test_cli_invokes_without_error():
    runner = CliRunner()
    result = runner.invoke(main)
    assert result.exit_code == 0

def test_cli_help_works():
    runner = CliRunner()
    result = runner.invoke(main, ['--help'])
    assert result.exit_code == 0
    assert "Usage: main [OPTIONS] COMMAND [ARGS]..." in result.output
    assert "cordctl CLI - Discord Server Management Tool" in result.output