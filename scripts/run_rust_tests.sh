#!/usr/bin/env bash
set -euo pipefail

cargo check --workspace
cargo fmt --check --all
cargo test --workspace
cargo clippy --workspace --all-targets -- -D warnings
