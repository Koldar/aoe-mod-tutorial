from typing import List

require_pmake_version("1.12.1")

property_file = path_wrt_pmakefile("config.properties")
read_variables_from_properties(property_file)

ensure_has_variable("PDF_READER_PROCESS_NAME")
set_variable("PDF_READER_EXE_NAME", variables.PDF_READER_PROCESS_NAME + ".exe")

if not has_variable_in_cache("PDF_READER_FULLPATH_EXE"):
    # save in cache the path of the pdf reader
    set_variable_in_cache("PDF_READER_FULLPATH_EXE", find_executable_in_program_directories(variables.PDF_READER_EXE_NAME, fail_if_program_is_not_found=True))
set_variable("PDF_READER_FULLPATH_EXE", get_variable_in_cache("PDF_READER_FULLPATH_EXE"))


get_variable_or("NOTES", "")
get_variable_or("BUILD_FOLDER", "build")
get_variable_or("RELEASE_FOLDER", "releases")
get_variable_or("LATEX_CC", "lualatex")
get_variable_or("BIBTEX_CC", "bibtex")
get_variable_or("MAKEINDEX_EXE", "makeglossaries-lite")
get_variable_or("MAIN_SRC", "main")
# name of the output pdf (extensions excluded)
get_variable_or("OUTPUT_NAME", "main")
get_variable_or("RELEASE_NAME", "releases")
get_variable_or("LATEX_FLAGS", "-halt-on-error -interaction=nonstopmode -c-style-errors")
get_variable_or("BIBTEX_FLAGS", "-quiet")
get_variable_or("VERSION_FILE", ".version")
get_variable_or("OPEN_CLOSE_PDFREADER", True)
get_variable_or("PDF_READER_OPEN_FILE", "")
get_variable_or("PDF_READER_SUPPORT_TAB_FILE", False)
get_variable_or("PDF_READER_CLOSE_TAB_FILE", "")

###################################
# Utils
###################################

def get_main_src_file() -> str:
    return path_wrt_pmakefile(f"{variables.MAIN_SRC}.tex")


def get_pdf_file() -> str:
    return path_wrt_pmakefile(variables.BUILD_FOLDER, f"{variables.OUTPUT_NAME}.pdf")


def get_version_file() -> str:
    return path_wrt_pmakefile(variables.VERSION_FILE)


def latexFlags() -> List[str]:
    return variables.LATEX_FLAGS.split(" ")


def bibtexFlags() -> List[str]:
    return variables.BIBTEX_FLAGS.split(" ")

###################################
# Targets
###################################

def clean_pmake_cache():
    clear_cache()

def clean():
    remove_tree(variables.BUILD_FOLDER, ignore_if_not_exists=True)


def open_pdf_reader():
    execute_and_forget(commands=[
        f"{variables.PDF_READER_EXE} {variables.PDF_READER_OPEN_FILE} {get_pdf_file()}"
    ])


def close_pdf_reader():
    if as_bool(variables.PDF_READER_SUPPORT_TAB_FILE):
        execute_and_forget(commands=[
            f"{variables.PDF_READER_EXE} {variables.PDF_READER_CLOSE_TAB_FILE} {get_pdf_file()}"
        ])
    else:
        kill_process_by_name(program_name=variables.PDF_READER_EXE, ignore_if_process_does_not_exists=True)


def call_latex():
    cmd = []
    cmd.append(variables.LATEX_CC)
    cmd.extends(latexFlags())
    cmd.append(get_main_src_file())
    echo(f"executing {' '.join(cmd)} at {get_pmakefile_dir()}", foreground="blue")
    execute_stdout_on_screen(
        commands=[cmd],
        cwd=get_pmakefile_dir()
    )


def call_bibtex():
    cmd = []
    cmd.append(variables.BIBTEX_CC)
    cmd.extends(bibtexFlags())
    cmd.append("-include-directory='..'")
    cmd.append(get_file_without_extension(get_pdf_file()))
    execute_stdout_on_screen(
        commands=[cmd],
        cwd=get_pmakefile_path()
    )


def call_makeindex():
    cmd = []
    cmd.append(variables.MAKEINDEX_EXE)
    cmd.append(variables.MAIN_SRC)
    execute_stdout_on_screen(
        commands=[cmd],
        cwd = path_wrt_pmakefile(variables.BUILD_FOLDER)
    )


def make_all():
    try:
        echo(f"Compiling first time with latex", foreground="blue")
        call_latex()
        echo(f"Compiling bibliography", foreground="blue")
        call_bibtex()
        echo(f"Resordering glossary with makeindex", foreground="blue")
        call_makeindex()
        echo(f"Compiling second time", foreground="blue")
        call_latex()
        echo(f"Compiling third time", foreground="blue")
        call_latex()
        echo(f"Compilation has succeeded!", foreground="green")
    except Exception as e:
        echo(f"Failed the compilation due to {e}", foreground="red")


def make_fast():
    try:
        echo(f"Compiling...", foreground="blue")
        call_latex()
        echo(f"Compilation has succeeded!", foreground="green")
    except Exception as e:
        echo(f"Failed the compilation due to {e}", foreground="red")


def make_directories():
    make_directories(path_wrt_pmakefile(variables.RELEASE_FOLDER))


def update_version():
    version_file = get_version_file()
    if not is_file_exists(version_file):
        version = VersionInfo.parse("1.0.0")
    else:
        version = read_file_content(
            name=version_file,
            encoding="utf-8",
            trim_newlines=True
        )
        version = VersionInfo.parse(version)
        version = version.bump_major()

    write_file(
        name=version_file,
        content=str(version),
        encoding="utf-8",
        overwrite=False,
        add_newline=False
    )


def make_release():
    version = get_version_file()
    new_file = path_wrt_pmakefile(variables.RELEASE_FOLDER, f"{RELEASE_NAME}-{version}.pdf")
    copy_file(
        src=get_pdf_file(),
        dst=new_file
    )


###################################
# process targets
###################################


declare_file_descriptor(f"""
    Allows to build a latex project.
    {variables.NOTES}
""")

declare_target(
    target_name="clean-cache",
    requires=[],
    description="Clean pmake cache",
    f=clean_pmake_cache
)

declare_target(
    target_name="clean",
    requires=[],
    description="Clean all the metadata generated by building the project (but notn pmake cache)",
    f=clean
)

declare_target(
    target_name="open-pdf",
    requires=[],
    description="Open the pdf reader allowing you to read the pdf generated",
    f=open_pdf_reader
)

declare_target(
    target_name="close-pdf",
    requires=[],
    description="Close the pdf reader. Some systems (e.g., windows) does not allow compioling the latex if the output file is opened by a pdf reader",
    f=close_pdf_reader
)

declare_target(
    target_name="all",
    requires=[],
    description="""
        Build the pdf by calling latex 3 times. In this way we can build the pdf, the bibliography and the glossaries. 
        Slow, but ensure that the document is build from beginning to end""",
    f=make_all
)

declare_target(
    target_name="fast",
    requires=[],
    description="""
        Run latex once. Fast, but bibliography and index are not syncyhronized 
    """,
    f=make_fast
)


declare_target(
    target_name="make-directories",
    requires=[],
    description="""
        Create the necessaries directories for the project
    """,
    f=make_directories
)


declare_target(
    target_name="update-version",
    requires=["make-directories"],
    description=f"""
        Update the version of the document. The version is stored in {variables.VERSION_FILE} 
    """,
    f=update_version
)

declare_target(
    target_name="release",
    requires=["make-directories", "update-version", "all"],
    description="""
        Build the document from start to finish, then copy the artifact to the release folder. 
    """,
    f=make_release
)

process_targets()

