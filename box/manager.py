"""Provide user with utility functions for box"""

import io
from pathlib import Path

from boxsdk.object.folder import Folder

from box.oauth2 import get_box_client

###################################################
# Proteomics folder id
FOLDER_ID = "200099021915"
# Protected folders
PROTECTED_FOLDERS = [
    ".",
    "raw_data",
    "results",
    "archives",
    "official",
]
###################################################


class BoxManager:
    """
    Provide user with utility functions for Box.

    The root folder is called 'proteomics' and is structured as follows:
    - raw_data: contains cortisol, melatonin, proteins, and temperature data.
    - doc: contains additional information from labs / companies.
    - archives: contains useful formatted datasets.
    - official: contains official documents such as grants and abstracts...etc.
    - results: contains relevant figures and information to present our research.

    Methods:
    - __init__: Authenticates the client, and sets the root proteomics folder.
    - get_id: Recursively retrieves the ID of a file or folder based on its path.
    - get_file: Retrieves a file from Box and returns its contents as a StringIO object.
    - save_file: Saves of updates a file to Box.
    - create_folder: Creates a folder and necessary parents in Box.
    - delete: Deletes a specified item from Box.
    - get_folder_contents: Retrieves the contents of a folder in Box.
    - exists: Checks if a file or folder exists in Box.
    """

    def __init__(self):
        self.token_path = Path("box/tokens.yaml")
        if self.token_path.exists():
            self.client = get_box_client()
            self.proteomics = self.client.folder(folder_id=FOLDER_ID).get()

    def get_id(self, path: Path, folder: Folder) -> str:
        """Get box file id (recursive)"""
        parts = path.parts
        # If path is empty
        if len(parts) == 0:
            return folder.object_id
        # If path is just the file's name
        if len(parts) == 1:
            for item in folder.get_items():
                if item.name == parts[0]:
                    return item.id
            raise FileNotFoundError(f"Item {path} not found in Box")
        # If the path includes at least a parent folder
        for item in folder.get_items():
            if item.name == parts[0]:
                return self.get_id(Path(*parts[1:]), item)
        raise FileNotFoundError(f"Item {path} not found in Box")

    def get_file(self, path: Path) -> io.StringIO:
        """Get box file"""
        file_id = self.get_id(path, self.proteomics)
        file = self.client.file(file_id).get()
        return io.StringIO(file.content().decode("utf-8"))

    def save_file(self, file: io.IOBase, path: Path):
        """Save file to Box"""
        # If path is a folder
        if path.suffix == "":
            raise ValueError(f"{path} is a folder.")
        # Try to update the file
        if self.exists(path):
            file_id = self.get_id(path, self.proteomics)
            self.client.file(file_id).update_contents_with_stream(
                file, upload_using_accelerator=True
            )
        # If file does not exist, create it
        else:
            folder_id = self.get_id(path.parent, self.proteomics)
            self.client.folder(folder_id).upload_stream(
                file, path.name, upload_using_accelerator=True
            )

    def create_folder(self, path: Path):
        """Create folder in Box"""
        if path.suffix:
            raise ValueError(f"{path} is not a folder.")
        if self.exists(path):
            raise ValueError(f"{path} already exists.")
        if self.exists(path.parent):
            folder_id = self.get_id(path.parent, self.proteomics)
            self.client.folder(folder_id).create_subfolder(path.name)
        else:
            self.create_folder(path.parent)
            folder_id = self.get_id(path.parent, self.proteomics)
            self.client.folder(folder_id).create_subfolder(path.name)

    def delete(self, path: Path, **kwargs):
        """Delete item in Box"""
        if str(path) in PROTECTED_FOLDERS:
            raise ValueError(f"Cannot delete {path}.")
        # If path is a file
        if path.suffix:
            file_id = self.get_id(path, self.proteomics)
            self.client.file(file_id).delete()
        # If path is a folder
        else:
            folder_id = self.get_id(path, self.proteomics)
            self.client.folder(folder_id).delete(**kwargs)

    def get_folder_contents(self, path: Path) -> list[str]:
        """Get folder contents"""
        if path.suffix:
            raise ValueError(f"{path} is not a folder.")
        folder_id = self.get_id(path, self.proteomics)
        folder = self.client.folder(folder_id).get()
        return [item.name for item in folder.get_items()]

    def exists(self, path: Path) -> bool:
        """Check if path exists in Box"""
        try:
            self.get_id(path, self.proteomics)
            return True
        except FileNotFoundError:
            return False
