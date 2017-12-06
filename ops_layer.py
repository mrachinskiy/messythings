from bpy.types import Operator


class OBJECT_OT_MessyThings_Get_Misplaced_Dependencies(Operator):
	"""Get to active layer objects used in modifiers and constraints by visible objects, but located in hidden layers"""
	bl_label = 'Messy Things Get Misplaced Dependencies'
	bl_idname = 'object.messythings_get_misplaced_dependencies'
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		return context.mode == 'OBJECT'

	def execute(self, context):
		scene = context.scene
		active_layer = scene.active_layer
		dep_obs = set()

		for ob in context.visible_objects:
			ob.select = False

			if ob.modifiers:
				for mod in ob.modifiers:
					if ((mod.type in {'CURVE', 'LATTICE', 'BOOLEAN'} and mod.object) or
					   (mod.type == 'SHRINKWRAP' and mod.target)):

						mod_ob = mod.target if mod.type == 'SHRINKWRAP' else mod.object
						mod_ob.hide = False

						if not mod_ob.is_visible(scene):
							mod_ob.layers[active_layer] = True
							mod_ob.select = True
							dep_obs.add(mod_ob)

			if ob.constraints:
				for con in ob.constraints:
					if con.type == 'FOLLOW_PATH' and con.target:

						con.target.hide = False

						if not con.target.is_visible(scene):
							con.target.layers[active_layer] = True
							con.target.select = True
							dep_obs.add(con.target)

		if dep_obs:
			for ob in dep_obs:
				scene.objects.active = ob
				break

		self.report({'INFO'}, '{} misplaced objects'.format(len(dep_obs)))

		return {'FINISHED'}


class OBJECT_OT_MessyThings_Sort_By_Layers(Operator):
	"""Move Curve, Lattice, Empty and Mesh (with draw type: Wire and Bounds) objets to bottom layers; and Curve with bevel profile and Mesh objects to top layers"""
	bl_label = 'Messy Things Sort Objects By Layers'
	bl_idname = 'object.messythings_sort_by_layers'
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		return context.mode == 'OBJECT'

	def execute(self, context):
		top_layers = range(0, 10)
		bottom_layers = range(10, 20)
		obs_sorted_top = 0
		obs_sorted_bottom = 0

		for ob in context.scene.objects:
			ob.hide = False

			if ((ob.type == 'MESH' and ob.draw_type in {'TEXTURED', 'SOLID'}) or
			   (ob.type == 'CURVE' and (ob.data.bevel_depth or ob.data.bevel_object))):
				i = 0
				for l in bottom_layers:
					if ob.layers[l]:
						ob.layers[l - 10] = True
						ob.layers[l] = False
						i = 1
				obs_sorted_top += i

			elif ob.type in {'CURVE', 'LATTICE', 'EMPTY', 'MESH'}:
				i = 0
				for l in top_layers:
					if ob.layers[l]:
						ob.layers[l + 10] = True
						ob.layers[l] = False
						i = 1
				obs_sorted_bottom += i

		self.report({'INFO'}, 'Objects sorted: {} to top layers, {} to bottom layers'.format(obs_sorted_top, obs_sorted_bottom))

		return {'FINISHED'}
