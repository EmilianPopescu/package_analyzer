import json
import csv
import requests

# Load the JSON file
with open("dependencies.json", "r") as file:
    data = json.load(file)

# Extract dependencies (name and version)
dependencies = []
for tree in data.get("data", {}).get("trees", []):
    if "@" in tree["name"]:  # Ensure format is name@version
        dependencies.append(tree["name"])

# Function to fetch the latest version from npm registry
def fetch_latest_version(package_name):
    try:
        # Extract name without version
        name = package_name.split("@")[0]
        response = requests.get(f"https://registry.npmjs.org/{name}")
        if response.status_code == 200:
            package_data = response.json()
            return package_data.get("dist-tags", {}).get("latest", "Unknown")
    except Exception as e:
        print(f"Error fetching latest version for {package_name}: {e}")
    return "Unknown"

# Function to check for security issues
def check_security_issues(package_name):
    try:
        name = package_name.split("@")[0]
        response = requests.post(
            "https://registry.npmjs.org/-/npm/v1/security/advisories/bulk",
            json={"name": name},
        )
        if response.status_code == 200:
            advisories = response.json().get("advisories", [])
            return "Yes" if advisories else "No"
    except Exception as e:
        print(f"Error checking security issues for {package_name}: {e}")
    return "No"

# Analyze dependencies
analysis_results = []
for dep in dependencies:
    try:
        name, version = dep.rsplit("@", 1)
    except ValueError:
        name, version = dep, "Unknown"
    latest_version = fetch_latest_version(name)
    security_issues = check_security_issues(name)
    analysis_results.append({
        "name": name,
        "current_version": version,
        "latest_version": latest_version,
        "security_issues": security_issues,
    })

# Save results to a CSV file
output_file = "dependency_analysis.csv"
with open(output_file, "w", newline="") as csvfile:
    fieldnames = ["name", "current_version", "latest_version", "security_issues"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(analysis_results)

print(f"Analysis complete. Results saved to {output_file}")
