[![Unix Build Status][travis-image]][travis-link]
[![Package Control Downloads][pc-image]][pc-link]
![License][license-image]
# EasyDiff
EasyDiff is a diff tool for comparing files in Sublime Text in special diff tabs or in your preferred external diff viewer.

![menus](docs/src/markdown/images/menus.png)

# Features
- Allows comparing views, selections, multi-selections, and clipboard combinations.
- Can compare working copy against the base or previous revision of a file in SVN, Git, and Mercurial (requires some setup and configuration).
- Dynamic context menus for selecting left side and right side compare.  Dynamic menus show what file is on *left* side (think Beyond Compare context menus).
- View diffs in a view buffer or output panel.
- You can selectively hide version control menus or disable the command completely via the settings file.
- Can open diffs in external diff programs if desired (requires some setup and configuration).
- Show only internal diff options, only external options, or show both depending on your needs and preferences.

# Documentation
http://facelessuser.github.io/EasyDiff/

# License
EasyDiff is released under the MIT license.

Copyright (c) 2013 - 2018 Isaac Muse <isaacmuse@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

[travis-image]: https://img.shields.io/travis/facelessuser/EasyDiff/master.svg
[travis-link]: https://travis-ci.org/facelessuser/EasyDiff
[pc-image]: https://img.shields.io/packagecontrol/dt/EasyDiff.svg
[pc-link]: https://packagecontrol.io/packages/EasyDiff
[license-image]: https://img.shields.io/badge/license-MIT-blue.svg
