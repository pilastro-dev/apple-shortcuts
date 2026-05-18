Welcome to the Cherri programming language documentation!

Thanks for taking an interest in the Cherri programming language. Cherri is designed to be easy to learn and use, and it’s likely very similar to a programming language you may already be familiar with.

Contributing to this open-source documentation is more than welcome!

## Offline

For general documentation, you can clone the repo for this site.

You can access the documentation for actions (even ones defined in your project) completely offline from the CLI.

```bash
cherri --action=action_name
```

This will find the action or give suggestions if there is no exact match.

Search actions defined in a project:

```bash
cherri main.cherri --action=action_name
```

### All actions

Providing nothing will show all standard actions documentation.

### By category

Prints all definitons for actions in the provided category and optionally a subcategory.

```bash
cherri --docs=category --subcat=optional
```

Subcategories are listed on each category page.

All parent categories are listed in the help message using `--help`.

---

## Table of contents

- [Actions](./actions.md)
- [Comments](./comments.md)
- [Definitions](./definitions.md)
- [Variables, Constants & Globals](./variables-constants-globals.md)
- [Content References](./references.md)
- [Types](./types.md)
- [Control Flow](./control-flow.md)
- [Menus](./menus.md)
- [vCard Menus](./vcards.md)
- [Copy/Paste Actions](./copy-paste.md)
- [Import Questions](./import-questions.md)
- [Import Actions](./import-actions.md)
- [Includes](./includes.md)
- [Functions](./functions.md)
- [Action Definitions](./action-definitions.md)
- [Packages](./package-manager.md)
- [Raw Actions](./raw-actions.md)
- [Best Practices](./best-practices.md)
