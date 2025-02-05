# Copyright: (c) 2017, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import annotations

import os
import shutil
import tempfile

from ansible.plugins.action import ActionBase
from ansible.utils.vars import merge_hash
from ansible.parsing.splitter import split_args


def _create_copy_or_empty_tempfile(path: str):
    """
    Create a tempfile containing a copy of the file at `path`.
    If `path` does not point to a file, create an empty tempfile.
    """
    fd, tempfile_path = tempfile.mkstemp(dir=C.DEFAULT_LOCAL_TMP)
    if os.path.isfile(path):
        try:
            shutil.copy(path, tempfile_path)
        except Exception as err:
            os.remove(tempfile_path)
            raise Exception(err)
    return tempfile_path


class ActionModule(ActionBase):

    def run(self, tmp=None, task_vars=None):
        self._supports_async = True
        results = super(ActionModule, self).run(tmp, task_vars)
        del tmp  # tmp no longer has any effect

        # the normal command module has presumably this same logic buried somewhere else in the source code
        if "cmd" in self._task.args:
            if self._task.args.get("_uses_shell", False):
                self._task.args["_raw_params"] = self._task.args["cmd"]
            else:
                self._task.args["argv"] = split_args(self._task.args["cmd"])
            del self._task.args["cmd"]

        wrap_async = self._task.async_val and not self._connection.has_native_async
        results = merge_hash(
            results,
            self._execute_module(
                module_name="unity.command_shell_diff.command",
                task_vars=task_vars,
                wrap_async=wrap_async,
            ),
        )

        if not wrap_async:
            # remove a temporary path we created
            self._remove_tmp_path(self._connection._shell.tmpdir)

        return results
