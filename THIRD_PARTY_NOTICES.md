# Third-party notices

NetChange Guard depends on third-party open-source software installed from its original package or
container registries. No third-party source code is copied into this repository.

| Component | Purpose | License | Project |
|---|---|---|---|
| Batfish / PyBatfish | Network configuration and reachability analysis | Apache License 2.0 | https://github.com/batfish/batfish |
| PyYAML | Safe YAML decoding | MIT | https://github.com/yaml/pyyaml |

Development-only tools and their transitive dependencies are declared in `pyproject.toml` and retain
their respective licenses. The authoritative license text for each installed package is distributed
with that package. Container images are pulled by digest but remain external third-party artifacts.
