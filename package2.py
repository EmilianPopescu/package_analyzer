import json
import csv
import requests
import time


with open("dependencies.json", "r") as file:
    data = json.load(file)


dependencies = []
for tree in data.get("data", {}).get("trees", []):
    if "@" in tree["name"]:  # Ensure format is name@version
        dependencies.append(tree["name"])


def fetch_latest_version(package_name):
    try:
        response = requests.get(f"https://registry.npmjs.org/{package_name}", timeout=10)
        if response.status_code == 200:
            package_data = response.json()
            return package_data.get("dist-tags", {}).get("latest", "Unknown")
        else:
            print(f"Failed to fetch {package_name}: HTTP {response.status_code}")
    except Exception as e:
        print(f"Error fetching latest version for {package_name}: {e}")
    return "Unknown"


def check_security_issues_bulk(package_list):
    try:
        payload = [{"name": name, "version": version} for name, version in package_list]

        response = requests.post(
            "https://registry.npmjs.org/-/npm/v1/security/advisories/bulk",
            json=payload,
            timeout=10
        )
        if response.status_code == 200:
            advisories = response.json()
            return {item["name"]: "Yes" if item.get("advisories") else "No" for item in advisories.values()}
        else:
            print(f"Failed to fetch security advisories: HTTP {response.status_code}")
            print(f"Payload: {payload}")
    except Exception as e:
        print(f"Error checking security issues: {e}")
    return {name: "Unknown" for name, _ in package_list}

analysis_results = []
bulk_packages = []
for dep in dependencies:
    try:
        if dep.startswith("@"):
            name_version = dep.split("@", 1)
        else:
            name_version = dep.rsplit("@", 1)
        name, version = name_version[0], name_version[1]
        bulk_packages.append((name, version))
    except ValueError:
        bulk_packages.append((dep, "Unknown"))


security_issues = check_security_issues_bulk(bulk_packages)

for name, version in bulk_packages:
    latest_version = fetch_latest_version(name)
    security_status = security_issues.get(name, "Unknown")
    analysis_results.append({
        "name": name,
        "current_version": version,
        "latest_version": latest_version,
        "security_issues": security_status,
    })
    time.sleep(0.5)


output_file = "dependency_analysis.csv"
with open(output_file, "w", newline="") as csvfile:
    fieldnames = ["name", "current_version", "latest_version", "security_issues"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(analysis_results)

print(f"Analysis complete. Results saved to {output_file}")
