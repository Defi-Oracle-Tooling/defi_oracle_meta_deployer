import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
from click.testing import CliRunner
from azure_region_validator.cli import main

def test_cli():
    runner = CliRunner()
    result = runner.invoke(main, ['--subscription-id', 'test-sub', '--config-file', 'path/to/config.json'], prog_name='cli')
    assert result.exit_code == 0