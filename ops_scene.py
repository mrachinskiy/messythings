from bpy.types import Operator


class SCENE_OT_MessyThings_Apply_Render_Profile(Operator):
	"""Apply render profile"""
	bl_label = 'Messy Things Apply Render Profile'
	bl_idname = 'object.messythings_apply_render_profile'
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		return context.mode == 'OBJECT'

	def execute(self, context):
		scene = context.scene

		render = scene.render

		render.resolution_x = 1080
		render.resolution_y = 1080
		render.resolution_percentage = 100
		render.image_settings.file_format = 'PNG'
		render.image_settings.color_mode = 'RGBA'
		render.image_settings.compression = 100
		render.display_mode = 'SCREEN'

		cycles = scene.cycles

		cycles.film_transparent = True
		cycles.device = 'GPU'
		cycles.pixel_filter_type = 'BLACKMAN_HARRIS'
		cycles.progressive = 'PATH'
		cycles.use_square_samples = False
		cycles.samples = 100
		cycles.preview_samples = 10
		cycles.sample_clamp_indirect = 10.0
		cycles.light_sampling_threshold = 0.01
		cycles.tile_order = 'TOP_TO_BOTTOM'

		scene.view_settings.view_transform = 'Filmic'
		scene.view_settings.look = 'None'

		return {'FINISHED'}
