import os
import pandas as pd

# Helper functions
def getattr(item: str, data: dict):
    if item in data:
        return data[item]
    raise AttributeError(f"'{type(data).__name__}' object has no attribute '{item}'")


class Section:
    """
        Represents a section, containing properties loaded from a CSV file.
    """

    def __init__(self, name: str, properties: dict):
        self.name = name
        self.properties = properties

    def __getattr__(self, item):
        return getattr(item, self.properties)

class Family:
    """
    Represents a family of sections, containing multiple Section objects loaded from a CSV file.
    """

    def __init__(self, name: str, path: str):
        self.name = name
        self.path = path
        self.sections = self._load_sections()

    def __repr__(self):
        return f"Group(name={self.name}, path={self.path})"

    def _load_sections(self):
        sections = {}

        # Load the csv files into a pandas dataframe
        df = pd.read_csv(self.path)

        # Check if the dataframe is empty
        if df.empty:
            raise ValueError(f"No sections found in family '{self.name}' at path '{self.path}'")

        # Iterate through rows and create Section objects
        for _, row in df.iterrows():
            section_name = row.iloc[0]
            section_properties = row.iloc[1:].to_dict()
            sections[section_name] = Section(section_name, section_properties)
        return sections

    def __getattr__(self, name):
        return getattr(name, self.sections)

class Group:
    """
        Represents a group of section families, containing multiple Family objects loaded from CSV files.
    """

    def __init__(self, name: str, path: str):
        self.name = name
        self.path = path
        self.families = self._load_families()

    def __repr__(self):
        return f"Group(name={self.name}, path={self.path})"

    def _load_families(self):
        families = {}
        for file in os.listdir(self.path):
            if file.endswith(".csv"):
                family_name = file.split(".")[0]
                families[family_name] = Family(family_name, os.path.join(self.path, file))
        if not families:
            raise ValueError(f"No families found in group '{self.name}' at path '{self.path}'")
        return families

    def __getattr__(self, name):
        return getattr(name, self.families)

# Get data directories

#   Get package data
PACKAGE_DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

#   Get custom user data directory

HOME_DIR = os.path.expanduser("~/.sections_data")
CUSTOM_DATA_DIR = os.getenv("SECTIONS_DATA", HOME_DIR)

#   Get list of data directories

DATA_DIRS = [PACKAGE_DATA_DIR]
if os.path.exists(CUSTOM_DATA_DIR):
    DATA_DIRS.append(CUSTOM_DATA_DIR)

#   Load groups from data directories

groups = {}

for path in DATA_DIRS:
    for group_name in os.listdir(path):
        group_path = os.path.join(path, group_name)
        if os.path.isdir(group_path) and group_name not in groups:
            groups[group_name] = Group(group_name, group_path)

# Update globals with loaded groups
globals().update(groups)

# Set __all__ to include group names
__all__ = list(groups.keys())

# TODO: Add handling for duplicate group names
# TODO: Add handling for empty group folders
# TODO: Add handling for empty family csv files
