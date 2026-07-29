Stop `--suffix` environments from losing track of the packages injected into them. Reading `pipx_metadata.json` appended
the suffix to each injected package's key, so `inject` reported the suffix twice, `list` repeated it once more for every
command that rewrote the file, `reinstall` and `upgrade --include-injected` failed with an internal error naming a
distribution the environment does not contain, `upgrade-all --include-injected` skipped the injection silently, and
`uninject` matched neither the recorded name nor the one pipx displays. Such an environment is re-keyed the first time
this version reads it, and `reinstall` now keeps the suffix a package was injected with.
