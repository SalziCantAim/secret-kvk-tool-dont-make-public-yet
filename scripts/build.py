import shutil
from pathlib import Path
import PyInstaller.__main__


def main() -> None:
    Path("./dist/").mkdir(parents=True, exist_ok=True)
    exePath: Path = Path("./dist/Kovaaks_Tool.exe")
    if exePath.exists():
        exePath.unlink()

    assetsPath: Path = Path("./dist/assets/")
    if assetsPath.exists():
        shutil.rmtree(assetsPath)

    PyInstaller.__main__.run(
        [
            "./src/Kovaaks_Tool.py",
            "--onefile",
            "--windowed",
            "--clean",
        ]
    )

    shutil.copytree("./src/assets/", "./dist/assets/")


if __name__ == "__main__":
    main()
