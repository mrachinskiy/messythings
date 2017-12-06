from bpy.types import Operator


class OBJECT_OT_MessyThings_Normalize_Display(Operator):
	"""Disable Double Sided, enable Draw All Edges, SubD modifier match render to viewport subdivision level for all objects in the scene"""
	bl_label = 'Messy Things Normalize Object Display'
	bl_idname = 'object.messythings_normalize_display'
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		return context.mode == 'OBJECT'

	def execute(self, context):
		for ob in context.scene.objects:
			ob.hide = False

			if ob.type == 'MESH':
				ob.show_all_edges = True
				ob.data.show_double_sided = False

			if ob.modifiers:
				for mod in ob.modifiers:
					if mod.type == 'SUBSURF':
						mod.render_levels = mod.levels

		self.report({'INFO'}, 'Objects display normalized')

		return {'FINISHED'}
