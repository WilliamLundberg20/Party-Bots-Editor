bl_info = {
    "name": "Party Bots Editor Add-on",
    "author": "William",
    "version": (0, 0, 1),
    "blender": (4, 2, 1),
    "location": "View3D > Sidebar > Party Bots Editor",
    "description": "Click N to open the sidebar.",
    "category": "Object",
    "tracker_url": "https://discord.gg/HdtZgu7A",
}

import bpy
from bpy.props import StringProperty
import os
import getpass

# Base class for the tab system
class SimplePanelBase:
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Party Bots Editor'

# Panel: Text Input
class SimplePanelTab1(SimplePanelBase, bpy.types.Panel):
    bl_label = "Text Input"
    bl_idname = "PT_PartyBotsEditor_TextInput"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        layout.prop(scene, "text_input_1", text="Name")
        layout.prop(scene, "text_input_2", text="Description")
        layout.prop(scene, "select_path", text="File Path")
        layout.operator("wm.export_to_party")

# Consolidated Info Panel
class SimplePanelInfo(SimplePanelBase, bpy.types.Panel):
    bl_label = "Add-on Info"
    bl_idname = "PT_PartyBotsEditor_Info"

    def draw(self, context):
        layout = self.layout

        layout.label(text="Party Bots Editor Add-on")
        layout.label(text=f"Author: {bl_info['author']}")
        layout.label(text=f"Version: {'.'.join(map(str, bl_info['version']))}")
        layout.label(text="Description: Custom properties for objects.")
        layout.label(text=bl_info['description'])
        layout.operator("wm.url_open", text="Report Issue").url = bl_info['tracker_url']

# Export operator class
class ExportToParty(bpy.types.Operator):
    bl_idname = "wm.export_to_party"
    bl_label = "Export to .party"

    def execute(self, context):
        input_1 = context.scene.text_input_1
        input_2 = context.scene.text_input_2
        file_path = context.scene.select_path

        if not file_path:
            self.report({'ERROR'}, "No file path selected.")
            return {'CANCELLED'}

        if not file_path.endswith(".party"):
            file_path = os.path.join(file_path, '20.party')

        try:
            with open(bpy.path.abspath(file_path), 'w') as file:
                file.write(f"#1:4\n")
                file.write(f"[info]\n")
                file.write(f'name "{input_1}"\n')
                file.write(f'desc "{input_2}"\n')
                file.write(f"[variants]\n")

                for collection in bpy.data.collections:
                    file.write(f'{{{collection.name}}}\n')
                    file.write(" [info]\n")
                    for key, value in collection.items():
                        file.write(f' {key} {value}\n')
                    file.write(f" [platforms]\n")
                    for obj in collection.objects:
                        loc = obj.location
                        sca = obj.scale
                        Xsize = loc.x / 2
                        Ysize = loc.z / 2 + 15
                        Zsize = loc.y / 2

                        file.write(f' {{{obj.name}}}\n')
                        file.write(f"  [layout]\n")
                        file.write(f"  x {Xsize:.2f}\n")
                        file.write(f"  y {Ysize:.2f}\n")
                        file.write(f"  z {Zsize:.2f}\n")
                        file.write(f"  size {sca.x:.1f}\n")
                        file.write(f"  vertical_size {sca.z:.1f}\n")

                        for key, value in obj.items():
                            if "material" in key.lower():
                                materials = {1: "grass", 2: "snow", 3: "slime", 4: "steel", 5: "wood"}
                                if value in materials:
                                    file.write(f"  material {materials[value]}\n")
                            if "spawn_point" in key.lower():
                                file.write(f"  spawn_point {'true' if value else 'false'}\n")

                        file.write("  [info]\n")
                        for key, value in obj.items():
                            if "color" in key.lower():
                                file.write(f'  {key}: {value}\n')

            self.report({'INFO'}, f"Data exported to {file_path}")
        except Exception as e:
            self.report({'ERROR'}, f"Failed to write to file: {e}")
            return {'CANCELLED'}

        return {'FINISHED'}

def register():
    username = getpass.getuser()
    default_path = os.path.join("C:\\Users", username, "AppData\\LocalLow\\Party Bots\\Party Bots\\GameModes")

    bpy.utils.register_class(SimplePanelTab1)
    bpy.utils.register_class(SimplePanelInfo)
    bpy.utils.register_class(ExportToParty)

    bpy.types.Scene.text_input_1 = StringProperty(name="Input 1", default="Untitled")
    bpy.types.Scene.text_input_2 = StringProperty(name="Input 2", default="No description")
    bpy.types.Scene.select_path = StringProperty(
        name="Select Path",
        description="Select a file path",
        default=default_path,
        subtype='FILE_PATH',
    )

def unregister():
    bpy.utils.unregister_class(SimplePanelTab1)
    bpy.utils.unregister_class(SimplePanelInfo)
    bpy.utils.unregister_class(ExportToParty)

    del bpy.types.Scene.text_input_1
    del bpy.types.Scene.text_input_2
    del bpy.types.Scene.select_path

if __name__ == "__main__":
    register()
