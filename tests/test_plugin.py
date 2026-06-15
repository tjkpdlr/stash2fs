"""Plugin runtime tests."""

import json
from io import StringIO
from unittest.mock import patch

from stash2fs.plugin.runtime import main


def test_hook_disabled_noop() -> None:
    fragment = {
        "server_connection": {
            "Scheme": "http",
            "Host": "0.0.0.0",
            "Port": 9999,
            "SessionCookie": {"Value": "test"},
            "PluginDir": "/tmp/stash2fs",
        },
        "args": {
            "hookContext": {"id": "100", "type": "Scene"},
        },
    }

    with (
        patch("stash2fs.plugin.runtime.read_fragment", return_value=fragment),
        patch("stash2fs.plugin.runtime.HttpStashClient") as mock_client_cls,
    ):
        client = mock_client_cls.return_value
        client.get_plugin_settings.return_value = {"enabled": False}
        client.find_scene.return_value = None
        with patch("sys.stdin", StringIO(json.dumps(fragment))):
            main()
        client.find_scene.assert_not_called()


def test_enable_task() -> None:
    fragment = {
        "server_connection": {
            "Scheme": "http",
            "Host": "localhost",
            "Port": 9999,
            "SessionCookie": {"Value": "test"},
            "PluginDir": "/tmp/stash2fs",
        },
        "args": {"mode": "enable"},
    }

    with (
        patch("stash2fs.plugin.runtime.read_fragment", return_value=fragment),
        patch("stash2fs.plugin.runtime.HttpStashClient") as mock_client_cls,
    ):
        client = mock_client_cls.return_value
        client.get_plugin_settings.return_value = {}
        main()
        client.set_plugin_setting.assert_called_once()
