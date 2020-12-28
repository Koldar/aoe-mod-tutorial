Installation
============

Linux
-----

To create the pdf (in build):

```
make
```

To clean the build directory

```
make clean
```

Note that this Makefile is **not** windows compliant!

Windows
-------

I've created a powershell script that allows the user to build the pdf. This emulate as much as possible the make file

```
& .\make.ps1
```

Note that you need unrestricted access to powershell scripting. Furthermore, you can configure the make powershell script by looking at "config.ini": within it, you can configure several values like program paths and so on.

Programs that may be required on Windows.
=============================

When writing Latex, I usually install some softwares (which are required in order to complete the compilation):

- MikTex (basically mandatory on windows);
- Plantuml (https://plantuml.com/download), use latest version whenever possible;
- Java (since plantuml is a jar);
- lualatex (latex compiler available from the MikTex);
- Foxit PDF Reader (for viewing pdfs)

Advance Usage
=============

To make a release of the document:

```
make release
```



Making a release will just put a copy of the generated pdf in the release/ folder (together with a version). However, it will do **nothing** about version control!
For further tweaking, see `make show-variables`. If you happen to change the internals of the Makefile, please fill the `NOTES` macro: the content of the macro will always be printed before running the compilation so future developers can see what you have changed.

To build umls:

```
make umls
```

This will invoke Plantuml jar file (positioned in the file system as per `config.ini`). We will call `plantuml` several times, one per file within `src/plantumls`. The generated images will be png and they will be positioned in `src/images/plantumls`.
After this operation you can call `make` to build the pdf. Note that `make`will not call `make umls` at all.

You can invoke the help by doining:



```
make help
```

Or proceed to perform a fast compilation (just one run of `latex`) via:

```
make fast
```


