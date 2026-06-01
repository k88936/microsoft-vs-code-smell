There are two places to explore available refactoring actions in the %IDE_NAME%: the **Refactor This**
and **Search Everywhere** dialogs.

(below is adapted from [Practical IDE Code Refactoring in Kotlin](https://github.com/jetbrains-academy/refactoring-course))

### Refactor This

To invoke refactoring in %IDE_NAME%;, select an item to refactor (a variable, method, class, package, etc.)
and press **&shortcut:Refactorings.QuickListPopupAction;** to open a
list of
refactorings that can be applied.
You can also use a shortcut to invoke specific refactoring.

It is possible to undo any refactoring by pressing **&shortcut:$Undo;**.

<img src="../../../res/refactor_this.png" alt="Refactor This" width="400"/>

### Search Everywhere

If you want to refactor some code and are unfamiliar with the IDE’s refactorings shortcuts, you can open the **Search
Everywhere** dialog and type the name of the action you would like to perform.

To open the **Search Everywhere** dialog, press **Shift+Shift**.

For example, if you want to extract a function or explore any extract possibilities in the IDE,
open the **Search Everywhere** dialog, type “Extract”, and it will show the available options.

<img src="../../../res/search_everywhere.png" alt="Search Everywhere" width="400"/>

Moreover, for some refactorings, %IDE_NAME% allows users to see the preview before applying changes.
It could be useful if you are not sure how refactoring changes would affect your code and want to make sure that it
would work as you expect.

### Refactoring shortcuts

Here is a table with the most popular refactorings and shortcuts to invoke them:

| Refactoring type       | Description                                                            | Shortcut                                     |
|------------------------|------------------------------------------------------------------------|----------------------------------------------|
| **Refactor This**      | Shows available refactoring options.                                   | &shortcut:Refactorings.QuickListPopupAction; |
| **Rename**             | Changes the name of the code element.                                  | &shortcut:RenameElement;                     |
| **Change Signature**   | Allows to change the method’s name, parameters, and return type.       | &shortcut:ChangeSignature;                   |
| **Introduce Variable** | Extracts a value into a new variable.                                  | &shortcut:IntroduceVariable;                 |
| **Inline**             | Removes a variable/method and puts its body to the place it’s used at. | &shortcut:Inline;                            |
| **Extract Function**   | Creates a new method and moves a selected piece of code to it.         | &shortcut:ExtractMethod;                     |
| **Move**               | Moves code method/class to another place in the codebase.              | &shortcut:DatabaseView.MoveToGroup;          |
