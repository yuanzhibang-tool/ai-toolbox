# !/bin/bash
cp README.md code/README.md
cd code
flit install
version=`dev-version --section=patch --toml_path=pyproject.toml`
dev-release --version=$version
flit build
rm -rf code/README.md
flit publish    # This will ask for username and password
