# Malaysia State Random Forest Continuity Benchmark

Purpose: document the Random Forest benchmark and the deterministic state-level selection decision.

Continuity facts:

- Part 1 proposed Random Forest as the Semester 2 non-parametric modelling direction.
- No retained executable old Random Forest modelling script is present in the final package.
- Random Forest has therefore been reimplemented as a Malaysia state-level benchmark in `notebooks/03_model_training_evaluation.ipynb` inside this notebook.
- Scope is state-level only. Only Malaysia state-level modelling forms part of the active project.
- The primary model is selected by an encoded rule restricted to sensor-safe features; no manual override is used.

Promotion status:

- Selected absolute-poverty point predictor: `rf_sensor_safe`.
- Best observed absolute-poverty model in this run: `rf_sensor_safe`.
- Selection status: `not_applicable_deterministic_rule`.
- RF is not claimed as decisively superior because the paired MAE uncertainty interval overlaps zero.
- Relative poverty is best handled as year/trend-driven because the year-only baseline has the strongest state-level metrics.

RF and state headline benchmark comparison:

| target | model | feature_policy | feature_count | loso_mae_pp | loso_rmse | loso_r2 | loso_spearman |
| --- | --- | --- | --- | --- | --- | --- | --- |
| poverty_absolute | rf_sensor_safe | sensor_safe | 11 | 2.4425 | 4.3923 | 0.2759 | 0.7945 |
| poverty_absolute | rf_current_full | current_full | 20 | 2.5122 | 4.5445 | 0.2248 | 0.7886 |
| poverty_absolute | current_xgb | current_full | 20 | 2.5372 | 4.6639 | 0.1835 | 0.8102 |
| poverty_absolute | year_only_xgb | year_only | 1 | 2.9609 | 4.8456 | 0.1187 | 0.4910 |
| poverty_relative | year_only_xgb | year_only | 1 | 2.2364 | 2.8891 | 0.2472 | 0.4313 |
| poverty_relative | current_xgb | current_full | 20 | 2.5228 | 3.2736 | 0.0335 | 0.4271 |
| poverty_relative | rf_current_full | current_full | 20 | 2.6302 | 3.4041 | -0.0451 | 0.3654 |
| poverty_relative | rf_sensor_safe | sensor_safe | 11 | 2.6314 | 3.4699 | -0.0859 | 0.3445 |

RF uncertainty intervals:

| target | model | metric | observed | ci_lower | ci_upper | n_boot | n_groups |
| --- | --- | --- | --- | --- | --- | --- | --- |
| poverty_absolute | rf_current_full | mae | 2.5122 | 1.4002 | 3.9719 | 2000 | 16 |
| poverty_absolute | rf_current_full | pearson | 0.5147 | 0.3082 | 0.8317 | 2000 | 16 |
| poverty_absolute | rf_current_full | r2 | 0.2248 | -0.0703 | 0.6287 | 2000 | 16 |
| poverty_absolute | rf_current_full | rmse | 4.5445 | 2.1906 | 6.7400 | 2000 | 16 |
| poverty_absolute | rf_current_full | spearman | 0.7886 | 0.6791 | 0.8671 | 2000 | 16 |
| poverty_absolute | rf_sensor_safe | mae | 2.4425 | 1.3368 | 3.8472 | 2000 | 16 |
| poverty_absolute | rf_sensor_safe | pearson | 0.5559 | 0.3652 | 0.8492 | 2000 | 16 |
| poverty_absolute | rf_sensor_safe | r2 | 0.2759 | -0.0655 | 0.6601 | 2000 | 16 |
| poverty_absolute | rf_sensor_safe | rmse | 4.3923 | 2.1347 | 6.4130 | 2000 | 16 |
| poverty_absolute | rf_sensor_safe | spearman | 0.7945 | 0.6849 | 0.8761 | 2000 | 16 |
| poverty_relative | rf_current_full | mae | 2.6302 | 2.1150 | 3.2529 | 2000 | 16 |
| poverty_relative | rf_current_full | pearson | 0.3296 | 0.1844 | 0.4955 | 2000 | 16 |
| poverty_relative | rf_current_full | r2 | -0.0451 | -0.4173 | 0.2002 | 2000 | 16 |
| poverty_relative | rf_current_full | rmse | 3.4041 | 2.7574 | 4.0523 | 2000 | 16 |
| poverty_relative | rf_current_full | spearman | 0.3654 | 0.2139 | 0.5328 | 2000 | 16 |
| poverty_relative | rf_sensor_safe | mae | 2.6314 | 2.0741 | 3.3181 | 2000 | 16 |
| poverty_relative | rf_sensor_safe | pearson | 0.3090 | 0.1611 | 0.4924 | 2000 | 16 |
| poverty_relative | rf_sensor_safe | r2 | -0.0859 | -0.5055 | 0.1897 | 2000 | 16 |
| poverty_relative | rf_sensor_safe | rmse | 3.4699 | 2.7734 | 4.1777 | 2000 | 16 |
| poverty_relative | rf_sensor_safe | spearman | 0.3445 | 0.1937 | 0.5340 | 2000 | 16 |
