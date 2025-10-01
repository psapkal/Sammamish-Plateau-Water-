import arcpy, os

class mytable:
    def __init__(self, table):
        """
        Initialize the MyTable object with table metadata.

        Args:
            table (str): Full path to the ArcGIS table or feature class

        Raises:
            arcpy.ExecuteError: If the table cannot be described or doesn't exist
        """
        try:
            # Get table description using ArcPy
            desc = arcpy.Describe(table)

            # Store table metadata
            self.basename = desc.basename
            self.path = desc.path
            self.isversioned = desc.isVersioned
            self.table = os.path.join(self.path, self.basename)

        except Exception as e:
            print(f"Error describing table {table}: {str(e)}")
            raise

    def get_basename(self):
        """
        Get the table basename (name without path).

        Returns:
            str: The table basename
        """
        return self.basename

    def get_path(self):
        """
        Get the table workspace path.

        Returns:
            str: The workspace path
        """
        return self.path

    def get_isversioned(self):
        """
        Check if the table is versioned.

        Returns:
            bool: True if table is versioned, False otherwise
        """
        return self.isversioned

    def get_table(self):
        """
        Get the full table path.

        Returns:
            str: The complete table path
        """
        return self.table

    def updatetable(self, sourcetable):
        """
        Update the target table with data from a source table.

        This method intelligently chooses between DeleteRows (for versioned tables)
        and TruncateTable (for non-versioned tables) for optimal performance.
        After clearing the target table, it appends all data from the source table.

        Args:
            sourcetable (str): Path to the source table containing new data

        Raises:
            arcpy.ExecuteError: If any ArcPy operation fails

        Process:
            1. Check if target table is versioned
            2. Clear existing data using appropriate method:
               - Versioned: DeleteRows (maintains version history)
               - Non-versioned: TruncateTable (faster performance)
            3. Append new data from source table using NO_TEST schema matching
        """
        if self.isversioned:
            arcpy.DeleteRows_management(self.table)
            arcpy.Append_management(sourcetable, self.table, "NO_TEST", "", "")
        else:
            print ("not versioned " + sourcetable)
            arcpy.TruncateTable_management(self.table)
            arcpy.Append_management(sourcetable, self.table, "NO_TEST", "", "")
