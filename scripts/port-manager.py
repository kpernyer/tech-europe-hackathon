#!/usr/bin/env python3
"""
Port Manager - Centralized port configuration management
Generates Docker Compose configurations and Makefile variables from ports.yaml
"""

import yaml
import sys
import os
from pathlib import Path

def load_port_config():
    """Load the centralized port configuration"""
    config_path = Path(__file__).parent.parent / "ports.yaml"
    try:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Error: {config_path} not found", file=sys.stderr)
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"Error parsing YAML: {e}", file=sys.stderr)
        sys.exit(1)

def get_project_ports(project_name):
    """Get port configuration for a specific project"""
    config = load_port_config()
    if project_name not in config['projects']:
        print(f"Error: Project '{project_name}' not found in configuration", file=sys.stderr)
        sys.exit(1)
    return config['projects'][project_name]

def generate_docker_compose_ports(project_name):
    """Generate Docker Compose port mapping for a project"""
    project_config = get_project_ports(project_name)
    docker_ports = project_config.get('docker_ports', {})

    port_mappings = []
    for service, mapping in docker_ports.items():
        port_mappings.append(f"      - \"{mapping}\"")

    return "\n".join(port_mappings)

def generate_makefile_vars(project_name):
    """Generate Makefile variables for a project"""
    project_config = get_project_ports(project_name)
    ports = project_config.get('ports', {})

    makefile_vars = []
    for service, port in ports.items():
        var_name = f"{service.upper()}_PORT"
        makefile_vars.append(f"{var_name} = {port}")

    return "\n".join(makefile_vars)

def list_all_ports():
    """List all configured ports"""
    config = load_port_config()

    print("Tech Europe Hackathon - Port Allocation")
    print("=" * 50)

    for project_name, project_config in config['projects'].items():
        print(f"\n{project_config['name']} ({project_name}):")
        ports = project_config.get('ports', {})
        for service, port in ports.items():
            print(f"  {service:15} -> {port}")

def check_port_conflicts():
    """Check for port conflicts across projects"""
    config = load_port_config()
    used_ports = {}
    conflicts = []

    for project_name, project_config in config['projects'].items():
        ports = project_config.get('ports', {})
        for service, port in ports.items():
            port_key = f"{project_name}.{service}"
            if port in used_ports:
                conflicts.append(f"Port {port}: {used_ports[port]} and {port_key}")
            else:
                used_ports[port] = port_key

    if conflicts:
        print("Port Conflicts Detected:")
        for conflict in conflicts:
            print(f"  ⚠️  {conflict}")
        return False
    else:
        print("✅ No port conflicts detected")
        return True

def get_health_check_url(project_name):
    """Get health check URL for a project"""
    config = load_port_config()
    return config['health_checks'].get(project_name, f"http://localhost:8000")

def main():
    if len(sys.argv) < 2:
        print("Usage: port-manager.py <command> [project_name]")
        print("Commands:")
        print("  list                    - List all port allocations")
        print("  check                   - Check for port conflicts")
        print("  docker-ports <project>  - Generate Docker Compose port mappings")
        print("  makefile-vars <project> - Generate Makefile variables")
        print("  health-url <project>    - Get health check URL")
        sys.exit(1)

    command = sys.argv[1]

    if command == "list":
        list_all_ports()
    elif command == "check":
        check_port_conflicts()
    elif command == "docker-ports":
        if len(sys.argv) < 3:
            print("Error: Project name required", file=sys.stderr)
            sys.exit(1)
        print(generate_docker_compose_ports(sys.argv[2]))
    elif command == "makefile-vars":
        if len(sys.argv) < 3:
            print("Error: Project name required", file=sys.stderr)
            sys.exit(1)
        print(generate_makefile_vars(sys.argv[2]))
    elif command == "health-url":
        if len(sys.argv) < 3:
            print("Error: Project name required", file=sys.stderr)
            sys.exit(1)
        print(get_health_check_url(sys.argv[2]))
    else:
        print(f"Error: Unknown command '{command}'", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()