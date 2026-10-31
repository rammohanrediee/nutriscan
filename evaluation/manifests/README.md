# Benchmark manifests

`public.csv` identifies the retained 75-example public diagnostic: the first five streamed test
examples for each class, sorted by class when written. It reports narrow single-dish top-1
accuracy but does not participate in the model-selection gate. Images are regenerated into the
ignored `artifacts/public/images/` directory from the pinned dataset revision recorded in
`nutriscan_eval.dataset`. The loader accepts this legacy diagnostic manifest without a
`benchmark_category`; newly generated manifests label rows `public_diagnostic`.

Private labels must never be stored here. Keep them only at the ignored `private/labels.csv` path.

