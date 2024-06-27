# SPDX-FileCopyrightText: 2017-2024 Mikhail Rachinskiy
# SPDX-License-Identifier: GPL-3.0-or-later

import bpy


def purge_materials() -> int:
    count = 0

    for mat in bpy.data.materials:
        if not mat.is_grease_pencil:
            bpy.data.materials.remove(mat)
            count += 1

    for ob in bpy.context.scene.objects:
        if ob.type == "GPENCIL":
            continue
        if ob.material_slots:
            with bpy.context.temp_override(object=ob):
                for _ in ob.material_slots:
                    bpy.ops.object.material_slot_remove()

    return count


def purge_gpencil() -> int:
    count = 0
    excluded = set()

    for ob in bpy.context.scene.objects:
        if ob.type == "GPENCIL":
            excluded.add(ob.data)

    for gp in bpy.data.grease_pencils:
        if gp not in excluded:
            bpy.data.grease_pencils.remove(gp)
            count += 1

    return count


_mod_ob_prop = {
    "NODES": "node_group",
    "BOOLEAN": "object",
    "CURVE": "object",
    "LATTICE": "object",
    "MESH_DEFORM": "object",
    "SHRINKWRAP": "target",
}


def cleanup_modifiers() -> int:
    count = 0

    for ob in bpy.context.scene.objects:
        if ob.modifiers:
            for mod in ob.modifiers:
                if (prop := _mod_ob_prop.get(mod.type)) and getattr(mod, prop) is None:
                    ob.modifiers.remove(mod)
                    count += 1

    return count


def cleanup_objects() -> tuple[int, int, int]:
    obs_to_del = set()
    obs_in_use = set()
    curve_del_count = 0
    lat_del_count = 0
    mesh_del_count = 0

    # Get objects

    for ob in bpy.context.scene.objects:
        ob.hide_viewport = False
        ob.hide_set(False)

        if ob.type in {"CURVE", "LATTICE"}:
            obs_to_del.add(ob)

        elif ob.type == "MESH" and not ob.data.vertices:
            ob_del = True

            if ob.modifiers:
                for mod in ob.modifiers:
                    if mod.type == "BOOLEAN" and mod.operation == "UNION" and mod.object:
                        ob_del = False  # Booltron combined object
                        break

            if ob_del:
                obs_to_del.add(ob)

        # Object dependencies

        if ob.modifiers:
            for mod in ob.modifiers:
                if mod.type in {"CURVE", "LATTICE"} and mod.object:
                    obs_in_use.add(mod.object)

        if ob.constraints:
            for con in ob.constraints:
                if con.type == "FOLLOW_PATH" and con.target:
                    obs_in_use.add(con.target)

        if ob.type == "CURVE":
            if ob.data.bevel_object:
                obs_in_use.add(ob.data.bevel_object)
            if ob.data.taper_object:
                obs_in_use.add(ob.data.taper_object)

    # Remove objects

    if obs_to_del:
        for ob in obs_to_del:
            if ob not in obs_in_use:

                if ob.type == "CURVE":
                    curve_del_count += 1
                elif ob.type == "LATTICE":
                    lat_del_count += 1
                elif ob.type == "MESH":
                    mesh_del_count += 1

                bpy.data.objects.remove(ob)

    # Report

    for area in bpy.context.screen.areas:
        area.tag_redraw()

    return curve_del_count, lat_del_count, mesh_del_count
