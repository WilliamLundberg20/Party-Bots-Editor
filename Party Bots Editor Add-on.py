bl_info = {
    "name": "Party Bots Editor Add-on",
    "author": "William",
    "version": (0, 0, 3),
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


# Consolidated Info Panel
class GameModeSettings(SimplePanelBase, bpy.types.Panel):
    bl_label = "Game Mode Settings"
    bl_idname = "PT_PartyBotsEditor_GameMode"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        # Collapsible section for Game Mode Settings
        box = layout.box()
        box.label(text="Game Mode Information", icon="FILE_BLEND")

        box.label(text="Game Mode Name", icon="DOT")
        box.prop(scene, "text_input_1", text="")

        box.label(text="Game Mode Description", icon="DOT")
        box.prop(scene, "text_input_2", text="")

        box.label(text="Game Mode Save Path", icon="DOT")
        box.prop(scene, "select_path", text="")

        # Operators with icons
        row = layout.row()
        row.scale_y = 1.2
        row.operator("wm.export_to_party", icon='EXPORT', text="Export to .party")
        row.operator("wm.open_partybots_window", icon='WINDOW', text="Variants Settings")


class AddonInfoPanel(SimplePanelBase, bpy.types.Panel):
    bl_label = "Add-on Information"
    bl_idname = "PT_PartyBotsEditor_Info"

    def draw(self, context):
        layout = self.layout

        # Add-on info in a box layout
        box = layout.box()
        box.label(text="Party Bots Editor", icon="INFO")
        box.label(text=f"Author: {bl_info['author']}")
        box.label(text=f"Version: {'.'.join(map(str, bl_info['version']))}")
        box.label(text=bl_info['description'])
        box.operator("wm.url_open", text="Report an Issue", icon="ERROR").url = bl_info['tracker_url']


# Operator for Exporting
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
                        rot = obj.rotation_euler
                        sca = obj.scale
                        Xsize = loc.x / 2
                        Ysize = loc.z / 2 + 15
                        Zsize = loc.y / 2
                        Xrot = rot.x * -115 / 2
                        Yrot = rot.z * -115 / 2
                        Zrot = rot.y * -115 / 2

                        file.write(f' {{{obj.name}}}\n')
                        file.write(f"  [layout]\n")
                        file.write(f"  x {Xsize:.2f}\n")
                        file.write(f"  y {Ysize:.2f}\n")
                        file.write(f"  z {Zsize:.2f}\n")
                        file.write(f"  size {sca.x:.1f}\n")
                        file.write(f"  vertical_size {sca.z:.1f}\n")

                        # Handle rotation and properties
                        for key, value in obj.items():
                            if "material" in key.lower():
                                materials = {1: "grass", 2: "snow", 3: "slime", 4: "steel", 5: "wood"}
                                if value in materials:
                                    file.write(f"  material {materials[value]}\n")
                            if "spawn_point" in key.lower():
                                file.write(f"  spawn_point {'true' if value else 'false'}\n")
                            if "id" in key.lower():
                                file.write(f'  {key} {value}\n')
                            if "tags" in key.lower():
                                file.write(f'  {key} {value}\n')

                        file.write(f"  x_rotation {Xrot:.0f}\n")
                        file.write(f"  y_rotation {Yrot:.0f}\n")
                        file.write(f"  z_rotation {Zrot:.0f}\n")

                        file.write("  [info]\n")
                        for key, value in obj.items():
                            if "color" in key.lower():
                                file.write(f'  {key} {value}\n')

            self.report({'INFO'}, f"Data exported to {file_path}")
        except IOError as e:
            self.report({'ERROR'}, f"Failed to write to file: {e.strerror}")
            return {'CANCELLED'}
        except Exception as e:
            self.report({'ERROR'}, f"An unexpected error occurred: {e}")
            return {'CANCELLED'}

        return {'FINISHED'}


# Operator for opening a custom window with more functionality
class OpenPartyBotsWindow(bpy.types.Operator):
    bl_idname = "wm.open_partybots_window"
    bl_label = "Variants Settings Window"

    def draw(self, context):
        layout = self.layout
        layout.label(text="Settings will be added here soon.", icon="WINDOW")
        # You could add properties or inputs here for the variants

    def execute(self, context):
        return context.window_manager.invoke_props_dialog(self)

# Registering scene properties with max_length
def register():
    username = getpass.getuser()
    default_path = os.path.join("C:\\Users", username, "AppData\\LocalLow\\Party Bots\\Party Bots\\GameModes")

    bpy.utils.register_class(GameModeSettings)
    bpy.utils.register_class(AddonInfoPanel)
    bpy.utils.register_class(ExportToParty)
    bpy.utils.register_class(OpenPartyBotsWindow)

    bpy.types.Scene.text_input_1 = StringProperty(name="Input 1", default="Untitled", maxlen=50)
    bpy.types.Scene.text_input_2 = StringProperty(name="Input 2", default="No description", maxlen=100)
    bpy.types.Scene.select_path = StringProperty(
        name="Select Path",
        description="Select a file path",
        default=default_path,
        subtype='FILE_PATH',
    )

def unregister():
    bpy.utils.unregister_class(GameModeSettings)
    bpy.utils.unregister_class(AddonInfoPanel)
    bpy.utils.unregister_class(ExportToParty)
    bpy.utils.unregister_class(OpenPartyBotsWindow)

    del bpy.types.Scene.text_input_1
    del bpy.types.Scene.text_input_2
    del bpy.types.Scene.select_path

if __name__ == "__main__":
    register()
