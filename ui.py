from bpy.types import Panel


class VIEW3D_PT_prokit(Panel):
	bl_category = 'Tools'
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'TOOLS'
	bl_label = 'Messy Things'
	bl_context = 'objectmode'
	bl_options = {'DEFAULT_CLOSED'}

	def draw(self, context):
		layout = self.layout

		col = layout.column(align=True)
		col.label('Render Profile:')
		col.operator('object.messythings_apply_render_profile', text='Jewelry', icon='SCENE')

		col = layout.column(align=True)
		col.label('Layers:')
		col.operator('object.messythings_get_misplaced_dependencies', text='Get Dependencies', icon='LINKED')
		col.operator('object.messythings_sort_by_layers', text='Sort Objects', icon='OOPS')

		col = layout.column(align=True)
		col.label('Objects:')
		col.operator('object.messythings_normalize_display', text='Normalize Display', icon='WIRE')

		col = layout.column(align=True)
		col.label('Clenup:')
		col.operator('object.messythings_cleanup_modifiers', text='Modifiers', icon='MODIFIER')
		col.operator('object.messythings_cleanup_objects', text='Objects', icon='OBJECT_DATA')
		col.operator('scene.messythings_cleanup_grease_pencil', text='Grease Pencil', icon='GREASEPENCIL')
		col.operator('scene.messythings_cleanup_materials', text='Materials', icon='MATERIAL')
