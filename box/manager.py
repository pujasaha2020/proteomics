"""Provide user with utility functions for box"""

import io
from pathlib import Path

from boxsdk.object.folder import Folder

from box.oauth2 import get_box_client

###################################################
FOLDER_ID = "200099021915"  # Proteomics folder id
###################################################


class BoxManager:
    """Provide user with utility functions for box"""

    def __init__(self):
        # show current pwd
        self.token_path = Path("box/tokens.yaml")
        if self.token_path.exists():
            self.client = get_box_client()
            self.proteomics = self.client.folder(folder_id=FOLDER_ID).get()
        else:
            print("Box token file is not accessible.")

    def get_id(self, path: Path, folder: Folder) -> str:
        """Get box file id (recursive)"""
        parts = path.parts
        # If path is just the file's name
        if len(parts) == 1:
            for item in folder.get_items():
                if item.name == parts[0]:
                    return item.id
            raise FileNotFoundError(f"File {path} not found in Box")
        # If the path includes at least a parent folder
        for item in folder.get_items():
            if item.name == parts[0]:
                return self.get_id(Path(*parts[1:]), item)
        raise FileNotFoundError(f"File {path} not found in Box")

    def get_file(self, path: Path) -> io.StringIO:
        """Get box file"""
        file_id = self.get_id(path, self.proteomics)
        file = self.client.file(file_id=file_id).get()
        return io.StringIO(file.content().decode("utf-8"))
