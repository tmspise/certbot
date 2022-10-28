"""Tests for certbot.compat.filesystem"""
import unittest
import tempfile
import os
import stat
import shutil

try:
    import mock
except ImportError: # pragma: no cover
    from unittest import mock # type: ignore

from certbot.compat import filesystem


def get_file_mode(path: str) -> int:
    """Returns the permissions section of the file mode"""
    stat_result = os.stat(path)
    return stat.S_IMODE(stat_result.st_mode)


class MakedirsTest(unittest.TestCase):
    """Tests for filesystem.makedirs"""
    def setUp(self) -> None:
        self.temp_dir = tempfile.mkdtemp("tmp")
        self.current_umask = os.umask(0)
        os.umask(self.current_umask)
        super().setUp()
    
    def tearDown(self) -> None:
        os.umask(self.current_umask) # Reset to the umask we were using prior to testing
        shutil.rmtree(self.temp_dir)
        super().tearDown()

    def _run_test_with_umask(self, umask: int) -> None:
        desired_mode = 0o755
        intermediate_path = os.path.join(self.temp_dir, "intermediate")
        full_path = os.path.join(intermediate_path, "leaf")
        os.umask(umask)
        filesystem.makedirs(full_path, desired_mode)
        self.assertEqual(get_file_mode(intermediate_path), desired_mode)
        self.assertEqual(get_file_mode(full_path), desired_mode)
        self.assertEqual(os.umask(0), umask)

    def test_with_permissive_umask(self) -> None:
        self._run_test_with_umask(0o0022)

    def test_with_strict_umask(self) -> None:
        self._run_test_with_umask(0o0027)


if __name__ == "__main__":
    unittest.main()  # pragma: no cover