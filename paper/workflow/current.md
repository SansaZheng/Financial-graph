# Current research stage

003-ntd | Codex + CQ | 2026-11-25

Completed: legacy CGI (negative vs strong control), three modern RG-ResMoE/MLP seeds (verified), NTD Kaggle smoke, ten-test qualification.
Active: j-1125-0c3a7c, unchanged NTD three-seed batch on c225 in the already-qualified project environment. See jobs/20261125-portable-batch/batch.json.
Superseded Kaggle batch j-1125-a08289 cancelled before launch after waiting for shared capacity. New isolated lab environment had slow imports; that smoke is cancelled. Existing portable environment passed ten tests in4.56seconds and is used read-only.
Environment difference: portable NumPy1.26.4/scikit-learn1.5.2/SciPy1.14.1 versus Kaggle NumPy2.2.6/scikit-learn1.6.1/SciPy1.15.3. Within NTD all controls run in the same environment. Cross-family modern comparisons additionally differ in software versions. No scientific source/hyperparameter changes.
Next: fetch batch, verify predictions and hashes, compare all controls, archive final report ending in Chinese.
All historical years are development-only. Missing iCloud investigation discontinued. No rental, paid CU or source deletion.
