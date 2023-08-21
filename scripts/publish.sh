# !/bin/bash
cd code
flit install
version=`dev-version --section=patch --toml_path=pyproject.toml`
dev-release --version=$version
flit build
flit publish    # This will ask for username and password