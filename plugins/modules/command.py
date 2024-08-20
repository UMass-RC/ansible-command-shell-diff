# -*- coding: utf-8 -*-

# Copyright: (c) 2012, Michael DeHaan <michael.dehaan@gmail.com>, and others
# Copyright: (c) 2016, Toshio Kuratomi <tkuratomi@ansible.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import annotations


DOCUMENTATION = r'''
---
module: command
short_description: Execute commands on targets
version_added: historical
description:
     - The M(ansible.builtin.command) module takes the command name followed by a list of space-delimited arguments.
     - The given command will be executed on all selected nodes.
     - The command(s) will not be
       processed through the shell, so variables like C($HOSTNAME) and operations
       like C("*"), C("<"), C(">"), C("|"), C(";") and C("&") will not work.
       Use the M(ansible.builtin.shell) module if you need these features.
     - To create C(command) tasks that are easier to read than the ones using space-delimited
       arguments, pass parameters using the C(args) L(task keyword,https://docs.ansible.com/ansible/latest/reference_appendices/playbooks_keywords.html#task)
       or use O(cmd) parameter.
     - Either a free form command or O(cmd) parameter is required, see the examples.
     - For Windows targets, use the M(ansible.windows.win_command) module instead.
extends_documentation_fragment:
    - action_common_attributes
    - action_common_attributes.raw
attributes:
    check_mode:
        details: while the command itself is arbitrary and cannot be subject to the check mode semantics it adds O(creates)/O(removes) options as a workaround
        support: partial
    diff_mode:
        details: the `modifies` option shows a diff before/after command execution.
        support: partial
    platform:
      support: full
      platforms: posix
    raw:
      support: full
options:
  expand_argument_vars:
    description:
      - Expands the arguments that are variables, for example C($HOME) will be expanded before being passed to the
        command to run.
      - Set to V(false) to disable expansion and treat the value as a literal argument.
    type: bool
    default: true
    version_added: "2.16"
  free_form:
    description:
      - The command module takes a free form string as a command to run.
      - There is no actual parameter named 'free form'.
  cmd:
    type: str
    description:
      - The command to run.
  argv:
    type: list
    elements: str
    description:
      - Passes the command as a list rather than a string.
      - Use O(argv) to avoid quoting values that would otherwise be interpreted incorrectly (for example "user name").
      - Only the string (free form) or the list (argv) form can be provided, not both.  One or the other must be provided.
    version_added: "2.6"
  creates:
    type: path
    description:
      - A filename or (since 2.0) glob pattern. If a matching file already exists, this step B(will not) be run.
      - This is checked before O(removes) is checked.
  removes:
    type: path
    description:
      - A filename or (since 2.0) glob pattern. If a matching file exists, this step B(will) be run.
      - This is checked after O(creates) is checked.
    version_added: "0.8"
  modifies:
    type: list
    elements: str
    description:
      - A list of file paths. A tempfile copy is made of each file before command execution,
      - and then `results['changed']` `results['diff']` are set by comparing after command execution.
      - Plain text files only.
    version_added: "2.18"
  chdir:
    type: path
    description:
      - Change into this directory before running the command.
    version_added: "0.6"
  stdin:
    description:
      - Set the stdin of the command directly to the specified value.
    type: str
    version_added: "2.4"
  stdin_add_newline:
    type: bool
    default: yes
    description:
      - If set to V(true), append a newline to stdin data.
    version_added: "2.8"
  strip_empty_ends:
    description:
      - Strip empty lines from the end of stdout/stderr in result.
    version_added: "2.8"
    type: bool
    default: yes
notes:
    -  If you want to run a command through the shell (say you are using C(<), C(>), C(|), and so on),
       you actually want the M(ansible.builtin.shell) module instead.
       Parsing shell metacharacters can lead to unexpected commands being executed if quoting is not done correctly so it is more secure to
       use the M(ansible.builtin.command) module when possible.
    -  O(creates), O(removes), and O(chdir) can be specified after the command.
       For instance, if you only want to run a command if a certain file does not exist, use this.
    -  Check mode is supported when passing O(creates) or O(removes). If running in check mode and either of these are specified, the module will
       check for the existence of the file and report the correct changed status. If these are not supplied, the task will be skipped.
    -  The O(ignore:executable) parameter is removed since version 2.4. If you have a need for this parameter, use the M(ansible.builtin.shell) module instead.
    -  For Windows targets, use the M(ansible.windows.win_command) module instead.
    -  For rebooting systems, use the M(ansible.builtin.reboot) or M(ansible.windows.win_reboot) module.
    -  If the command returns non UTF-8 data, it must be encoded to avoid issues. This may necessitate using M(ansible.builtin.shell) so the output
       can be piped through C(base64).
seealso:
- module: ansible.builtin.raw
- module: ansible.builtin.script
- module: ansible.builtin.shell
- module: ansible.windows.win_command
author:
    - Ansible Core Team
    - Michael DeHaan
'''

EXAMPLES = r'''
- name: Return motd to registered var
  ansible.builtin.command: cat /etc/motd
  register: mymotd

# free-form (string) arguments, all arguments on one line
- name: Run command if /path/to/database does not exist (without 'args')
  ansible.builtin.command: /usr/bin/make_database.sh db_user db_name creates=/path/to/database

# free-form (string) arguments, some arguments on separate lines with the 'args' keyword
# 'args' is a task keyword, passed at the same level as the module
- name: Run command if /path/to/database does not exist (with 'args' keyword)
  ansible.builtin.command: /usr/bin/make_database.sh db_user db_name
  args:
    creates: /path/to/database

# 'cmd' is module parameter
- name: Run command if /path/to/database does not exist (with 'cmd' parameter)
  ansible.builtin.command:
    cmd: /usr/bin/make_database.sh db_user db_name
    creates: /path/to/database

- name: Run command and show changes in /path/to/database file
  ansible.builtin.command:
    cmd: /usr/bin/make_database.sh db_user db_name
    modifies:
      - /path/to/database
    diff: true

- name: Change the working directory to somedir/ and run the command as db_owner if /path/to/database does not exist
  ansible.builtin.command: /usr/bin/make_database.sh db_user db_name
  become: yes
  become_user: db_owner
  args:
    chdir: somedir/
    creates: /path/to/database

# argv (list) arguments, each argument on a separate line, 'args' keyword not necessary
# 'argv' is a parameter, indented one level from the module
- name: Use 'argv' to send a command as a list - leave 'command' empty
  ansible.builtin.command:
    argv:
      - /usr/bin/make_database.sh
      - Username with whitespace
      - dbname with whitespace
    creates: /path/to/database

- name: Run command using argv with mixed argument formats
  ansible.builtin.command:
    argv:
      - /path/to/binary
      - -v
      - --debug
      - --longopt
      - value for longopt
      - --other-longopt=value for other longopt
      - positional

- name: Safely use templated variable to run command. Always use the quote filter to avoid injection issues
  ansible.builtin.command: cat {{ myfile|quote }}
  register: myoutput
'''

RETURN = r'''
msg:
  description: changed
  returned: always
  type: bool
  sample: True
start:
  description: The command execution start time.
  returned: always
  type: str
  sample: '2017-09-29 22:03:48.083128'
end:
  description: The command execution end time.
  returned: always
  type: str
  sample: '2017-09-29 22:03:48.084657'
delta:
  description: The command execution delta time.
  returned: always
  type: str
  sample: '0:00:00.001529'
stdout:
  description: The command standard output.
  returned: always
  type: str
  sample: 'Clustering node rabbit@slave1 with rabbit@master …'
stderr:
  description: The command standard error.
  returned: always
  type: str
  sample: 'ls cannot access foo: No such file or directory'
cmd:
  description: The command executed by the task.
  returned: always
  type: list
  sample:
  - echo
  - hello
rc:
  description: The command return code (0 means success).
  returned: always
  type: int
  sample: 0
stdout_lines:
  description: The command standard output split in lines.
  returned: always
  type: list
  sample: [u'Clustering node rabbit@slave1 with rabbit@master …']
stderr_lines:
  description: The command standard error split in lines.
  returned: always
  type: list
  sample: [u'ls cannot access foo: No such file or directory', u'ls …']
'''

import datetime
import glob
import os
import pwd
import grp
import shlex
import stat
import hashlib

from typing import List

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.common.text.converters import to_native, to_bytes, to_text
from ansible.module_utils.common.collections import is_iterable


def examine_file(path: str) -> dict:

    def human_readable_size(st_size) -> str:
        if st_size < 1024:
            return f"{st_size} bytes"
        current_size = st_size
        for suffix in ["KiB", "MiB", "GiB", "TiB", "PiB"]:
            current_size = current_size / 1024
            if current_size < 1024:
                return f"{current_size:.2f} {suffix}"
        return f"{current_size:.2f} {suffix}"

    def human_readable_file_type(st_mode) -> str:
        func2file_type = {
            stat.S_ISREG: "regular file",
            stat.S_ISDIR: "directory",
            stat.S_ISCHR: "character device",
            stat.S_ISBLK: "block device",
            stat.S_ISFIFO: "FIFO/pipe",
            stat.S_ISLNK: "symlink",
            stat.S_ISSOCK: "socket",
        }
        for func, file_type in func2file_type.items():
            if func(st_mode):
                return file_type
        return "unknown"

    def _human_readable_stat(path: str) -> dict:
        path_stat = os.stat(path, follow_symlinks=False)
        return {
            "path": path,
            "owner": pwd.getpwuid(path_stat.st_uid).pw_name,
            "group": grp.getgrgid(path_stat.st_gid).gr_name,
            "file_type": human_readable_file_type(path_stat.st_mode),
            "mode": stat.filemode(path_stat.st_mode),
            "size": human_readable_size(path_stat.st_size),
        }

    def get_symlink_destination_absolute(symlink_path: str) -> str:
        destination_path = os.readlink(symlink_path)
        if not os.path.isabs(destination_path):
            # "/a/b/c" -> "../d" = "a/b/c/../d"
            return os.path.abspath(os.path.join(os.path.dirname(symlink_path), destination_path))
        return destination_path

    def human_readable_stat(path) -> List[dict]:
        """
        Return a list of human-readable stat dictionaries. If the path is a symlink,
        append another dict to the list using the destination of that symlink, and so on.
        """
        path = os.path.abspath(path)
        output = [_human_readable_stat(path)]
        seen_paths = [path]  # To handle cyclic symlinks
        while output[-1]["file_type"] == "symlink":
            path = get_symlink_destination_absolute(path)
            if path in seen_paths:
                raise RecursionError(f"Cyclic symlinks detected: {seen_paths + [path]}")
            output.append(_human_readable_stat(path))
        return output

    output = {}
    try:
        output["stat"] = human_readable_stat(path)
        if output["stat"][0]["file_type"] in ["regular file", "symlink"]:
            try:
                with open(path, "r", encoding="utf8") as fp:
                    output["content"] = fp.read()
            except UnicodeDecodeError:
                with open(path, "rb") as fp:
                    output["content"] = (
                        f"content ommitted, binary file. sha1sum: {hashlib.sha1(fp.read()).hexdigest()}"
                    )
        elif output["stat"][0]["file_type"] == "directory":
            output["content"] = os.listdir(path)
        else:
            output["content"] = "content ommitted, special file."
    except FileNotFoundError:
        output = {"state": "absent", "stat": None, "contents": None}
    return output

def main():

    # the command module is the one ansible module that does not take key=value args
    # hence don't copy this one if you are looking to build others!
    # NOTE: ensure splitter.py is kept in sync for exceptions
    module = AnsibleModule(
        argument_spec=dict(
            _raw_params=dict(),
            _uses_shell=dict(type='bool', default=False),
            argv=dict(type='list', elements='str'),
            chdir=dict(type='path'),
            executable=dict(),
            expand_argument_vars=dict(type='bool', default=True),
            creates=dict(type='path'),
            removes=dict(type='path'),
            modifies=dict(type='list', elements='str'),
            # The default for this really comes from the action plugin
            stdin=dict(required=False),
            stdin_add_newline=dict(type='bool', default=True),
            strip_empty_ends=dict(type='bool', default=True),
        ),
        supports_check_mode=True,
    )
    shell = module.params['_uses_shell']
    chdir = module.params['chdir']
    executable = module.params['executable']
    args = module.params['_raw_params']
    argv = module.params['argv']
    creates = module.params['creates']
    removes = module.params['removes']
    modifies = module.params['modifies']
    stdin = module.params['stdin']
    stdin_add_newline = module.params['stdin_add_newline']
    strip = module.params['strip_empty_ends']
    expand_argument_vars = module.params['expand_argument_vars']

    # we promised these in 'always' ( _lines get auto-added on action plugin)
    r = {'changed': False, 'stdout': '', 'stderr': '', 'rc': None, 'cmd': None, 'start': None, 'end': None, 'delta': None, 'msg': ''}

    if not shell and executable:
        module.warn("As of Ansible 2.4, the parameter 'executable' is no longer supported with the 'command' module. Not using '%s'." % executable)
        executable = None

    if (not args or args.strip() == '') and not argv:
        r['rc'] = 256
        r['msg'] = "no command given"
        module.fail_json(**r)

    if args and argv:
        r['rc'] = 256
        r['msg'] = "only command or argv can be given, not both"
        module.fail_json(**r)

    if not shell and args:
        args = shlex.split(args)

    args = args or argv
    # All args must be strings
    if is_iterable(args, include_strings=False):
        args = [to_native(arg, errors='surrogate_or_strict', nonstring='simplerepr') for arg in args]

    r['cmd'] = args

    if chdir:
        chdir = to_bytes(chdir, errors='surrogate_or_strict')

        try:
            os.chdir(chdir)
        except (IOError, OSError) as e:
            r['msg'] = 'Unable to change directory before execution: %s' % to_text(e)
            module.fail_json(**r)

    # check_mode partial support, since it only really works in checking creates/removes
    if module.check_mode:
        shoulda = "Would"
    else:
        shoulda = "Did"

    # special skips for idempotence if file exists (assumes command creates)
    if creates:
        if glob.glob(creates):
            r['msg'] = "%s not run command since '%s' exists" % (shoulda, creates)
            r['stdout'] = "skipped, since %s exists" % creates  # TODO: deprecate

            r['rc'] = 0

    # special skips for idempotence if file does not exist (assumes command removes)
    if not r['msg'] and removes:
        if not glob.glob(removes):
            r['msg'] = "%s not run command since '%s' does not exist" % (shoulda, removes)
            r['stdout'] = "skipped, since %s does not exist" % removes  # TODO: deprecate
            r['rc'] = 0

    if r['msg']:
        module.exit_json(**r)

    r['changed'] = True

    # initialize before/after data structure, fill out before
    path2diff = {}
    if modifies is not None and len(modifies) > 0:
        for path in modifies:
            path2diff[path] = {"before": {}, "after": {}}
            path2diff[path]["before"] = examine_file(path)

    # actually executes command (or not ...)
    if not module.check_mode:
        r['start'] = datetime.datetime.now()
        r['rc'], r['stdout'], r['stderr'] = module.run_command(args, executable=executable, use_unsafe_shell=shell, encoding=None,
                                                               data=stdin, binary_data=(not stdin_add_newline),
                                                               expand_user_and_vars=expand_argument_vars)
        r['end'] = datetime.datetime.now()
    else:
        # this is partial check_mode support, since we end up skipping if we get here
        r['rc'] = 0
        r['msg'] = "Command would have run if not in check mode"
        if creates is None and removes is None:
            r['skipped'] = True
            # skipped=True and changed=True are mutually exclusive
            r['changed'] = False

    # fill out the "after" part of the before/after data structure, compare
    if modifies is not None and len(modifies) > 0:
        r['diff'] = []
        r['changed'] = False
        for path in modifies:
            path2diff[path]["after"] = examine_file(path)
        for path in modifies:
            if path2diff[path]["before"] != path2diff[path]["after"]:
                new_diff = path2diff[path]
                # if state has changed, then "state" is the only key that matters
                if new_diff["before"]["state"] != new_diff["after"]["state"]:
                    new_diff["before"] = {"state": new_diff["before"]["state"]}
                    new_diff["after"] = {"state": new_diff["after"]["state"]}
                # always add the "path" key
                new_diff["before"]["path"] = new_diff["after"]["path"] = path
                r['diff'].append(new_diff)
                r['changed'] = True

    # convert to text for jsonization and usability
    if r['start'] is not None and r['end'] is not None:
        # these are datetime objects, but need them as strings to pass back
        r['delta'] = to_text(r['end'] - r['start'])
        r['end'] = to_text(r['end'])
        r['start'] = to_text(r['start'])

    if strip:
        r['stdout'] = to_text(r['stdout']).rstrip("\r\n")
        r['stderr'] = to_text(r['stderr']).rstrip("\r\n")

    if r['rc'] != 0:
        r['msg'] = 'non-zero return code'
        module.fail_json(**r)

    module.exit_json(**r)


if __name__ == '__main__':
    main()
