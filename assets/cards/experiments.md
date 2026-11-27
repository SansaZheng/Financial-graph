# Selected experimental evidence

Completed NTD seeds471/472/473, modern adapted baselines seeds471/472/473,
and the legacy CGI full run. Retain all selected primary results, including
negative results. Each run includes original metrics/predictions, configuration
selection, dependency freeze and code revision when produced. No trained model
checkpoint was emitted by these evaluation pipelines. Model repositories should
be created only after actual best/final/recovery checkpoints are selected.

The pinned code revision in each run is the training code; the current asset
migration commit is a separate infrastructure revision. See the GitHub manifest
for required paths, byte sizes and full SHA256. Model-input/feature CSVs are
retained for timing audits. Logs, package installation output and repeated smoke
outputs are excluded from this curated upload; local originals are not deleted.
