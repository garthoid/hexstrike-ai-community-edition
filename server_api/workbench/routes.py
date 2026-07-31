from flask import Blueprint, jsonify, request

from server_core.singletons import db
from server_core.workbench.registry import CATEGORIES, get_operation, list_operations

api_workbench_bp = Blueprint("api_workbench", __name__)


@api_workbench_bp.route("/api/workbench/operations", methods=["GET"])
def workbench_operations():
    return jsonify(
        {
            "success": True,
            "categories": CATEGORIES,
            "operations": [op.to_dict() for op in list_operations()],
        }
    )


@api_workbench_bp.route("/api/workbench/run/<operation_id>", methods=["POST"])
def workbench_run(operation_id: str):
    op = get_operation(operation_id)
    if op is None:
        return jsonify({"success": False, "error": f"Unknown operation: {operation_id}"})

    params = request.get_json(silent=True) or {}
    try:
        result = op.run(params)
    except ValueError as e:
        return jsonify({"success": False, "error": str(e)})
    except Exception as e:
        return jsonify({"success": False, "error": f"Operation failed: {e}"})

    return jsonify({"success": True, **result})


@api_workbench_bp.route("/api/workbench/run-recipe", methods=["POST"])
def workbench_run_recipe():
    body = request.get_json(silent=True) or {}
    current = body.get("input", "")
    step_results = []

    for step in body.get("steps") or []:
        operation_id = step.get("operation_id")
        op = get_operation(operation_id)
        if op is None:
            error = f"Unknown operation: {operation_id}"
            step_results.append({"operation_id": operation_id, "error": error})
            return jsonify({"success": False, "error": error, "steps": step_results})

        params = dict(step.get("params") or {})
        params["input"] = current
        try:
            result = op.run(params)
        except ValueError as e:
            step_results.append({"operation_id": operation_id, "name": op.name, "error": str(e)})
            return jsonify({"success": False, "error": str(e), "steps": step_results})
        except Exception as e:
            error = f"Operation failed: {e}"
            step_results.append({"operation_id": operation_id, "name": op.name, "error": error})
            return jsonify({"success": False, "error": error, "steps": step_results})

        current = result.get("output", "")
        step_results.append({"operation_id": operation_id, "name": op.name, "output": current})

    return jsonify({"success": True, "output": current, "steps": step_results})


@api_workbench_bp.route("/api/workbench/recipes", methods=["GET"])
def workbench_list_recipes():
    return jsonify({"success": True, "recipes": db.list_workbench_recipes()})


@api_workbench_bp.route("/api/workbench/recipes", methods=["POST"])
def workbench_create_recipe():
    body = request.get_json(silent=True) or {}
    name = (body.get("name") or "").strip()
    if not name:
        return jsonify({"success": False, "error": "Recipe name must not be empty"})
    steps = body.get("steps") or []
    recipe_id = db.add_workbench_recipe(name, steps)
    return jsonify({"success": True, "recipe": db.get_workbench_recipe(recipe_id)})


@api_workbench_bp.route("/api/workbench/recipes/<recipe_id>", methods=["GET"])
def workbench_get_recipe(recipe_id: str):
    recipe = db.get_workbench_recipe(recipe_id)
    if recipe is None:
        return jsonify({"success": False, "error": f"Unknown recipe: {recipe_id}"})
    return jsonify({"success": True, "recipe": recipe})


@api_workbench_bp.route("/api/workbench/recipes/<recipe_id>", methods=["PATCH"])
def workbench_update_recipe(recipe_id: str):
    if db.get_workbench_recipe(recipe_id) is None:
        return jsonify({"success": False, "error": f"Unknown recipe: {recipe_id}"})
    body = request.get_json(silent=True) or {}
    fields = {}
    if "name" in body:
        name = (body.get("name") or "").strip()
        if not name:
            return jsonify({"success": False, "error": "Recipe name must not be empty"})
        fields["name"] = name
    if "steps" in body:
        fields["steps"] = body.get("steps") or []
    db.update_workbench_recipe(recipe_id, **fields)
    return jsonify({"success": True, "recipe": db.get_workbench_recipe(recipe_id)})


@api_workbench_bp.route("/api/workbench/recipes/<recipe_id>", methods=["DELETE"])
def workbench_delete_recipe(recipe_id: str):
    if db.get_workbench_recipe(recipe_id) is None:
        return jsonify({"success": False, "error": f"Unknown recipe: {recipe_id}"})
    db.delete_workbench_recipe(recipe_id)
    return jsonify({"success": True})
