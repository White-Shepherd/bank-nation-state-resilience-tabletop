# Streamlit telemetry-directory warning

## Captured warning

Local verification originally emitted `PermissionError: [WinError 5] Access is denied: 'C:\Users\baile\.streamlit'` from Streamlit's `metrics_util._get_machine_id_v4()` while it attempted to create an installation identifier.

## Diagnosis

The affected path is Streamlit's per-user configuration and anonymous usage-telemetry directory. It is not `data/private_assessments/`, assessment version history, Streamlit session state, or an export directory. The application continued to load and assessment/report tests passed, so no assessment data or exports were lost.

## Correction

Repository-local `.streamlit/config.toml` sets the supported `browser.gatherUsageStats = false` option. This prevents the telemetry installation-ID write without changing permissions on the user profile or weakening filesystem controls. `server.headless = true` also makes local and CI startup deterministic.

If a future Streamlit release writes other per-user configuration despite telemetry being disabled, set `STREAMLIT_CONFIG_DIR` to a writable, narrowly scoped application directory before startup. Do not grant broad write access to the user profile.
