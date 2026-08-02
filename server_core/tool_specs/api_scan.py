import base64
import json
import shlex

from server_core.tool_spec import ParamSpec, ToolSpec, ToolValidationError


def _api_schema_analyzer_command(p: dict) -> str:
    return shlex.join(["curl", "-s", p["schema_url"]])


def _api_schema_analyzer_postprocess(raw: dict, p: dict) -> dict:
    if not raw.get("success"):
        raise ToolValidationError("Failed to fetch API schema")

    schema_content = raw.get("stdout", "")
    schema_type = p["schema_type"]

    analysis_results = {
        "schema_url": p["schema_url"],
        "schema_type": schema_type,
        "endpoints_found": [],
        "security_issues": [],
        "recommendations": [],
    }

    try:
        schema_data = json.loads(schema_content)
        if schema_type.lower() in ["openapi", "swagger"]:
            paths = schema_data.get("paths", {})

            for path, methods in paths.items():
                for method, details in methods.items():
                    if isinstance(details, dict):
                        endpoint_info = {
                            "path": path,
                            "method": method.upper(),
                            "summary": details.get("summary", ""),
                            "parameters": details.get("parameters", []),
                            "security": details.get("security", []),
                        }
                        analysis_results["endpoints_found"].append(endpoint_info)

                        if not endpoint_info["security"]:
                            analysis_results["security_issues"].append({
                                "endpoint": f"{method.upper()} {path}",
                                "issue": "no_authentication",
                                "severity": "MEDIUM",
                                "description": "Endpoint has no authentication requirements",
                            })

                        for param in endpoint_info["parameters"]:
                            param_name = param.get("name", "").lower()
                            if any(sensitive in param_name for sensitive in ["password", "token", "key", "secret"]):
                                analysis_results["security_issues"].append({
                                    "endpoint": f"{method.upper()} {path}",
                                    "issue": "sensitive_parameter",
                                    "severity": "HIGH",
                                    "description": f"Sensitive parameter detected: {param_name}",
                                })

        if analysis_results["security_issues"]:
            analysis_results["recommendations"] = [
                "Implement authentication for all endpoints",
                "Use HTTPS for all API communications",
                "Validate and sanitize all input parameters",
                "Implement rate limiting",
                "Add proper error handling",
                "Use secure headers (CORS, CSP, etc.)",
            ]

    except json.JSONDecodeError:
        analysis_results["security_issues"].append({
            "endpoint": "schema",
            "issue": "invalid_json",
            "severity": "HIGH",
            "description": "Schema is not valid JSON",
        })

    return {"success": True, "schema_analysis_results": analysis_results}


def _graphql_scanner_commands(p: dict) -> list:
    commands = []

    if p["introspection"]:
        introspection_query = """
            {
                __schema {
                    types {
                        name
                        fields {
                            name
                            type {
                                name
                            }
                        }
                    }
                }
            }
            """
        clean_query = introspection_query.replace("\n", " ").replace("  ", " ").strip()
        payload = f'{{"query":"{clean_query}"}}'
        commands.append(shlex.join([
            "curl", "-s", "-X", "POST",
            "-H", "Content-Type: application/json",
            "-d", payload, p["endpoint"],
        ]))

    deep_query = "{ " * p["query_depth"] + "field" + " }" * p["query_depth"]
    payload = f'{{"query":"{deep_query}"}}'
    commands.append(shlex.join([
        "curl", "-s", "-X", "POST",
        "-H", "Content-Type: application/json",
        "-d", payload, p["endpoint"],
    ]))

    batch_query = "[" + ",".join(['{"query":"{field}"}' for _ in range(10)]) + "]"
    commands.append(shlex.join([
        "curl", "-s", "-X", "POST",
        "-H", "Content-Type: application/json",
        "-d", batch_query, p["endpoint"],
    ]))

    return commands


def _graphql_scanner_postprocess(raw_list: list, p: dict) -> dict:
    results = {
        "endpoint": p["endpoint"],
        "tests_performed": [],
        "vulnerabilities": [],
        "recommendations": [],
    }
    idx = 0

    if p["introspection"]:
        result = raw_list[idx]
        idx += 1
        results["tests_performed"].append("introspection_query")
        if "data" in result.get("stdout", ""):
            results["vulnerabilities"].append({
                "type": "introspection_enabled",
                "severity": "MEDIUM",
                "description": "GraphQL introspection is enabled",
            })

    depth_result = raw_list[idx]
    idx += 1
    results["tests_performed"].append("query_depth_analysis")
    if "error" not in depth_result.get("stdout", "").lower():
        results["vulnerabilities"].append({
            "type": "no_query_depth_limit",
            "severity": "HIGH",
            "description": f"No query depth limiting detected (tested depth: {p['query_depth']})",
        })

    batch_result = raw_list[idx]
    idx += 1
    results["tests_performed"].append("batch_query_testing")
    if "data" in batch_result.get("stdout", "") and batch_result.get("success"):
        results["vulnerabilities"].append({
            "type": "batch_queries_allowed",
            "severity": "MEDIUM",
            "description": "Batch queries are allowed without rate limiting",
        })

    if results["vulnerabilities"]:
        results["recommendations"] = [
            "Disable introspection in production",
            "Implement query depth limiting",
            "Add rate limiting for batch queries",
            "Implement query complexity analysis",
            "Add authentication for sensitive operations",
        ]

    return {"success": True, "graphql_scan_results": results}


def _jwt_analyzer_commands(p: dict) -> list:
    if not p["target_url"]:
        return []

    none_token_parts = p["jwt_token"].split(".")
    if len(none_token_parts) < 2:
        return []

    none_header = base64.b64encode(b'{"alg":"none","typ":"JWT"}').decode().rstrip("=")
    none_token = f"{none_header}.{none_token_parts[1]}."
    return [shlex.join(["curl", "-s", "-H", f"Authorization: Bearer {none_token}", p["target_url"]])]


def _jwt_analyzer_postprocess(raw_list: list, p: dict) -> dict:
    jwt_token = p["jwt_token"]
    results = {
        "token": jwt_token[:50] + "..." if len(jwt_token) > 50 else jwt_token,
        "vulnerabilities": [],
        "token_info": {},
        "attack_vectors": [],
    }

    try:
        parts = jwt_token.split(".")
        if len(parts) >= 2:
            header_b64 = parts[0] + "=" * (4 - len(parts[0]) % 4)
            payload_b64 = parts[1] + "=" * (4 - len(parts[1]) % 4)

            try:
                header = json.loads(base64.b64decode(header_b64))
                payload = json.loads(base64.b64decode(payload_b64))

                results["token_info"] = {
                    "header": header,
                    "payload": payload,
                    "algorithm": header.get("alg", "unknown"),
                }

                algorithm = header.get("alg", "").lower()

                if algorithm == "none":
                    results["vulnerabilities"].append({
                        "type": "none_algorithm",
                        "severity": "CRITICAL",
                        "description": "JWT uses 'none' algorithm - no signature verification",
                    })

                if algorithm in ["hs256", "hs384", "hs512"]:
                    results["attack_vectors"].append("hmac_key_confusion")
                    results["vulnerabilities"].append({
                        "type": "hmac_algorithm",
                        "severity": "MEDIUM",
                        "description": "HMAC algorithm detected - vulnerable to key confusion attacks",
                    })

                exp = payload.get("exp")
                if not exp:
                    results["vulnerabilities"].append({
                        "type": "no_expiration",
                        "severity": "HIGH",
                        "description": "JWT token has no expiration time",
                    })

            except Exception as decode_error:
                results["vulnerabilities"].append({
                    "type": "malformed_token",
                    "severity": "HIGH",
                    "description": f"Token decoding failed: {str(decode_error)}",
                })

    except Exception:
        results["vulnerabilities"].append({
            "type": "invalid_format",
            "severity": "HIGH",
            "description": "Invalid JWT token format",
        })

    if raw_list:
        none_result = raw_list[0]
        if "200" in none_result.get("stdout", "") or "success" in none_result.get("stdout", "").lower():
            results["vulnerabilities"].append({
                "type": "none_algorithm_accepted",
                "severity": "CRITICAL",
                "description": "Server accepts tokens with 'none' algorithm",
            })

    return {"success": True, "jwt_analysis_results": results}


SPECS = [
    ToolSpec(
        name="api_schema_analyzer",
        mcp_tool_name="api_schema_analyzer",
        endpoint="/api/tools/api_schema_analyzer",
        category="api_scan",
        description="Analyze API schemas and identify potential security issues.",
        params=[
            ParamSpec("schema_url", str, required=True, help_text="URL of the OpenAPI/Swagger/GraphQL schema"),
            ParamSpec("schema_type", str, default="openapi", help_text="Schema type: openapi, swagger, or graphql"),
        ],
        build_command=_api_schema_analyzer_command,
        postprocess=_api_schema_analyzer_postprocess,
    ),
    ToolSpec(
        name="graphql_scanner",
        mcp_tool_name="graphql_scanner",
        endpoint="/api/tools/graphql_scanner",
        category="api_scan",
        description="Advanced GraphQL security scanning and introspection.",
        params=[
            ParamSpec("endpoint", str, required=True, help_text="GraphQL endpoint URL"),
            ParamSpec("introspection", bool, default=True, help_text="Test for introspection being enabled"),
            ParamSpec("query_depth", int, default=10, help_text="Query depth to test for depth-limiting"),
            ParamSpec("test_mutations", bool, default=True, help_text="Test mutation endpoints"),
        ],
        build_command=_graphql_scanner_commands,
        postprocess=_graphql_scanner_postprocess,
    ),
    ToolSpec(
        name="jwt_analyzer",
        mcp_tool_name="jwt_analyzer",
        endpoint="/api/tools/jwt_analyzer",
        category="api_scan",
        description="Advanced JWT token analysis and vulnerability testing.",
        params=[
            ParamSpec("jwt_token", str, required=True, help_text="JWT token to analyze"),
            ParamSpec("target_url", str, default="", help_text="Target URL to test token manipulation attacks against"),
        ],
        build_command=_jwt_analyzer_commands,
        postprocess=_jwt_analyzer_postprocess,
    ),
]
