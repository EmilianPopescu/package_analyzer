import re
import json

def parse_yarn_lock(yarn_lock_path):
    dependency_regex = re.compile(r'^"?(.+?)@.+?":$')  # Matches the dependency name
    version_regex = re.compile(r'^\s*version\s+"(.+)"$')  # Matches the version line

    dependencies = {}
    current_name = None

    with open(yarn_lock_path, 'r') as file:
        for line in file:
            line = line.strip()
            dep_match = dependency_regex.match(line)
            ver_match = version_regex.match(line)

            if dep_match:
                current_name = dep_match.group(1)
            elif ver_match and current_name:
                version = ver_match.group(1)
                dependencies[current_name] = version
                current_name = None

    return dependencies

def generate_dependencies_json(dependencies, output_file):
    trees = [{"name": f"{name}@{version}"} for name, version in dependencies.items()]

    dependency_tree = {
        "type": "tree",
        "data": {
            "type": "list",
            "trees": trees
        }
    }
    with open(output_file, 'w') as json_file:
        json.dump(dependency_tree, json_file, indent=2)


yarn_lock_path = "yarn.lock"
output_json_path = "dependencies.json"

dependencies = parse_yarn_lock(yarn_lock_path)
generate_dependencies_json(dependencies, output_json_path)

print(f"Generated dependencies.json at {output_json_path}")
