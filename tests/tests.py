import unittest
from typing import Dict
from unittest.mock import patch, Mock, call, mock_open
from cgmerger.cgmerge import main


class TestException(Exception):
    pass


class TestExitException(Exception):
    pass


def path_exists_wrapper(paths: Dict[str, bool]):
    def real_path_exists(path: str):
        return paths.get(path, False)

    return real_path_exists


class FileDoesntExist(unittest.TestCase):
    def raise_exception(self, message):
        raise TestException(message)

    def raise_exit_exception(self, message):
        raise TestExitException(message)

    def get_default_args(self):
        args_mock = Mock()
        args_mock.file_regex = None
        args_mock.exclude_line_regex = None
        args_mock.output = None
        args_mock.workdir = None
        args_mock.basedir = "./"
        args_mock.header = None
        args_mock.footer = None
        args_mock.comment = None
        args_mock.order = None
        args_mock.write = False
        args_mock.debug = False
        args_mock.separator_start = None
        args_mock.separator_end = None
        args_mock.separator_length = None
        return args_mock

    def get_default_setup(self, parser):
        args_mock = self.get_default_args()
        parser.error = self.raise_exception
        parser.exit = self.raise_exit_exception
        parser.parse_args.return_value = args_mock

        return args_mock, parser

    @patch("cgmerger.cgmerge.parser")
    @patch("cgmerger.cgmerge.os.path.isfile")
    def test_debug_printout(self, path_exists, parser):
        path_exists.return_value = False
        args_mock, _ = self.get_default_setup(parser)
        args_mock.debug = True

        with self.assertRaisesRegex(
            TestExitException, "No further operations will be performed"
        ):
            main()

    @patch("cgmerger.cgmerge.parser")
    @patch("cgmerger.cgmerge.os.path.isfile")
    def test_default_output_file_doesnt_exist(self, path_exists, parser):
        path_exists.return_value = False
        self.get_default_setup(parser)
        with self.assertRaisesRegex(
            TestException, 'No "./codingame.volatile.py" file present in '
        ):
            main()

    @patch("cgmerger.cgmerge.parser")
    @patch("cgmerger.cgmerge.os.path.isfile")
    def test_custom_basedir(self, path_exists, parser):
        path_exists.return_value = False
        args_mock, _ = self.get_default_setup(parser)
        args_mock.basedir = "/one/two/three/"
        with self.assertRaisesRegex(
            TestException,
            'No "{}codingame.volatile.py" file present in {}'.format(
                args_mock.basedir, args_mock.basedir
            ),
        ):
            main()

    @patch("cgmerger.cgmerge.parser")
    @patch("cgmerger.cgmerge.os.path.exists")
    def test_custom_output_file_doesnt_exist(self, path_exists, parser):
        path_exists.return_value = False
        args_mock, _ = self.get_default_setup(parser)
        args_mock.output = "very_custom_file.py"
        with self.assertRaisesRegex(
            TestException, 'No "./{}" file present in '.format(args_mock.output)
        ):
            main()

    @patch("cgmerger.cgmerge.parser")
    @patch("cgmerger.cgmerge.os.path.isfile")
    @patch("cgmerger.cgmerge.os.path.isdir")
    def test_default_workdir_doesnt_exist(self, is_dir, path_exists, parser):
        path_exists.return_value = True
        is_dir.return_value = False
        self.get_default_setup(parser)
        with self.assertRaisesRegex(
            TestException, 'No "codingame/" directory present in '
        ):
            main()

    @patch("cgmerger.cgmerge.parser")
    @patch("cgmerger.cgmerge.os.path.isfile")
    @patch("cgmerger.cgmerge.os.path.isdir")
    def test_custom_workdir_doesnt_exist(self, is_dir, path_exists, parser):
        path_exists.return_value = True
        is_dir.return_value = False
        args_mock, _ = self.get_default_setup(parser)
        args_mock.workdir = "very_custom_folder/"
        with self.assertRaisesRegex(
            TestException, 'No "{}" directory present in '.format(args_mock.workdir)
        ):
            main()

    @patch("cgmerger.cgmerge.parser")
    @patch("cgmerger.cgmerge.os.path.isfile")
    @patch("cgmerger.cgmerge.os.path.isdir")
    @patch("cgmerger.cgmerge.os.listdir")
    @patch("cgmerger.cgmerge.open")
    def test_create_default_output(self, open, listdir, is_dir, path_exists, parser):
        path_exists.return_value = True
        is_dir.return_value = True
        listdir.return_value = []
        self.get_default_setup(parser)
        main()
        open.assert_called_once_with("./codingame.volatile.py", "w")

    @patch(
        "cgmerger.cgmerge.os.path.isfile",
        new=path_exists_wrapper(
            {
                "./codingame.volatile.py": True,
                "./codingame/quite_interesting_header_file.py": False,
            }
        ),
    )
    @patch("cgmerger.cgmerge.parser")
    @patch("cgmerger.cgmerge.os.path.isdir")
    def test_add_header_file_doesnt_exist(self, is_dir, parser):
        is_dir.return_value = True
        args_mock, _ = self.get_default_setup(parser)
        args_mock.header = "quite_interesting_header_file.py"
        with self.assertRaisesRegex(
            TestException,
            'No "./codingame/{}" file present in '.format(args_mock.header),
        ):
            main()

    @patch("cgmerger.cgmerge.parser")
    @patch("cgmerger.cgmerge.os.path.isfile")
    @patch("cgmerger.cgmerge.os.path.isdir")
    @patch("cgmerger.cgmerge.os.path.getsize")
    @patch("cgmerger.cgmerge.os.listdir")
    @patch("cgmerger.cgmerge.open")
    @patch("cgmerger.cgmerge.chardet.detect")
    def test_add_header_file_exists(
        self, detect, open, listdir, getsize, is_dir, path_exists, parser
    ):
        detect.return_value = {"encoding": "utf-8"}
        getsize.return_value = 1
        path_exists.return_value = True
        is_dir.return_value = True
        listdir.return_value = []
        args_mock, _ = self.get_default_setup(parser)
        args_mock.header = "quite_interesting_header_file.py"
        main()
        open.assert_has_calls(
            [
                call("./codingame.volatile.py", "w"),
                call("./codingame/quite_interesting_header_file.py", "rb"),
                call(
                    "./codingame/quite_interesting_header_file.py",
                    "r",
                    encoding="utf-8",
                ),
            ],
            any_order=True,
        )

    @patch(
        "cgmerger.cgmerge.os.path.isfile",
        new=path_exists_wrapper(
            {
                "./codingame.volatile.py": True,
                "./codingame/quite_interesting_footer_file.py": False,
            }
        ),
    )
    @patch("cgmerger.cgmerge.parser")
    @patch("cgmerger.cgmerge.os.path.isdir")
    def test_add_footer_file_doesnt_exist(self, is_dir, parser):
        is_dir.return_value = True
        args_mock, _ = self.get_default_setup(parser)
        args_mock.footer = "quite_interesting_footer_file.py"
        with self.assertRaisesRegex(
            TestException,
            'No "./codingame/{}" file present in '.format(args_mock.footer),
        ):
            main()

    @patch("cgmerger.cgmerge.parser")
    @patch("cgmerger.cgmerge.os.path.isfile")
    @patch("cgmerger.cgmerge.os.path.isdir")
    @patch("cgmerger.cgmerge.os.path.getsize")
    @patch("cgmerger.cgmerge.os.listdir")
    @patch("cgmerger.cgmerge.open")
    @patch("cgmerger.cgmerge.chardet.detect")
    def test_add_footer_file_exists(
        self, detect, open, listdir, getsize, is_dir, path_exists, parser
    ):
        detect.return_value = {"encoding": "utf-8"}
        getsize.return_value = 1
        path_exists.return_value = True
        is_dir.return_value = True
        listdir.return_value = []
        args_mock, _ = self.get_default_setup(parser)
        args_mock.footer = "quite_interesting_footer_file.py"
        main()
        open.assert_has_calls(
            [
                call("./codingame.volatile.py", "w"),
                call("./codingame/quite_interesting_footer_file.py", "rb"),
                call(
                    "./codingame/quite_interesting_footer_file.py",
                    "r",
                    encoding="utf-8",
                ),
            ],
            any_order=True,
        )

    @patch("cgmerger.cgmerge.parser")
    @patch("cgmerger.cgmerge.os.path.isfile")
    @patch("cgmerger.cgmerge.os.path.isdir")
    @patch("cgmerger.cgmerge.os.path.getsize")
    @patch("cgmerger.cgmerge.os.listdir")
    @patch("cgmerger.cgmerge.chardet.detect")
    def test_add_file(self, detect, listdir, getsize, is_dir, path_exists, parser):
        open = mock_open(Mock(), read_data="One\nTwo\nThree")
        detect.return_value = {"encoding": "utf-8"}
        getsize.return_value = 1
        path_exists.return_value = True
        is_dir.return_value = True
        listdir.return_value = ["merge_me.py"]
        self.get_default_setup(parser)
        with patch("cgmerger.cgmerge.open", open):
            main()
        open.assert_has_calls(
            [
                call("./codingame.volatile.py", "w"),
                call("./codingame/merge_me.py", "rb"),
                call("./codingame/merge_me.py", "r", encoding="utf-8"),
                call().write(
                    '\n# file "codingame/merge_me.py" -------------------------------------------------\n'
                ),
                call().write("One\n"),
                call().write("Two\n"),
                call().write("Three"),
                call().write(
                    '\n\n\n# end of file "codingame/merge_me.py" ==========================================\n'
                ),
            ],
            any_order=True,
        )

    @patch("cgmerger.cgmerge.parser")
    @patch("cgmerger.cgmerge.os.path.isfile")
    @patch("cgmerger.cgmerge.os.path.isdir")
    @patch("cgmerger.cgmerge.os.path.getsize")
    @patch("cgmerger.cgmerge.os.listdir")
    @patch("cgmerger.cgmerge.open")
    @patch("cgmerger.cgmerge.chardet.detect")
    def test_add_header(
        self, detect, open, listdir, getsize, is_dir, path_exists, parser
    ):
        detect.return_value = {"encoding": "utf-8"}
        getsize.return_value = 1
        path_exists.return_value = True
        is_dir.return_value = True
        listdir.return_value = []
        self.get_default_setup(parser)
        args_mock, _ = self.get_default_setup(parser)
        args_mock.order = "one.py,two.py,three.py"

        main()
        open.assert_has_calls(
            [
                call("./codingame.volatile.py", "w"),
                call("./codingame/one.py", "rb"),
                call("./codingame/one.py", "r", encoding="utf-8"),
                call("./codingame/two.py", "rb"),
                call("./codingame/two.py", "r", encoding="utf-8"),
                call("./codingame/three.py", "rb"),
                call("./codingame/three.py", "r", encoding="utf-8"),
            ],
            any_order=True,
        )

    @patch("cgmerger.cgmerge.parser")
    @patch("cgmerger.cgmerge.os.path.isfile")
    @patch("cgmerger.cgmerge.os.path.isdir")
    @patch("cgmerger.cgmerge.os.path.getsize")
    @patch("cgmerger.cgmerge.os.listdir")
    @patch("cgmerger.cgmerge.chardet.detect")
    def test_order_footer_header_files(
        self, detect, listdir, getsize, is_dir, path_exists, parser
    ):
        open = mock_open(Mock(), read_data="One\nTwo\nThree")
        detect.return_value = {"encoding": "utf-8"}
        getsize.return_value = 1
        path_exists.return_value = True
        is_dir.return_value = True
        listdir.return_value = ["merge_me.py", "two.py"]
        args_mock, _ = self.get_default_setup(parser)
        args_mock.order = "one.py,two.py,three.py"
        args_mock.header = "three.py"
        args_mock.footer = "one.py"
        with patch("cgmerger.cgmerge.open", open):
            main()

        calls = list(
            filter(
                lambda line: line != call().__enter__()
                and line != call().__exit__(None, None, None)
                and line != call().read(1)
                and line != call().readlines(),
                open.mock_calls,
            )
        )
        self.assertListEqual(
            calls,
            [
                call("./codingame.volatile.py", "w"),
                call("./codingame/three.py", "rb"),
                call("./codingame/three.py", "r", encoding="utf-8"),
                call().write("One\n"),
                call().write("Two\n"),
                call().write("Three"),
                call("./codingame/two.py", "rb"),
                call("./codingame/two.py", "r", encoding="utf-8"),
                call().write(
                    '\n# file "codingame/two.py" ------------------------------------------------------\n'
                ),
                call().write("One\n"),
                call().write("Two\n"),
                call().write("Three"),
                call().write(
                    '\n\n\n# end of file "codingame/two.py" ===============================================\n'
                ),
                call("./codingame/merge_me.py", "rb"),
                call("./codingame/merge_me.py", "r", encoding="utf-8"),
                call().write(
                    '\n# file "codingame/merge_me.py" -------------------------------------------------\n'
                ),
                call().write("One\n"),
                call().write("Two\n"),
                call().write("Three"),
                call().write(
                    '\n\n\n# end of file "codingame/merge_me.py" ==========================================\n'
                ),
                call("./codingame/one.py", "rb"),
                call("./codingame/one.py", "r", encoding="utf-8"),
                call().write("One\n"),
                call().write("Two\n"),
                call().write("Three"),
            ],
        )

    @patch("cgmerger.cgmerge.parser")
    @patch("cgmerger.cgmerge.os.path.isfile")
    @patch("cgmerger.cgmerge.os.path.isdir")
    @patch("cgmerger.cgmerge.os.path.getsize")
    @patch("cgmerger.cgmerge.os.listdir")
    @patch("cgmerger.cgmerge.chardet.detect")
    def test_footer_header_files(
        self, detect, listdir, getsize, is_dir, path_exists, parser
    ):
        open = mock_open(Mock(), read_data="One\nTwo\nThree")
        detect.return_value = {"encoding": "utf-8"}
        getsize.return_value = 1
        path_exists.return_value = True
        is_dir.return_value = True
        listdir.return_value = ["one.py", "two.py", "three.py"]
        args_mock, _ = self.get_default_setup(parser)
        args_mock.header = "three.py"
        args_mock.footer = "one.py"
        with patch("cgmerger.cgmerge.open", open):
            main()

        calls = list(
            filter(
                lambda line: line != call().__enter__()
                and line != call().__exit__(None, None, None)
                and line != call().read(1)
                and line != call().readlines(),
                open.mock_calls,
            )
        )
        self.assertListEqual(
            calls,
            [
                call("./codingame.volatile.py", "w"),
                call("./codingame/three.py", "rb"),
                call("./codingame/three.py", "r", encoding="utf-8"),
                call().write("One\n"),
                call().write("Two\n"),
                call().write("Three"),
                call("./codingame/two.py", "rb"),
                call("./codingame/two.py", "r", encoding="utf-8"),
                call().write(
                    '\n# file "codingame/two.py" ------------------------------------------------------\n'
                ),
                call().write("One\n"),
                call().write("Two\n"),
                call().write("Three"),
                call().write(
                    '\n\n\n# end of file "codingame/two.py" ===============================================\n'
                ),
                call("./codingame/one.py", "rb"),
                call("./codingame/one.py", "r", encoding="utf-8"),
                call().write("One\n"),
                call().write("Two\n"),
                call().write("Three"),
            ],
        )

    @patch("cgmerger.cgmerge.parser")
    @patch("cgmerger.cgmerge.os.path.isfile")
    @patch("cgmerger.cgmerge.os.path.isdir")
    @patch("cgmerger.cgmerge.os.path.getsize")
    @patch("cgmerger.cgmerge.os.listdir")
    @patch("cgmerger.cgmerge.chardet.detect")
    def test_file_regex(self, detect, listdir, getsize, is_dir, path_exists, parser):
        open = mock_open(Mock())
        detect.return_value = {"encoding": "utf-8"}
        getsize.return_value = 1
        path_exists.return_value = True
        is_dir.return_value = True
        listdir.return_value = ["one.cs", "two.py", "three.cs"]
        args_mock, _ = self.get_default_setup(parser)
        args_mock.file_regex = ".*.py"  # ignore one.cs and three.cs
        with patch("cgmerger.cgmerge.open", open):
            main()

        calls = list(
            filter(
                lambda line: line != call().__enter__()
                and line != call().__exit__(None, None, None)
                and line != call().read(1)
                and line != call().readlines(),
                open.mock_calls,
            )
        )
        self.assertListEqual(
            calls,
            [
                call("./codingame.volatile.py", "w"),
                call("./codingame/two.py", "rb"),
                call("./codingame/two.py", "r", encoding="utf-8"),
                call().write(
                    '\n# file "codingame/two.py" ------------------------------------------------------\n'
                ),
                call().write(
                    '\n\n\n# end of file "codingame/two.py" ===============================================\n'
                ),
            ],
        )

    @patch("cgmerger.cgmerge.parser")
    @patch("cgmerger.cgmerge.os.path.isfile")
    @patch("cgmerger.cgmerge.os.path.isdir")
    @patch("cgmerger.cgmerge.os.path.getsize")
    @patch("cgmerger.cgmerge.os.listdir")
    @patch("cgmerger.cgmerge.chardet.detect")
    def test_comment_change(
        self, detect, listdir, getsize, is_dir, path_exists, parser
    ):
        open = mock_open(Mock())
        detect.return_value = {"encoding": "utf-8"}
        getsize.return_value = 1
        path_exists.return_value = True
        is_dir.return_value = True
        listdir.return_value = ["one.cs"]
        args_mock, _ = self.get_default_setup(parser)
        args_mock.output = "codingame.volatile.cs"
        args_mock.comment = "//"
        args_mock.separator_start = "#"
        args_mock.separator_end = "*"
        args_mock.separator_length = "40"
        with patch("cgmerger.cgmerge.open", open):
            main()

        calls = list(
            filter(
                lambda line: line != call().__enter__()
                and line != call().__exit__(None, None, None)
                and line != call().read(1)
                and line != call().readlines(),
                open.mock_calls,
            )
        )
        self.assertListEqual(
            calls,
            [
                call("./codingame.volatile.cs", "w"),
                call("./codingame/one.cs", "rb"),
                call("./codingame/one.cs", "r", encoding="utf-8"),
                call().write('\n// file "codingame/one.cs" #############\n'),
                call().write('\n\n\n// end of file "codingame/one.cs" ******\n'),
            ],
        )

    @patch("cgmerger.cgmerge.parser")
    @patch("cgmerger.cgmerge.os.path.isfile")
    @patch("cgmerger.cgmerge.os.path.isdir")
    @patch("cgmerger.cgmerge.os.path.getsize")
    @patch("cgmerger.cgmerge.os.listdir")
    @patch("cgmerger.cgmerge.chardet.detect")
    def test_exclude_content(
        self, detect, listdir, getsize, is_dir, path_exists, parser
    ):
        open = mock_open(
            Mock(),
            read_data="using System;\nusing System.Linq;\nstatic void Main(string[] args)",
        )
        detect.return_value = {"encoding": "utf-8"}
        getsize.return_value = 1
        path_exists.return_value = True
        is_dir.return_value = True
        listdir.return_value = ["one.cs"]
        args_mock, _ = self.get_default_setup(parser)
        args_mock.exclude_line_regex = "^using"
        args_mock.output = "codingame.volatile.cs"
        args_mock.comment = "//"
        with patch("cgmerger.cgmerge.open", open):
            main()

        calls = list(
            filter(
                lambda line: line != call().__enter__()
                and line != call().__exit__(None, None, None)
                and line != call().read(1)
                and line != call().readlines(),
                open.mock_calls,
            )
        )
        self.assertListEqual(
            calls,
            [
                call("./codingame.volatile.cs", "w"),
                call("./codingame/one.cs", "rb"),
                call("./codingame/one.cs", "r", encoding="utf-8"),
                call().write(
                    '\n// file "codingame/one.cs" -----------------------------------------------------\n'
                ),
                call().write("static void Main(string[] args)"),
                call().write(
                    '\n\n\n// end of file "codingame/one.cs" ==============================================\n'
                ),
            ],
        )

    @patch("cgmerger.cgmerge.parser")
    @patch("cgmerger.cgmerge.os.path.isfile")
    @patch("cgmerger.cgmerge.os.path.isdir")
    @patch("cgmerger.cgmerge.os.path.getsize")
    @patch("cgmerger.cgmerge.os.listdir")
    @patch("cgmerger.cgmerge.chardet.detect")
    def test_bug_3_not_utf(self, detect, listdir, getsize, is_dir, path_exists, parser):
        open = mock_open(
            Mock(),
            read_data=b"\xef\xbb\xbfusing System;\nstatic void Main(string[] "
            b"args)".decode("utf-8-sig"),
        )
        detect.return_value = {"encoding": "utf-8-sig"}
        getsize.return_value = 32
        path_exists.return_value = True
        is_dir.return_value = True
        listdir.return_value = ["one.cs"]
        args_mock, _ = self.get_default_setup(parser)
        args_mock.exclude_line_regex = "^using"
        args_mock.output = "codingame.volatile.cs"
        args_mock.comment = "//"
        with patch("cgmerger.cgmerge.open", open):
            main()

        calls = list(
            filter(
                lambda line: line != call().__enter__()
                and line != call().__exit__(None, None, None)
                and line != call().read(32)
                and line != call().readlines(),
                open.mock_calls,
            )
        )
        self.assertListEqual(
            calls,
            [
                call("./codingame.volatile.cs", "w"),
                call("./codingame/one.cs", "rb"),
                call("./codingame/one.cs", "r", encoding="utf-8-sig"),
                call().write(
                    '\n// file "codingame/one.cs" -----------------------------------------------------\n'
                ),
                call().write("static void Main(string[] args)"),
                call().write(
                    '\n\n\n// end of file "codingame/one.cs" ==============================================\n'
                ),
            ],
        )
