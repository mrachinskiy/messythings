bl_info = {
	'name': 'Messy Things',
	'author': 'Mikhail Rachinskiy',
	'version': (1, 0, 0),
	'blender': (2, 79, 0),
	'location': '3D View > Tool Shelf > Tools',
	'description': 'Deal with badly organized projects.',
	'wiki_url': '',
	'tracker_url': '',
	'category': 'Scene',
	}


if 'bpy' in locals():
	import importlib
	importlib.reload(ops_cleanup)
	importlib.reload(ops_layer)
	importlib.reload(ops_object)
	importlib.reload(ops_scene)
	importlib.reload(ui)
else:
	import bpy

	from . import (
		ops_cleanup,
		ops_layer,
		ops_object,
		ops_scene,
		ui,
		)


classes = (
	ui.VIEW3D_PT_prokit,

	ops_cleanup.OBJECT_OT_MessyThings_Cleanup_Modifiers,
	ops_cleanup.OBJECT_OT_MessyThings_Cleanup_Objects,
	ops_cleanup.SCENE_OT_MessyThings_Cleanup_Grease_Pencil,
	ops_cleanup.SCENE_OT_MessyThings_Cleanup_Materials,

	ops_layer.OBJECT_OT_MessyThings_Get_Misplaced_Dependencies,
	ops_layer.OBJECT_OT_MessyThings_Sort_By_Layers,

	ops_object.OBJECT_OT_MessyThings_Normalize_Display,

	ops_scene.SCENE_OT_MessyThings_Apply_Render_Profile,
	)


def register():
	for cls in classes:
		bpy.utils.register_class(cls)


def unregister():
	for cls in classes:
		bpy.utils.unregister_class(cls)


if __name__ == '__main__':
	register()
