import pytest
from click.testing import CliRunner
from azure_region_validator.cli import main

def test_cli():
    runner = CliRunner()
    result = runner.invoke(main, ['--subscription-id', 'test-sub', '--config-file', 'path/to/config.json'])
    assert result.exit_code == 0