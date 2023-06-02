# AddNoteSpace

**Table of Contents**

- [Overview](#overview)
- [Installation](#installation)
- [License](#license)
- [TODO](#todo)


## Overview

Professors never leave enough space on their slides to take notes.
This allows you to add white space to every side of each page in a pdf file.

This can be done in bulk, where you select an entire folder, or by selecting
a single pdf file.

The configuration can be saved and loaded at will. For adding space in bulk,
there is an additional `run_bulk.exe`, which uses your default values.

## Installation

Head to the [Releases page](https://github.com/maromei/addnotespace/releases)
and download the latest `*.zip` file. The extracted content can be placed anywhere on
your pc. For easy access create a shortcut for the `addnotespace.exe` and
`run_bulk.exe`.

## License

`addnotespace` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.


## TODO:

- app_windows.MainWindow.validate_and_modify_defaults return is never used
- preview of space added
- implement update message
- separate run bulk/single logic from the error windows
- docstrings for info windows needed
- whether to include single file names in the NoteValue dataclass is messy
