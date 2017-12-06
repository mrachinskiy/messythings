from bpy.types import Operator


class OBJECT_OT_MessyThings_Get_Misplaced_Dependencies(Operator):
	"""Get to active layer objects used in modifiers by visible objects, but located in hidden layers"""
	bl_label = 'Messy Things Get Misplaced Dependencies'
	bl_idname = 'object.messythings_get_misplaced_dependencies'
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		return context.mode == 'OBJECT'

	def execute(self, context):
		scene = context.scene
		active_layer = scene.active_layer
		mod_types = {'CURVE', 'LATTICE', 'BOOLEAN'}
		dep_obs = set()

		for ob in context.visible_objects:
			ob.select = False

			if ob.modifiers:
				for mod in ob.modifiers:
					if (mod.type in mod_types and mod.object) or (mod.type == 'SHRINKWRAP' and mod.target):
						mod.object.hide = False

						if not mod.object.is_visible(scene):
							mod.object.layers[active_layer] = True
							mod.object.select = True
							dep_obs.add(mod.object)
							break

		if dep_obs:
			scene.objects.active = mod.object

		self.report({'INFO'}, '{} misplaced objects'.format(len(dep_obs)))

		return {'FINISHED'}


class OBJECT_OT_MessyThings_Sort_By_Layers(Operator):
	"""Move Curve, Lattice and Empty objets to bottom layers"""
	bl_label = 'Messy Things Sort Objects By Layers'
	bl_idname = 'object.messythings_sort_by_layers'
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		return context.mode == 'OBJECT'

	def execute(self, context):
		ob_helper_types = {'CURVE', 'LATTICE', 'EMPTY'}
		top_layers = range(0, 10)
		bottom_layers = range(10, 20)
		ob_helper_sorted = 0
		ob_mesh_sorted = 0

		for ob in context.scene.objects:
			ob.hide = False

			if ob.type == 'MESH' or (ob.type == 'CURVE' and (ob.data.bevel_depth or ob.data.bevel_object)):
				i = 0
				for l in bottom_layers:
					if ob.layers[l]:
						ob.layers[l - 10] = True
						ob.layers[l] = False
						i = 1
				ob_mesh_sorted += i

			elif ob.type in ob_helper_types:
				i = 0
				for l in top_layers:
					if ob.layers[l]:
						ob.layers[l + 10] = True
						ob.layers[l] = False
						i = 1
				ob_helper_sorted += i

		self.report({'INFO'}, 'Sorted: {} helper objects, {} mesh objects'.format(ob_helper_sorted, ob_mesh_sorted))

		return {'FINISHED'}
