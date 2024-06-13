copies the ansible-core `command` and `shell` modules, but adds a new option: `modifies`.

`modifies` is gramatically similar to `creates` and `removes` but the logic underneath is different. While `creates` and `removes` give the task a chance to exit early, `modifies` allows the task to define whether or not it changed based on the contents of a list of files, and it allows the task to produce a diff.

```yml
modifies:
  type: list
  elements: str
  description:
    - A list of file paths. A tempfile copy is made of each file before command execution,
    - and then `results['changed']` `results['diff']` are set by comparing after command execution.
```
