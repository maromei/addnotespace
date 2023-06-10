# AddNoteSpace

**Table of Contents**

- [Overview](#overview)
- [Installation](#installation)
- [License](#license)
- [TODO](#todo)


## Overview

Professors never leave enough space on their slides to take notes.
This tool allows you to add white space to every side of each page in a pdf file.

This can be done in bulk, where you select an entire folder, or by selecting
a single pdf file.

The configuration can be saved and loaded at will. For adding space in bulk,
there is an additional `run_bulk.exe`, which uses your default values.

## Installation

Head to the [Releases page](https://github.com/maromei/addnotespace/releases)
and download the latest `*.zip` file. The extracted content can be placed anywhere on
your pc. This tool functions as a standalone.
For easy access create a shortcut for the `addnotespace.exe` and
`run_bulk.exe`.

## License

`addnotespace` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.


## TODO:

- preview of space added
- whether to include single file names in the NoteValue dataclass is messy
- drag and drop file
- automated dev versioning

## Standing Changes for Version 0.2.0

- Added message for new releases
- If a file is selected for a single run, the new filename will be automatically set. It uses the same folder and file name with the bulk suffix. Should the suffix be empty, "_note" will be used.
