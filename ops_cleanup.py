import bpy
from bpy.types import Operator


class OBJECT_OT_MessyThings_Cleanup_Modifiers(Operator):
	"""Remove Curve, Lattice, Boolean and Shrinkwrap modifiers with empty Object/Target field"""
	bl_label = 'Messy Things Cleanup Modifiers'
	bl_idname = 'object.messythings_cleanup_modifiers'
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		return context.mode == 'OBJECT'

	def execute(self, context):
		mod_del_types = {'CURVE', 'LATTICE', 'BOOLEAN'}
		mod_del_count = 0

		for ob in context.scene.objects:
			ob.hide = False

			if ob.modifiers:
				for mod in ob.modifiers:
					if (mod.type in mod_del_types and not mod.object) or (mod.type == 'SHRINKWRAP' and not mod.target):
						ob.modifiers.remove(mod)
						mod_del_count += 1

		self.report({'INFO'}, '{} modifiers removed'.format(mod_del_count))

		return {'FINISHED'}


class OBJECT_OT_MessyThings_Cleanup_Objects(Operator):
	"""Remove empty Mesh, Lattice and Curve objects that are not in use by modifiers or constraints"""
	bl_label = 'Messy Things Cleanup Objects'
	bl_idname = 'object.messythings_cleanup_objects'
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		return context.mode == 'OBJECT'

	def execute(self, context):
		ob_del_types = {'CURVE', 'LATTICE'}
		mod_types = {'CURVE', 'LATTICE'}
		obs_to_del = []
		obs_in_use = set()
		obs_del_count = 0

		# Get objects

		for ob in context.scene.objects:
			ob.hide = False

			if ob.type in ob_del_types:
				obs_to_del.append(ob)

			# Empty mesh
			if ob.type == 'MESH' and not ob.data.vertices:
				obs_to_del.append(ob)

			# Object dependencies
			if ob.modifiers:
				for mod in ob.modifiers:
					if mod.type in mod_types and mod.object:
						obs_in_use.add(mod.object)

			if ob.constraints:
				for con in ob.constraints:
					if con.type == 'FOLLOW_PATH' and con.target:
						obs_in_use.add(con.target)

		# Remove objects

		for ob in obs_to_del:
			if ob not in obs_in_use:
				bpy.data.objects.remove(ob)
				obs_del_count += 1

		# Report

		for area in context.screen.areas:
			area.tag_redraw()

		self.report({'INFO'}, '{} objects removed'.format(obs_del_count))

		return {'FINISHED'}


class SCENE_OT_MessyThings_Cleanup_Grease_Pencil(Operator):
	"""Remove all grease pencil datablocks"""
	bl_label = 'Messy Things Cleanup Grease Pencil'
	bl_idname = 'scene.messythings_cleanup_grease_pencil'
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		return context.mode == 'OBJECT'

	def execute(self, context):
		count = len(bpy.data.grease_pencil)

		for gp in bpy.data.grease_pencil:
			bpy.data.grease_pencil.remove(gp)

		self.report({'INFO'}, '{} datablocks removed'.format(count))

		return {'FINISHED'}


class SCENE_OT_MessyThings_Cleanup_Materials(Operator):
	"""Remove all materials from file, additionally remove material slots from objects"""
	bl_label = 'Messy Things Cleanup Materials'
	bl_idname = 'scene.messythings_cleanup_materials'
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		return context.mode == 'OBJECT'

	def execute(self, context):
		scene = context.scene
		active_object = context.active_object
		count = len(bpy.data.materials)

		for mat in bpy.data.materials:
			bpy.data.materials.remove(mat)

		for ob in scene.objects:

			if ob.material_slots:
				scene.objects.active = ob

				while ob.material_slots:
					bpy.ops.object.material_slot_remove()

		scene.objects.active = active_object

		self.report({'INFO'}, '{} materials removed'.format(count))

		return {'FINISHED'}
