In vscode, we can explore and apply available refactoring actions via **Code Action**

(below is adapted from [official doc page](https://code.visualstudio.com/docs/editing/refactoring))

## Code Action

Select the source code you'd like to extract and then select the light bulb in the gutter or press (`Ctrl+.`) to see
available refactorings.
<img src="../../../res/ts-extract-local.gif">

### (special) Rename symbol

Renaming is a common operation related to refactoring source code, and VS Code has a separate Rename Symbol command (
`F2`). Some languages support renaming a symbol across files. Press F2, type the new desired name, and press Enter. All
instances of the symbol across all files will be renamed.
