import shutil
import subprocess
import sys
from pathlib import Path


package_root = Path(__file__).resolve().parents[1]
package_dir = package_root / "src" / "adroit_wpd2text"
for staging_dir in ("bin", "lib", "licenses"):
    shutil.rmtree(package_dir / staging_dir, ignore_errors=True)
brew_prefix = Path(subprocess.check_output(["brew", "--prefix"], text=True).strip())
binary_source = (brew_prefix / "bin" / "wpd2text").resolve()
binary_target = package_dir / "bin" / "wpd2text"
binary_target.parent.mkdir(exist_ok=True)
shutil.copy2(binary_source, binary_target)

libraries = [
    (brew_prefix / "opt" / "libwpd" / "lib" / "libwpd-0.10.dylib").resolve(),
    (brew_prefix / "opt" / "librevenge" / "lib" / "librevenge-0.0.dylib").resolve(),
    (brew_prefix / "opt" / "librevenge" / "lib" / "librevenge-generators-0.0.dylib").resolve(),
    (brew_prefix / "opt" / "librevenge" / "lib" / "librevenge-stream-0.0.dylib").resolve(),
]
library_dir = package_dir / "lib"
library_dir.mkdir(exist_ok=True)
for library_source in libraries:
    shutil.copy2(library_source, library_dir / library_source.name)

for library_name in ("libwpd", "librevenge"):
    formula_dir = (brew_prefix / "opt" / library_name).resolve()
    license_dir = package_dir / "licenses"
    license_dir.mkdir(exist_ok=True)
    for license_type in ("MPL", "LGPL"):
        shutil.copy2(
            formula_dir / f"COPYING.{license_type}",
            license_dir / f"{library_name}-{license_type}.txt",
        )

for binary_path in [binary_target, *(library_dir / source.name for source in libraries)]:
    if binary_path.suffix == ".dylib":
        subprocess.run(
            ["install_name_tool", "-id", f"@loader_path/{binary_path.name}", str(binary_path)],
            check=True,
        )
    linked_libraries = subprocess.check_output(["otool", "-L", str(binary_path)], text=True)
    for linked_line in linked_libraries.splitlines()[1:]:
        linked_path = linked_line.strip().split(" (")[0]
        if "/libwpd/" in linked_path or "/librevenge/" in linked_path:
            linked_name = Path(linked_path).name
            relative_path = (
                f"@executable_path/../lib/{linked_name}"
                if binary_path == binary_target
                else f"@loader_path/{linked_name}"
            )
            subprocess.run(
                ["install_name_tool", "-change", linked_path, relative_path, str(binary_path)],
                check=True,
            )
    subprocess.run(["codesign", "--force", "--sign", "-", str(binary_path)], check=True)

shutil.rmtree(package_root / "build", ignore_errors=True)
subprocess.run([sys.executable, "-m", "build", "--wheel"], cwd=package_root, check=True)
platform = f"macosx_{subprocess.check_output(['sw_vers', '-productVersion'], text=True).split('.')[0]}_0_{sys.argv[1]}"
untagged_wheel = next((package_root / "dist").glob("*-cp*-cp*-macosx_*.whl"))
subprocess.run(
    [
        sys.executable,
        "-m",
        "wheel",
        "tags",
        "--remove",
        "--python-tag",
        "py3",
        "--abi-tag",
        "none",
        "--platform-tag",
        platform,
        str(untagged_wheel),
    ],
    check=True,
)
